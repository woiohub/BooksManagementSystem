from functools import wraps
from flask import session, redirect, url_for, flash

def admin_required(f):
    """管理员权限装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_id'):
            flash('请先登录管理员账号', 'error')
            return redirect(url_for('auth.admin_login'))
        return f(*args, **kwargs)
    return decorated_function

def user_required(f):
    """用户权限装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('user_id'):
            flash('请先登录用户账号', 'error')
            return redirect(url_for('auth.user_login'))
        return f(*args, **kwargs)
    return decorated_function
