import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'books-management-secret-key-2024')

    # ── 数据库连接 ──────────────────────────────────────────────
    # 系统不自动建表，需提前在数据库中执行建库建表脚本。
    # 通过环境变量 DATABASE_URL 指定连接，未设置时使用默认值（SQL Server）。
    #
    # 默认：SQL Server（Windows 身份验证）
    #   mssql+pyodbc://@localhost/LibraryManagementSystem?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes&TrustServerCertificate=yes
    #
    # 可选：SQL Server（用户名密码）
    #   mssql+pyodbc://sa:password@localhost/LibraryManagementSystem?driver=ODBC+Driver+17+for+SQL+Server&TrustServerCertificate=yes
    #
    # 可选：MySQL
    #   mysql+pymysql://root:password@localhost/LibraryManagementSystem?charset=utf8mb4

    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', (
        'mssql+pyodbc://@localhost\SQLEXPRESS/LibraryManagementSystem?'
        'driver=ODBC+Driver+17+for+SQL+Server&'
        'trusted_connection=yes&'
        'TrustServerCertificate=yes'
    ))
    SQLALCHEMY_TRACK_MODIFICATIONS = False