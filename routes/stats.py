import logging
from datetime import date
from flask import Blueprint, render_template, request
from services.stats_service import StatsService
from utils.decorators import admin_required

logger = logging.getLogger(__name__)

stats_bp = Blueprint('stats', __name__)


@stats_bp.route('/')
@admin_required
def dashboard():
    try:
        overview = StatsService.get_overview_stats()
        book_heat = StatsService.get_book_heat_ranking(top_n=10)
        cat_heat = StatsService.get_category_heat_ranking()
        user_rank = StatsService.get_user_borrow_ranking(top_n=10)
    except Exception:
        logger.exception('统计面板数据加载异常')
        overview = {
            'total_books': 0, 'total_users': 0, 'active_borrows': 0,
            'total_borrows': 0, 'total_penalty': 0, 'overdue_count': 0,
        }
        book_heat = []
        cat_heat = []
        user_rank = []

    return render_template('stats/dashboard.html', overview=overview,
                           book_heat=book_heat, cat_heat=cat_heat,
                           user_rank=user_rank)


@stats_bp.route('/books')
@admin_required
def book_ranking():
    top_n = request.args.get('top_n', 10, type=int)
    # 限制 top_n 范围，防止过大查询
    top_n = max(1, min(top_n, 100))
    try:
        book_heat = StatsService.get_book_heat_ranking(top_n=top_n)
    except Exception:
        logger.exception('图书热度排行查询异常')
        book_heat = []
    return render_template('stats/book_ranking.html', book_heat=book_heat, top_n=top_n)


@stats_bp.route('/categories')
@admin_required
def category_ranking():
    try:
        cat_heat = StatsService.get_category_heat_ranking()
    except Exception:
        logger.exception('分类热度排行查询异常')
        cat_heat = []
    return render_template('stats/category_ranking.html', cat_heat=cat_heat)


@stats_bp.route('/users')
@admin_required
def user_ranking():
    top_n = request.args.get('top_n', 10, type=int)
    # 限制 top_n 范围，防止过大查询
    top_n = max(1, min(top_n, 100))
    try:
        user_rank = StatsService.get_user_borrow_ranking(top_n=top_n)
    except Exception:
        logger.exception('用户借阅排行查询异常')
        user_rank = []
    return render_template('stats/user_ranking.html', user_rank=user_rank, top_n=top_n)
