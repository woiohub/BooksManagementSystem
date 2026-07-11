from datetime import date
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Category(db.Model):
    """图书分类模型"""
    __tablename__ = 'Category'

    cat_id = db.Column(db.String(10), primary_key=True)
    cat_name = db.Column(db.String(50), nullable=False, unique=True)
    location = db.Column(db.String(100))
    remark = db.Column(db.String(200))

    books = db.relationship('Book', backref='category', lazy='dynamic')


class Book(db.Model):
    """图书模型"""
    __tablename__ = 'Book'

    book_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    isbn = db.Column(db.String(20), unique=True, nullable=False, index=True)
    title = db.Column(db.String(200), nullable=False, index=True)
    author = db.Column(db.String(100), index=True)
    publisher = db.Column(db.String(100))
    pub_year = db.Column(db.Integer)
    cat_id = db.Column(db.String(10), db.ForeignKey('Category.cat_id'), nullable=False)
    total_stock = db.Column(db.Integer, nullable=False)
    available_stock = db.Column(db.Integer, nullable=False)
    shelf_location = db.Column(db.String(50))

    borrow_records = db.relationship('BorrowRecord', backref='book', lazy='dynamic')

    def __repr__(self):
        return f'<Book {self.title}>'


class User(db.Model):
    """用户模型"""
    __tablename__ = 'User'

    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(128), nullable=False)
    user_type = db.Column(db.String(20), nullable=False)
    max_borrow = db.Column(db.Integer, nullable=False)
    days_limit = db.Column(db.Integer, nullable=False)
    penalty_per_day = db.Column(db.Numeric(10, 2), nullable=False)
    borrowed_count = db.Column(db.Integer, default=0)
    penalty_total = db.Column(db.Numeric(10, 2), default=0)

    borrow_records = db.relationship('BorrowRecord', backref='user', lazy='dynamic')

    @property
    def can_borrow(self):
        """判断用户是否还能借阅图书"""
        return self.borrowed_count < self.max_borrow

    def __repr__(self):
        return f'<User {self.name}>'


class BorrowRecord(db.Model):
    """借阅记录模型"""
    __tablename__ = 'BorrowRecord'
    __table_args__ = {'implicit_returning': False}

    record_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    book_id = db.Column(db.Integer, db.ForeignKey('Book.book_id'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('User.user_id'), nullable=False, index=True)
    borrow_date = db.Column(db.Date, nullable=False)
    due_date = db.Column(db.Date, nullable=False)
    return_date = db.Column(db.Date, nullable=True)
    penalty = db.Column(db.Numeric(10, 2), default=0)
    status = db.Column(db.SmallInteger, default=0, index=True)  # 0=借阅中, 1=已归还

    @property
    def is_overdue(self):
        """判断该借阅记录是否已超期"""
        if self.status == 1:
            return False
        return date.today() > self.due_date

    def __repr__(self):
        return f'<BorrowRecord book={self.book_id} user={self.user_id} status={self.status}>'


class Admin(db.Model):
    """管理员模型"""
    __tablename__ = 'Admin'

    admin_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(30), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
