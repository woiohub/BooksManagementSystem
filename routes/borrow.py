from flask import Blueprint, render_template, request, redirect, url_for
from services.borrow_service import BorrowService
from models import db, Book, User, BorrowRecord

borrow_bp = Blueprint('borrow', __name__)


@borrow_bp.route('/')
def borrow_page():
    return render_template('borrow/borrow.html')


@borrow_bp.route('/do_borrow', methods=['POST'])
def do_borrow():
    user_id = request.form.get('user_id', '').strip()
    book_id = request.form.get('book_id', '').strip()

    if not user_id or not book_id:
        return render_template('borrow/borrow.html', error='请输入用户ID和图书ID')

    success, msg = BorrowService.borrow_book(int(user_id), int(book_id))
    if success:
        return render_template('borrow/borrow.html', success=msg)
    return render_template('borrow/borrow.html', error=msg)


@borrow_bp.route('/return_page')
def return_page():
    return render_template('borrow/return.html')


@borrow_bp.route('/do_return', methods=['POST'])
def do_return():
    record_id = request.form.get('record_id', '').strip()
    if not record_id:
        return render_template('borrow/return.html', error='请输入借阅记录ID')

    success, msg = BorrowService.return_book(int(record_id))
    if success:
        return render_template('borrow/return.html', success=msg)
    return render_template('borrow/return.html', error=msg)


@borrow_bp.route('/records')
def records():
    user_id = request.args.get('user_id', '').strip()
    status = request.args.get('status', '')
    q = BorrowRecord.query
    if user_id:
        q = q.filter_by(user_id=int(user_id))
    if status != '':
        q = q.filter_by(status=int(status))
    records = q.order_by(BorrowRecord.borrow_date.desc()).all()
    return render_template('borrow/records.html', records=records,
                           user_id=user_id, status=status)


@borrow_bp.route('/overdue')
def overdue():
    records = BorrowService.get_overdue_records()
    return render_template('borrow/overdue.html', records=records)


@borrow_bp.route('/quick_search')
def quick_search():
    q = request.args.get('q', '').strip()
    books = []
    users = []
    if q:
        if q.isdigit():
            books = Book.query.filter_by(book_id=int(q)).all()
            users = User.query.filter_by(user_id=int(q)).all()
        books += Book.query.filter(
            Book.title.contains(q) | Book.isbn.contains(q)
        ).all()
        users += User.query.filter(User.name.contains(q)).all()

    return render_template('borrow/quick_search.html', books=books, users=users, q=q)