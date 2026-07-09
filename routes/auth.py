from flask import Blueprint, render_template, request, redirect, url_for, session
from models import db, Admin, User

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/user_login', methods=['GET', 'POST'])
def user_login():
    """用户登录 - 仅需用户ID"""
    if request.method == 'POST':
        user_id = request.form.get('user_id', '').strip()

        if not user_id:
            return render_template('user_login.html', error='请输入用户ID')

        user = db.session.get(User, int(user_id))
        if user:
            session['user_id'] = user.user_id
            session['user_name'] = user.name
            return redirect(url_for('index'))
        return render_template('user_login.html', error='用户不存在')

    return render_template('user_login.html')


@auth_bp.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    """管理员登录 - 用户名+密码"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

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