from flask import Blueprint, render_template, request, redirect, url_for
from models import db, Book, Category
from utils.decorators import admin_required

books_bp = Blueprint('books', __name__)


@books_bp.route('/')
@admin_required
def list_books():
    search = request.args.get('search', '').strip()
    cat_filter = request.args.get('cat_id', '').strip()
    q = Book.query
    if search:
        q = q.filter(Book.title.contains(search) | Book.author.contains(search))
    if cat_filter:
        q = q.filter_by(cat_id=cat_filter)
    books = q.order_by(Book.book_id).all()
    return render_template('books/list.html', books=books, search=search,
                           cat_filter=cat_filter, categories=Category.query.all())


@books_bp.route('/add', methods=['GET', 'POST'])
@admin_required
def add_book():
    if request.method == 'POST':
        isbn = request.form.get('isbn', '').strip()
        title = request.form.get('title', '').strip()
        author = request.form.get('author', '').strip()
        publisher = request.form.get('publisher', '').strip()
        pub_year = request.form.get('pub_year', '').strip()
        cat_id = request.form.get('cat_id', '').strip()
        total_stock = request.form.get('total_stock', '0').strip()
        shelf_location = request.form.get('shelf_location', '').strip()

        if not isbn or not title or not cat_id:
            return render_template('books/add.html', error='ISBN、书名、分类为必填',
                                   categories=Category.query.all())

        book = Book(
            isbn=isbn, title=title, author=author, publisher=publisher,
            pub_year=int(pub_year) if pub_year else None,
            cat_id=cat_id,
            total_stock=int(total_stock),
            available_stock=int(total_stock),
            shelf_location=shelf_location
        )
        db.session.add(book)
        db.session.commit()
        return redirect(url_for('books.list_books'))

    return render_template('books/add.html', categories=Category.query.all())


@books_bp.route('/edit/<int:book_id>', methods=['GET', 'POST'])
@admin_required
def edit_book(book_id):
    book = db.session.get(Book, book_id)
    if not book:
        return redirect(url_for('books.list_books'))

    if request.method == 'POST':
        book.isbn = request.form.get('isbn', '').strip()
        book.title = request.form.get('title', '').strip()
        book.author = request.form.get('author', '').strip()
        book.publisher = request.form.get('publisher', '').strip()
        pub_year = request.form.get('pub_year', '').strip()
        book.pub_year = int(pub_year) if pub_year else None
        book.cat_id = request.form.get('cat_id', '').strip()
        new_total = int(request.form.get('total_stock', '0'))
        borrowed = book.total_stock - book.available_stock
        if new_total < borrowed:
            return render_template('books/edit.html', book=book,
                                   categories=Category.query.all(),
                                   error=f'总库存不能小于当前借出数量({borrowed})')
        book.total_stock = new_total
        book.available_stock = new_total - borrowed
        book.shelf_location = request.form.get('shelf_location', '').strip()
        db.session.commit()
        return redirect(url_for('books.list_books'))

    return render_template('books/edit.html', book=book, categories=Category.query.all())


@books_bp.route('/delete/<int:book_id>', methods=['POST'])
@admin_required
def delete_book(book_id):
    book = db.session.get(Book, book_id)
    if book:
        if book.available_stock < book.total_stock:
            return render_template('books/list.html',
                                   books=Book.query.all(),
                                   categories=Category.query.all(),
                                   error='该图书仍有未归还记录，无法删除')
        db.session.delete(book)
        db.session.commit()
    return redirect(url_for('books.list_books'))


@books_bp.route('/search')
def search():
    """图书搜索页面 - 支持多维度搜索"""
    book_id = request.args.get('book_id', '').strip()
    isbn = request.args.get('isbn', '').strip()
    title = request.args.get('title', '').strip()
    author = request.args.get('author', '').strip()
    publisher = request.args.get('publisher', '').strip()
    cat_id = request.args.get('cat_id', '').strip()

    q = Book.query.join(Category)

    if book_id:
        q = q.filter(Book.book_id == int(book_id))
    if isbn:
        q = q.filter(Book.isbn.contains(isbn))
    if title:
        q = q.filter(Book.title.contains(title))
    if author:
        q = q.filter(Book.author.contains(author))
    if publisher:
        q = q.filter(Book.publisher.contains(publisher))
    if cat_id:
        q = q.filter(Book.cat_id == cat_id)

    books = q.order_by(Book.book_id).all()
    categories = Category.query.all()

    return render_template('books/search.html', books=books, categories=categories,
                           book_id=book_id, isbn=isbn, title=title,
                           author=author, publisher=publisher, cat_id=cat_id)