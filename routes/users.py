import logging
from flask import Blueprint, render_template, request, redirect, url_for
from models import db, User
from utils.decorators import admin_required

logger = logging.getLogger(__name__)

users_bp = Blueprint('users', __name__)

USER_TYPE_QUOTAS = {
    '教师': {'max_borrow': 20, 'days_limit': 60, 'penalty_per_day': 0.50},
    '研究生': {'max_borrow': 15, 'days_limit': 45, 'penalty_per_day': 0.30},
    '本科生': {'max_borrow': 10, 'days_limit': 30, 'penalty_per_day': 0.20},
}

USER_TYPE_NAMES = list(USER_TYPE_QUOTAS.keys())


@users_bp.route('/')
@admin_required
def list_users():
    search = request.args.get('search', '').strip()
    q = User.query
    if search:
        q = q.filter(User.name.contains(search))
    users = q.order_by(User.user_id).all()
    return render_template('users/list.html', users=users, search=search)


@users_bp.route('/add', methods=['GET', 'POST'])
@admin_required
def add_user():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        password = request.form.get('password', '').strip()
        user_type = request.form.get('user_type', '').strip()

        if not name or not password or not user_type:
            return render_template('users/add.html', error='所有字段均为必填',
                                   user_type_names=USER_TYPE_NAMES,
                                   quotas=USER_TYPE_QUOTAS)

        if user_type not in USER_TYPE_QUOTAS:
            return render_template('users/add.html', error='无效的用户类型',
                                   user_type_names=USER_TYPE_NAMES,
                                   quotas=USER_TYPE_QUOTAS)

        q = USER_TYPE_QUOTAS[user_type]
        try:
            user = User(
                name=name, password=password, user_type=user_type,
                max_borrow=q['max_borrow'], days_limit=q['days_limit'],
                penalty_per_day=q['penalty_per_day']
            )
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('users.list_users'))
        except Exception:
            db.session.rollback()
            logger.exception('添加用户异常: name=%s', name)
            return render_template('users/add.html', error='添加用户失败，请稍后重试',
                                   user_type_names=USER_TYPE_NAMES,
                                   quotas=USER_TYPE_QUOTAS)

    return render_template('users/add.html', user_type_names=USER_TYPE_NAMES,
                           quotas=USER_TYPE_QUOTAS)


@users_bp.route('/edit/<int:user_id>', methods=['GET', 'POST'])
@admin_required
def edit_user(user_id):
    user = db.session.get(User, user_id)
    if not user:
        return redirect(url_for('users.list_users'))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        if not name:
            return render_template('users/edit.html', user=user,
                                   user_type_names=USER_TYPE_NAMES,
                                   quotas=USER_TYPE_QUOTAS,
                                   error='用户名不能为空')

        user.name = name
        new_password = request.form.get('password', '').strip()
        if new_password:
            user.password = new_password
        user_type = request.form.get('user_type', '').strip()
        if user_type in USER_TYPE_QUOTAS:
            user.user_type = user_type
            user.max_borrow = request.form.get('max_borrow', 0, type=int)
            user.days_limit = request.form.get('days_limit', 0, type=int)
            user.penalty_per_day = request.form.get('penalty_per_day', 0, type=float)

        try:
            db.session.commit()
            return redirect(url_for('users.list_users'))
        except Exception:
            db.session.rollback()
            logger.exception('编辑用户异常: user_id=%s', user_id)
            return render_template('users/edit.html', user=user,
                                   user_type_names=USER_TYPE_NAMES,
                                   quotas=USER_TYPE_QUOTAS,
                                   error='编辑用户失败，请稍后重试')

    return render_template('users/edit.html', user=user,
                           user_type_names=USER_TYPE_NAMES,
                           quotas=USER_TYPE_QUOTAS)


@users_bp.route('/delete/<int:user_id>', methods=['POST'])
@admin_required
def delete_user(user_id):
    user = db.session.get(User, user_id)
    if user:
        if user.borrowed_count > 0:
            return render_template('users/list.html',
                                   users=User.query.all(),
                                   error='该用户仍有未归还图书，无法删除')
        try:
            db.session.delete(user)
            db.session.commit()
        except Exception:
            db.session.rollback()
            logger.exception('删除用户异常: user_id=%s', user_id)
            return render_template('users/list.html',
                                   users=User.query.all(),
                                   error='删除用户失败，请稍后重试')
    return redirect(url_for('users.list_users'))
