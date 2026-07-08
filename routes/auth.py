from flask import Blueprint, render_template, request, redirect, url_for, session
from models import db, Admin

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        admin = Admin.query.filter_by(username=username, password=password).first()
        if admin:
            session['admin_id'] = admin.admin_id
            session['admin_username'] = admin.username
            return redirect(url_for('index'))
        return render_template('login.html', error='用户名或密码错误')

    return render_template('login.html')


@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))