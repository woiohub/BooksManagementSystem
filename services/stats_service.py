from datetime import date
from models import db, Book, User, BorrowRecord, Category
from sqlalchemy import func


class StatsService:

    @staticmethod
    def get_book_heat_ranking(top_n=10, start_date=None, end_date=None):
        q = db.session.query(
            Book.book_id, Book.title, Book.author,
            func.count(BorrowRecord.record_id).label('borrow_count')
        ).join(BorrowRecord, Book.book_id == BorrowRecord.book_id)

        if start_date:
            q = q.filter(BorrowRecord.borrow_date >= start_date)
        if end_date:
            q = q.filter(BorrowRecord.borrow_date <= end_date)

        return q.group_by(Book.book_id, Book.title, Book.author).order_by(
            func.count(BorrowRecord.record_id).desc()
        ).limit(top_n).all()

    @staticmethod
    def get_category_heat_ranking():
        return db.session.query(
            Category.cat_id, Category.cat_name,
            func.count(BorrowRecord.record_id).label('borrow_count')
        ).join(Book, Category.cat_id == Book.cat_id).join(
            BorrowRecord, Book.book_id == BorrowRecord.book_id
        ).group_by(Category.cat_id, Category.cat_name).order_by(
            func.count(BorrowRecord.record_id).desc()
        ).all()

    @staticmethod
    def get_user_borrow_ranking(top_n=10):
        return db.session.query(
            User.user_id, User.name, User.user_type,
            func.count(BorrowRecord.record_id).label('borrow_count')
        ).join(BorrowRecord, User.user_id == BorrowRecord.user_id).group_by(
            User.user_id, User.name, User.user_type
        ).order_by(func.count(BorrowRecord.record_id).desc()).limit(top_n).all()

    @staticmethod
    def get_overview_stats():
        total_books = Book.query.count()
        total_users = User.query.count()
        active_borrows = BorrowRecord.query.filter_by(status=0).count()
        total_borrows = BorrowRecord.query.count()
        total_penalty = db.session.query(
            func.sum(BorrowRecord.penalty)
        ).scalar() or 0
        overdue_count = BorrowRecord.query.filter(
            BorrowRecord.status == 0,
            BorrowRecord.due_date < date.today()
        ).count()

        return {
            'total_books': total_books,
            'total_users': total_users,
            'active_borrows': active_borrows,
            'total_borrows': total_borrows,
            'total_penalty': float(total_penalty),
            'overdue_count': overdue_count,
        }