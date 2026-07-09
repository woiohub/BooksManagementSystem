from flask import Blueprint, render_template, request, redirect, url_for, session
from services.borrow_service import BorrowService
from models import db, Book, User, BorrowRecord
from utils.decorators import user_required

borrow_bp = Blueprint('borrow', __name__)


@borrow_bp.route('/')
@user_required
def borrow_page():
    user = db.session.get(User, session.get('user_id'))
    return render_template('borrow/borrow.html', user=user)


@borrow_bp.route('/do_borrow', methods=['POST'])
@user_required
def do_borrow():
    user_id = session.get('user_id')
    book_id = request.form.get('book_id', '').strip()

    if not book_id:
        user = db.session.get(User, user_id)
        return render_template('borrow/borrow.html', error='请输入图书ID', user=user)

    success, msg = BorrowService.borrow_book(int(user_id), int(book_id))
    user = db.session.get(User, user_id)
    if success:
        return render_template('borrow/borrow.html', success=msg, user=user)
    return render_template('borrow/borrow.html', error=msg, user=user)


@borrow_bp.route('/return_page')
@user_required
def return_page():
    user_id = session.get('user_id')
    # 查询当前用户的所有借阅记录，按记录ID升序
    records = BorrowRecord.query.filter_by(user_id=user_id).order_by(BorrowRecord.record_id.asc()).all()
    return render_template('borrow/return.html', records=records)


@borrow_bp.route('/do_return', methods=['POST'])
@user_required
def do_return():
    record_id = request.form.get('record_id', '').strip()
    if not record_id:
        user_id = session.get('user_id')
        records = BorrowRecord.query.filter_by(user_id=user_id).order_by(BorrowRecord.record_id.asc()).all()
        return render_template('borrow/return.html', error='请输入借阅记录ID', records=records)

    success, msg = BorrowService.return_book(int(record_id))
    user_id = session.get('user_id')
    records = BorrowRecord.query.filter_by(user_id=user_id).order_by(BorrowRecord.record_id.asc()).all()
    if success:
        return render_template('borrow/return.html', success=msg, records=records)
    return render_template('borrow/return.html', error=msg, records=records)


@borrow_bp.route('/records')
@user_required
def records():
    user_id = request.args.get('user_id', '').strip()
    status = request.args.get('status', '')
    q = BorrowRecord.query
    if user_id:
        q = q.filter_by(user_id=int(user_id))
    if status != '':
        q = q.filter_by(status=int(status))
    records = q.order_by(BorrowRecord.record_id.asc()).all()
    return render_template('borrow/records.html', records=records,
                           user_id=user_id, status=status)


@borrow_bp.route('/overdue')
@user_required
def overdue():
    records = BorrowService.get_overdue_records()
    return render_template('borrow/overdue.html', records=records)


@borrow_bp.route('/quick_search')
@user_required
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