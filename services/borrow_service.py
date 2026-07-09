from datetime import date, timedelta
from models import db, Book, User, BorrowRecord


class BorrowService:

    @staticmethod
    def borrow_book(user_id, book_id):
        """借阅图书业务逻辑"""
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

        # 更新库存和借阅计数
        book.available_stock -= 1
        user.borrowed_count += 1

        db.session.add(record)
        db.session.commit()

        return True, f'借阅成功！应还日期：{due_date.strftime("%Y-%m-%d")}'

    @staticmethod
    def return_book(record_id):
        """归还图书业务逻辑"""
        # 校验记录
        record = db.session.get(BorrowRecord, record_id)
        if not record:
            return False, '归还失败：借阅记录不存在'

        if record.status == 1:
            return False, '归还失败：该图书已归还'

        # 计算归还日期和违约金
        return_date = date.today()
        penalty = 0.0
        overdue_days = 0

        if return_date > record.due_date:
            user = db.session.get(User, record.user_id)
            overdue_days = (return_date - record.due_date).days
            penalty = overdue_days * float(user.penalty_per_day)
            user.penalty_total = float(user.penalty_total) + penalty

        # 更新记录状态
        record.return_date = return_date
        record.status = 1
        record.penalty = penalty

        # 更新库存和借阅计数
        book = db.session.get(Book, record.book_id)
        book.available_stock += 1

        user = db.session.get(User, record.user_id)
        user.borrowed_count -= 1

        db.session.commit()

        # 返回结果
        if penalty > 0:
            return True, f'归还成功！超期{overdue_days}天，违约金{penalty:.2f}元'
        else:
            return True, '归还成功！'

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
        """获取超期记录"""
        today = date.today()
        return BorrowRecord.query.filter(
            BorrowRecord.status == 0,
            BorrowRecord.due_date < today
        ).order_by(BorrowRecord.record_id.asc()).all()