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


# 用户类型配额配置
USER_TYPE_CONFIG = {
    '教师': {'max_borrow': 20, 'days_limit': 60, 'penalty_per_day': 0.50},
    '研究生': {'max_borrow': 15, 'days_limit': 45, 'penalty_per_day': 0.30},
    '本科生': {'max_borrow': 10, 'days_limit': 30, 'penalty_per_day': 0.20},
}


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """用户注册"""
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        password = request.form.get('password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()
        user_type = request.form.get('user_type', '').strip()

        # 表单验证
        if not name or not password or not confirm_password or not user_type:
            return render_template('register.html', error='请填写所有必填字段')

        # 密码验证
        if password != confirm_password:
            return render_template('register.html', error='两次输入的密码不一致')

        if len(password) < 6:
            return render_template('register.html', error='密码长度不能少于6位')

        # 用户类型验证
        if user_type not in USER_TYPE_CONFIG:
            return render_template('register.html', error='请选择有效的用户类型')

        # 检查姓名是否已注册
        if User.query.filter_by(name=name).first():
            return render_template('register.html', error='该姓名已被注册')

        # 获取用户类型配额
        config = USER_TYPE_CONFIG[user_type]

        try:
            # 创建新用户
            new_user = User(
                name=name,
                password=password,
                user_type=user_type,
                max_borrow=config['max_borrow'],
                days_limit=config['days_limit'],
                penalty_per_day=config['penalty_per_day'],
                borrowed_count=0,
                penalty_total=0
            )
            db.session.add(new_user)
            db.session.commit()

            return render_template('register.html', success=f'注册成功！您的用户ID为：{new_user.user_id}，请牢记此ID用于登录。')
        except Exception as e:
            db.session.rollback()
            return render_template('register.html', error=f'注册失败：{str(e)}')

    return render_template('register.html')


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
