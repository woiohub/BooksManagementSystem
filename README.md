# 图书借阅管理系统

基于 Flask + SQLAlchemy + Jinja2 的 Web 应用程序，面向学校图书馆业务场景，提供图书管理、用户管理、借阅归还、统计排行等核心功能。

## 项目特点

- **双入口登录**：用户登录（用户ID+密码）和管理员登录（用户名+密码）
- **权限控制**：用户和管理员功能完全隔离，支持独立退出
- **借阅管理**：自动校验借阅权限，自动计算应还日期和违约金
- **图书搜索**：多维度组合搜索（图书ID、ISBN、书名、作者、出版社、分类）
- **统计分析**：图书热度排行、分类频率排行、用户活跃度排行
- **数据完整性**：数据库触发器自动维护库存和借阅计数一致性

## 技术栈

| 层级 | 技术 | 说明 |
|------|------|------|
| Web 框架 | Flask 3.1 | 轻量级服务端框架 |
| ORM | SQLAlchemy 2.0 | 数据库对象关系映射 |
| 模板引擎 | Jinja2 | 服务端动态页面渲染 |
| 数据库 | SQL Server / MySQL | 支持多种数据库 |
| 前端 | HTML + CSS | 响应式布局 |

## 快速开始

### 1. 环境准备

- Python 3.9+
- SQL Server（需安装 ODBC Driver 17）

### 2. 安装依赖

```bash
cd BooksManagementSystem
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### 3. 准备数据库

系统**不自动建表**，需在 SQL Server 中执行建库脚本：

1. 打开 SQL Server Management Studio (SSMS)
2. 执行 `SQL Server数据库设计.txt` 全部内容
3. 确认数据库 `LibraryManagementSystem` 已创建，5 张表已生成

### 4. 配置数据库连接

编辑 `config.py`，确认连接字符串与本地环境匹配：

```python
# 默认：SQL Server Windows 身份验证
SQLALCHEMY_DATABASE_URI = (
    'mssql+pyodbc://@localhost/LibraryManagementSystem?'
    'driver=ODBC+Driver+17+for+SQL+Server&'
    'trusted_connection=yes&'
    'TrustServerCertificate=yes'
)
```

### 5. 启动应用

```bash
python app.py
```

访问 http://127.0.0.1:5000 进入系统。

## 预置账号

### 管理员

| 用户名 | 密码 |
|--------|------|
| admin | admin123 |

### 用户

| 用户ID | 姓名 | 密码 | 用户类型 |
|--------|------|------|----------|
| 1 | 张教师 | 123456 | 教师 |
| 2 | 李教授 | 123456 | 教师 |
| 3 | 王研究生 | 123456 | 研究生 |
| 4 | 赵研究生 | 123456 | 研究生 |
| 5 | 陈本科生 | 123456 | 本科生 |
| 6 | 刘本科生 | 123456 | 本科生 |
| 7 | 孙本科生 | 123456 | 本科生 |

## 功能模块

### 用户功能

- **借阅图书**：自动获取当前登录用户ID，输入图书ID即可借阅
- **归还图书**：输入借阅记录ID，自动计算违约金
- **借阅记录**：查看所有借阅历史，支持筛选
- **图书搜索**：多维度组合搜索图书信息

### 管理员功能

- **用户管理**：增删改查用户信息
- **图书管理**：维护馆藏图书数据
- **分类管理**：维护中图分类与馆藏位置
- **统计看板**：多维度数据统计分析

## 项目结构

```
BooksManagementSystem/
├── app.py                      # Flask 应用入口
├── config.py                   # 数据库连接配置
├── models.py                   # ORM 实体类（5个模型）
├── requirements.txt            # Python 依赖清单
├── SQL Server数据库设计.txt     # 数据库建库建表脚本
├── 项目文档.md                  # 项目技术文档
├── 软件系统操作说明书.md         # 操作使用指南
├── routes/                     # 路由层（6个蓝图）
│   ├── auth.py                 # 用户登录/管理员登录/登出
│   ├── users.py                # 用户 CRUD
│   ├── books.py                # 图书 CRUD + 搜索
│   ├── categories.py           # 分类 CRUD
│   ├── borrow.py               # 借书/还书/查询
│   └── stats.py                # 统计排行
├── utils/                      # 工具模块
│   └── decorators.py           # 权限装饰器
├── services/                   # 业务逻辑层
│   ├── borrow_service.py       # 借阅核心业务
│   └── stats_service.py        # 统计排行业务
├── templates/                  # Jinja2 模板
│   ├── base.html               # 基础布局
│   ├── login.html              # 登录选择页
│   ├── user_login.html         # 用户登录页
│   ├── admin_login.html        # 管理员登录页
│   ├── users/                  # 用户管理页面
│   ├── books/                  # 图书管理页面
│   ├── categories/             # 分类管理页面
│   ├── borrow/                 # 借阅归还页面
│   └── stats/                  # 统计排行页面
└── static/
    └── css/style.css           # 全局样式
```

## 业务规则

### 借阅权限

| 用户类型 | 最大可借 | 借阅期限 | 日违约金 |
|----------|----------|----------|----------|
| 教师 | 20 本 | 60 天 | 0.50 元 |
| 研究生 | 15 本 | 45 天 | 0.30 元 |
| 本科生 | 10 本 | 30 天 | 0.20 元 |

### 违约金计算

```
违约金 = (实际归还日期 - 应还日期) × 日违约金标准
```

- 按期或提前归还：违约金 = 0
- 超期归还：按天累计，自动更新借阅记录和用户总违约金

## 文档

- [项目文档](项目文档.md) - 技术架构、数据库设计、功能模块详细说明
- [软件系统操作说明书](软件系统操作说明书.md) - 安装部署、功能操作指南、常见问题

## 常见问题

**Q: 启动报错 "Can't open lib 'ODBC Driver 17 for SQL Server'"**

A: 未安装 SQL Server ODBC 驱动。下载安装 [ODBC Driver 17 for SQL Server](https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server)。

**Q: 用户无法删除**

A: 该用户仍有未归还的图书。先在「归还图书」页面归还所有图书，再删除用户。

**Q: 如何切换数据库**

A: 修改 `config.py` 中的 `SQLALCHEMY_DATABASE_URI`：

```python
# MySQL
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:password@localhost/LibraryManagementSystem?charset=utf8mb4'
```

## 许可证

本项目为课程实践项目，仅供学习参考使用。
