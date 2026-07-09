import logging
from datetime import date, timedelta
from models import db, Book, User, BorrowRecord

logger = logging.getLogger(__name__)


class BorrowService:

    @staticmethod
    def borrow_book(user_id, book_id):
        """借阅图书业务逻辑

        Args:
            user_id: 用户ID（正整数）
            book_id: 图书ID（正整数）

        Returns:
            tuple: (success: bool, message: str)
        """
        # 校验用户
        user = db.session.get(User, user_id)
        if not user:
            return False, '借阅失败：用户不存在'

        # 校验图书
        book = db.session.get(Book, book_id)
        if not book:
            return False, '借阅失败：图书不存在'

        # 校验可借数量
        if not user.can_borrow:
            return False, f'借阅失败：您已达到最大可借数量（{user.max_borrow}本），请先归还后再借'

        # 校验库存
        if book.available_stock <= 0:
            return False, '借阅失败：该图书已全部借出，暂无库存'

        # 执行借阅
        borrow_date = date.today()
        due_date = borrow_date + timedelta(days=user.days_limit)

        record = BorrowRecord(
            book_id=book_id,
            user_id=user_id,
            borrow_date=borrow_date,
            due_date=due_date,
            status=0
        )

        # 由触发器 trg_BorrowRecord_Sync 自动更新 book.available_stock 和 user.borrowed_count
        try:
            db.session.add(record)
            db.session.commit()

            # 刷新对象以获取触发器更新后的最新值
            db.session.refresh(book)
            db.session.refresh(user)

            return True, f'借阅成功！应还日期：{due_date.strftime("%Y-%m-%d")}'
        except Exception:
            db.session.rollback()
            logger.exception('借阅图书数据库异常: user_id=%s, book_id=%s', user_id, book_id)
            return False, '借阅失败：数据库操作异常，请稍后重试'

    @staticmethod
    def return_book(record_id):
        """归还图书业务逻辑

        Args:
            record_id: 借阅记录ID（正整数）

        Returns:
            tuple: (success: bool, message: str)
        """
        # 校验记录
        record = db.session.get(BorrowRecord, record_id)
        if not record:
            return False, '归还失败：借阅记录不存在'

        if record.status == 1:
            return False, '归还失败：该图书已归还'

        # 计算归还日期和超期天数（仅用于前端展示，违约金由触发器自动计算）
        return_date = date.today()
        overdue_days = 0

        if return_date > record.due_date:
            overdue_days = (return_date - record.due_date).days

        # 更新记录状态（违约金由触发器自动计算并写入 penalty 字段）
        record.return_date = return_date
        record.status = 1

        # 由触发器 trg_BorrowRecord_Sync 自动更新：
        # - book.available_stock +1
        # - user.borrowed_count -1
        # - 若超期，自动计算违约金并更新 BorrowRecord.penalty 和 User.penalty_total
        try:
            db.session.commit()

            # 刷新记录以获取触发器更新后的违约金等最新值
            db.session.refresh(record)

            # 从触发器更新后的记录中获取违约金
            penalty = float(record.penalty or 0)

            # 返回结果
            if overdue_days > 0:
                return True, f'归还成功！超期{overdue_days}天，违约金{penalty:.2f}元'
            else:
                return True, '归还成功！'
        except Exception:
            db.session.rollback()
            logger.exception('归还图书数据库异常: record_id=%s', record_id)
            return False, '归还失败：数据库操作异常，请稍后重试'

    @staticmethod
    def get_active_records(user_id=None):
        """获取未归还记录"""
        q = BorrowRecord.query.filter_by(status=0)
        if user_id:
            q = q.filter_by(user_id=user_id)
        return q.order_by(BorrowRecord.record_id.asc()).all()

    @staticmethod
    def get_all_records(user_id=None):
        """获取所有记录"""
        q = BorrowRecord.query
        if user_id:
            q = q.filter_by(user_id=user_id)
        return q.order_by(BorrowRecord.record_id.asc()).all()

    @staticmethod
    def get_overdue_records():
        """获取超期记录（状态为借阅中且已超过应还日期）"""
        today = date.today()
        return BorrowRecord.query.filter(
            BorrowRecord.status == 0,
            BorrowRecord.due_date < today
        ).order_by(BorrowRecord.record_id.asc()).all()
