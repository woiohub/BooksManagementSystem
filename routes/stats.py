from datetime import date
from flask import Blueprint, render_template, request
from services.stats_service import StatsService

stats_bp = Blueprint('stats', __name__)


@stats_bp.route('/')
def dashboard():
    overview = StatsService.get_overview_stats()
    book_heat = StatsService.get_book_heat_ranking(top_n=10)
    cat_heat = StatsService.get_category_heat_ranking()
    user_rank = StatsService.get_user_borrow_ranking(top_n=10)
    return render_template('stats/dashboard.html', overview=overview,
                           book_heat=book_heat, cat_heat=cat_heat,
                           user_rank=user_rank)


@stats_bp.route('/books')
def book_ranking():
    top_n = request.args.get('top_n', 10, type=int)
    book_heat = StatsService.get_book_heat_ranking(top_n=top_n)
    return render_template('stats/book_ranking.html', book_heat=book_heat, top_n=top_n)


@stats_bp.route('/categories')
def category_ranking():
    cat_heat = StatsService.get_category_heat_ranking()
    return render_template('stats/category_ranking.html', cat_heat=cat_heat)


@stats_bp.route('/users')
def user_ranking():
    top_n = request.args.get('top_n', 10, type=int)
    user_rank = StatsService.get_user_borrow_ranking(top_n=top_n)
    return render_template('stats/user_ranking.html', user_rank=user_rank, top_n=top_n)