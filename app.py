from flask import Flask, render_template
from config import Config
from models import db


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)

    from routes.auth import auth_bp
    from routes.users import users_bp
    from routes.books import books_bp
    from routes.categories import categories_bp
    from routes.borrow import borrow_bp
    from routes.stats import stats_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(users_bp, url_prefix='/users')
    app.register_blueprint(books_bp, url_prefix='/books')
    app.register_blueprint(categories_bp, url_prefix='/categories')
    app.register_blueprint(borrow_bp, url_prefix='/borrow')
    app.register_blueprint(stats_bp, url_prefix='/stats')

    @app.route('/')
    def index():
        return render_template('index.html')

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)