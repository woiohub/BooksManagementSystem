from datetime import date
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Category(db.Model):
    __tablename__ = 'Category'

    cat_id = db.Column(db.String(10), primary_key=True)
    cat_name = db.Column(db.String(50), nullable=False)
    location = db.Column(db.String(100))
    remark = db.Column(db.String(200))

    books = db.relationship('Book', backref='category', lazy='dynamic')


class Book(db.Model):
    __tablename__ = 'Book'

    book_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    isbn = db.Column(db.String(20), unique=True, nullable=False)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(100))
    publisher = db.Column(db.String(100))
    pub_year = db.Column(db.Integer)
    cat_id = db.Column(db.String(10), db.ForeignKey('Category.cat_id'), nullable=False)
    total_stock = db.Column(db.Integer, nullable=False)
    available_stock = db.Column(db.Integer, nullable=False)
    shelf_location = db.Column(db.String(50))

    borrow_records = db.relationship('BorrowRecord', backref='book', lazy='dynamic')


class User(db.Model):
    __tablename__ = 'User'

    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(50), nullable=False)
    user_type = db.Column(db.String(20), nullable=False)
    max_borrow = db.Column(db.Integer, nullable=False)
    days_limit = db.Column(db.Integer, nullable=False)
    penalty_per_day = db.Column(db.Numeric(10, 2), nullable=False)
    borrowed_count = db.Column(db.Integer, default=0)
    penalty_total = db.Column(db.Numeric(10, 2), default=0)

    borrow_records = db.relationship('BorrowRecord', backref='user', lazy='dynamic')

    @property
    def can_borrow(self):
        return self.borrowed_count < self.max_borrow


class BorrowRecord(db.Model):
    __tablename__ = 'BorrowRecord'

    record_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    book_id = db.Column(db.Integer, db.ForeignKey('Book.book_id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('User.user_id'), nullable=False)
    borrow_date = db.Column(db.Date, nullable=False)
    due_date = db.Column(db.Date, nullable=False)
    return_date = db.Column(db.Date, nullable=True)
    penalty = db.Column(db.Numeric(10, 2), default=0)
    status = db.Column(db.SmallInteger, default=0)

    @property
    def is_overdue(self):
        if self.status == 1:
            return False
        return date.today() > self.due_date


class Admin(db.Model):
    __tablename__ = 'Admin'

    admin_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(30), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)