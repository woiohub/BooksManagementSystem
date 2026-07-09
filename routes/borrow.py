import logging
from flask import Blueprint, render_template, request, session
from services.borrow_service import BorrowService
from models import db, Book, User, BorrowRecord
from utils.decorators import user_required

logger = logging.getLogger(__name__)

borrow_bp = Blueprint('borrow', __name__)


def _get_user_records(user_id):
    """获取当前用户的借阅记录，按记录ID升序排列"""
    return BorrowRecord.query.filter_by(user_id=user_id).order_by(BorrowRecord.record_id.asc()).all()


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

    # 输入验证：图书ID必须为正整数
    if not book_id.isdigit() or int(book_id) <= 0:
        user = db.session.get(User, user_id)
        return render_template('borrow/borrow.html', error='图书ID必须为正整数', user=user)

    try:
        success, msg = BorrowService.borrow_book(int(user_id), int(book_id))
        user = db.session.get(User, user_id)
        if success:
            return render_template('borrow/borrow.html', success=msg, user=user)
        return render_template('borrow/borrow.html', error=msg, user=user)
    except Exception:
        db.session.rollback()
        logger.exception('借阅操作异常: user_id=%s, book_id=%s', user_id, book_id)
        user = db.session.get(User, user_id)
        return render_template('borrow/borrow.html', error='借阅操作失败，请稍后重试', user=user)


@borrow_bp.route('/return_page')
@user_required
def return_page():
    user_id = session.get('user_id')
    records = _get_user_records(user_id)
    return render_template('borrow/return.html', records=records)


@borrow_bp.route('/do_return', methods=['POST'])
@user_required
def do_return():
    record_id = request.form.get('record_id', '').strip()
    user_id = session.get('user_id')

    if not record_id:
        records = _get_user_records(user_id)
        return render_template('borrow/return.html', error='请输入借阅记录ID', records=records)

    # 输入验证：记录ID必须为正整数
    if not record_id.isdigit() or int(record_id) <= 0:
        records = _get_user_records(user_id)
        return render_template('borrow/return.html', error='记录ID必须为正整数', records=records)

    # 权限校验：只能归还自己的借阅记录
    record = db.session.get(BorrowRecord, int(record_id))
    if not record:
        records = _get_user_records(user_id)
        return render_template('borrow/return.html', error='借阅记录不存在', records=records)

    if record.user_id != int(user_id):
        records = _get_user_records(user_id)
        return render_template('borrow/return.html', error='只能归还自己的借阅记录', records=records)

    try:
        success, msg = BorrowService.return_book(int(record_id))
        records = _get_user_records(user_id)
        if success:
            return render_template('borrow/return.html', success=msg, records=records)
        return render_template('borrow/return.html', error=msg, records=records)
    except Exception:
        db.session.rollback()
        logger.exception('归还操作异常: user_id=%s, record_id=%s', user_id, record_id)
        records = _get_user_records(user_id)
        return render_template('borrow/return.html', error='归还操作失败，请稍后重试', records=records)


@borrow_bp.route('/records')
@user_required
def records():
    user_id = request.args.get('user_id', '').strip()
    status = request.args.get('status', '')
    q = BorrowRecord.query

    # 安全地解析 user_id 参数
    if user_id:
        if not user_id.isdigit():
            return render_template('borrow/records.html', error='用户ID必须为正整数',
                                   records=[], user_id=user_id, status=status)
        q = q.filter_by(user_id=int(user_id))

    # 安全地解析 status 参数（0=借阅中, 1=已归还）
    if status != '':
        if status not in ('0', '1'):
            return render_template('borrow/records.html', error='状态值无效',
                                   records=[], user_id=user_id, status=status)
        q = q.filter_by(status=int(status))

    records_list = q.order_by(BorrowRecord.record_id.asc()).all()
    return render_template('borrow/records.html', records=records_list,
                           user_id=user_id, status=status)


@borrow_bp.route('/overdue')
@user_required
def overdue():
    records_list = BorrowService.get_overdue_records()
    return render_template('borrow/overdue.html', records=records_list)


@borrow_bp.route('/quick_search')
@user_required
def quick_search():
    q = request.args.get('q', '').strip()
    books = []
    users = []
    if q:
        # 按ID精确搜索（仅当输入为纯数字时）
        if q.isdigit():
            numeric_id = int(q)
            book_by_id = db.session.get(Book, numeric_id)
            if book_by_id:
                books.append(book_by_id)
            user_by_id = db.session.get(User, numeric_id)
            if user_by_id:
                users.append(user_by_id)

        # 按标题/ISBN/姓名模糊搜索（使用集合避免重复）
        book_ids_seen = {b.book_id for b in books}
        for book in Book.query.filter(Book.title.contains(q) | Book.isbn.contains(q)).all():
            if book.book_id not in book_ids_seen:
                books.append(book)
                book_ids_seen.add(book.book_id)

        user_ids_seen = {u.user_id for u in users}
        for user in User.query.filter(User.name.contains(q)).all():
            if user.user_id not in user_ids_seen:
                users.append(user)
                user_ids_seen.add(user.user_id)

    return render_template('borrow/quick_search.html', books=books, users=users, q=q)
