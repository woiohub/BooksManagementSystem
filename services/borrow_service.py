from datetime import date, timedelta
from models import db, Book, User, BorrowRecord


class BorrowService:

    @staticmethod
    def borrow_book(user_id, book_id):
        user = db.session.get(User, user_id)
        if not user:
            return False, '用户不存在'

        book = db.session.get(Book, book_id)
        if not book:
            return False, '图书不存在'

        if not user.can_borrow:
            return False, f'借阅已达上限（最多{user.max_borrow}本），请先归还后再借'

        if book.available_stock <= 0:
            return False, '该图书已全部借出，暂无库存'

        borrow_date = date.today()
        due_date = borrow_date + timedelta(days=user.days_limit)

        record = BorrowRecord(
            book_id=book_id,
            user_id=user_id,
            borrow_date=borrow_date,
            due_date=due_date,
            status=0
        )

        book.available_stock -= 1
        user.borrowed_count += 1

        db.session.add(record)
        db.session.commit()
        return True, f'借阅成功！应还日期：{due_date}'

    @staticmethod
    def return_book(record_id):
        record = db.session.get(BorrowRecord, record_id)
        if not record:
            return False, '借阅记录不存在'

        if record.status == 1:
            return False, '该图书记归还'

        return_date = date.today()
        penalty = 0.0

        if return_date > record.due_date:
            user = db.session.get(User, record.user_id)
            overdue_days = (return_date - record.due_date).days
            penalty = overdue_days * float(user.penalty_per_day)
            user.penalty_total = float(user.penalty_total) + penalty

        record.return_date = return_date
        record.status = 1
        record.penalty = penalty

        book = db.session.get(Book, record.book_id)
        book.available_stock += 1

        user = db.session.get(User, record.user_id)
        user.borrowed_count -= 1

        db.session.commit()
        msg = '归还成功'
        if penalty > 0:
            msg += f'，超期{(return_date - record.due_date).days}天，违约金{penalty:.2f}元'
        return True, msg

    @staticmethod
    def get_active_records(user_id=None):
        q = BorrowRecord.query.filter_by(status=0)
        if user_id:
            q = q.filter_by(user_id=user_id)
        return q.order_by(BorrowRecord.borrow_date.desc()).all()

    @staticmethod
    def get_all_records(user_id=None):
        q = BorrowRecord.query
        if user_id:
            q = q.filter_by(user_id=user_id)
        return q.order_by(BorrowRecord.borrow_date.desc()).all()

    @staticmethod
    def get_overdue_records():
        today = date.today()
        return BorrowRecord.query.filter(
            BorrowRecord.status == 0,
            BorrowRecord.due_date < today
        ).order_by(BorrowRecord.due_date).all()