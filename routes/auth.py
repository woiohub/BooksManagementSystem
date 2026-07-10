from flask import Blueprint, render_template, request, redirect, url_for, session
from models import db, Admin, User

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/user_login', methods=['GET', 'POST'])
def user_login():
    """用户登录 - 用户ID+密码"""
    if request.method == 'POST':
        user_id = request.form.get('user_id', '').strip()
        password = request.form.get('password', '').strip()

        if not user_id or not password:
            return render_template('user_login.html', error='请输入用户ID和密码')

        # 输入验证：用户ID必须为正整数
        if not user_id.isdigit() or int(user_id) <= 0:
            return render_template('user_login.html', error='用户ID必须为正整数')

        user = User.query.filter_by(user_id=int(user_id), password=password).first()
        if user:
            session['user_id'] = user.user_id
            session['user_name'] = user.name
            return redirect(url_for('index'))
        return render_template('user_login.html', error='用户ID或密码错误')

    return render_template('user_login.html')


@auth_bp.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    """管理员登录 - 用户名+密码"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        if not username or not password:
            return render_template('admin_login.html', error='请输入用户名和密码')

        admin = Admin.query.filter_by(username=username, password=password).first()
        if admin:
            session['admin_id'] = admin.admin_id
            session['admin_username'] = admin.username
            return redirect(url_for('index'))
        return render_template('admin_login.html', error='用户名或密码错误')

    return render_template('admin_login.html')


@auth_bp.route('/login')
def login():
    """登录选择页"""
    return render_template('login.html')


@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


@auth_bp.route('/logout_admin')
def logout_admin():
    """管理员退出登录"""
    session.pop('admin_id', None)
    session.pop('admin_username', None)
    return redirect(url_for('index'))


@auth_bp.route('/logout_user')
def logout_user():
    """用户退出登录"""
    session.pop('user_id', None)
    session.pop('user_name', None)
    return redirect(url_for('index'))
