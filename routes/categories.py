import logging
from flask import Blueprint, render_template, request, redirect, url_for
from models import db, Category
from utils.decorators import admin_required

logger = logging.getLogger(__name__)

categories_bp = Blueprint('categories', __name__)


@categories_bp.route('/')
@admin_required
def list_categories():
    cats = Category.query.order_by(Category.cat_id).all()
    return render_template('categories/list.html', categories=cats)


@categories_bp.route('/add', methods=['GET', 'POST'])
@admin_required
def add_category():
    if request.method == 'POST':
        cat_id = request.form.get('cat_id', '').strip()
        cat_name = request.form.get('cat_name', '').strip()
        location = request.form.get('location', '').strip()
        remark = request.form.get('remark', '').strip()

        if not cat_id or not cat_name:
            return render_template('categories/add.html', error='分类编号和名称为必填')

        if db.session.get(Category, cat_id):
            return render_template('categories/add.html', error='分类编号已存在')

        try:
            cat = Category(cat_id=cat_id, cat_name=cat_name, location=location, remark=remark)
            db.session.add(cat)
            db.session.commit()
            return redirect(url_for('categories.list_categories'))
        except Exception:
            db.session.rollback()
            logger.exception('添加分类异常: cat_id=%s', cat_id)
            return render_template('categories/add.html', error='添加分类失败，请稍后重试')

    return render_template('categories/add.html')


@categories_bp.route('/edit/<cat_id>', methods=['GET', 'POST'])
@admin_required
def edit_category(cat_id):
    cat = db.session.get(Category, cat_id)
    if not cat:
        return redirect(url_for('categories.list_categories'))

    if request.method == 'POST':
        cat_name = request.form.get('cat_name', '').strip()
        if not cat_name:
            return render_template('categories/edit.html', category=cat,
                                   error='分类名称不能为空')

        cat.cat_name = cat_name
        cat.location = request.form.get('location', '').strip()
        cat.remark = request.form.get('remark', '').strip()

        try:
            db.session.commit()
            return redirect(url_for('categories.list_categories'))
        except Exception:
            db.session.rollback()
            logger.exception('编辑分类异常: cat_id=%s', cat_id)
            return render_template('categories/edit.html', category=cat,
                                   error='编辑分类失败，请稍后重试')

    return render_template('categories/edit.html', category=cat)


@categories_bp.route('/delete/<cat_id>', methods=['POST'])
@admin_required
def delete_category(cat_id):
    cat = db.session.get(Category, cat_id)
    if cat:
        if cat.books.count() > 0:
            return render_template('categories/list.html',
                                   categories=Category.query.all(),
                                   error='该分类下仍有图书，无法删除')
        try:
            db.session.delete(cat)
            db.session.commit()
        except Exception:
            db.session.rollback()
            logger.exception('删除分类异常: cat_id=%s', cat_id)
            return render_template('categories/list.html',
                                   categories=Category.query.all(),
                                   error='删除分类失败，请稍后重试')
    return redirect(url_for('categories.list_categories'))
