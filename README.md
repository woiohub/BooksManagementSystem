# 图书借阅管理系统

基于 Flask + SQLAlchemy 的图书借阅管理系统，支持用户注册登录、图书借阅归还、分类管理、统计分析等功能。

## 系统特点

- **双入口登录**：用户和管理员分别登录，权限隔离
- **用户注册**：支持用户自主注册，根据用户类型自动设置借阅配额
- **图书管理**：完整的图书CRUD操作，支持多维度搜索
- **借阅管理**：自动计算违约金，库存实时同步
- **统计分析**：多维度数据统计和排行榜
- **权限控制**：基于装饰器的权限验证机制

## 技术栈

- **后端框架**：Flask 3.1.0
- **ORM框架**：SQLAlchemy 2.0.36 + Flask-SQLAlchemy 3.1.1
- **数据库**：SQL Server / MySQL（支持两种数据库）
- **前端**：Bootstrap 5 + Jinja2 模板引擎
- **开发语言**：Python 3.13+

## 项目结构

```
BooksManagementSystem/
├── app.py                 # 应用入口
├── config.py              # 配置文件
├── models.py              # 数据模型（5个实体类）
├── requirements.txt       # 依赖清单
├── routes/               # 路由模块
│   ├── __init__.py
│   ├── auth.py           # 认证模块（登录/注册/登出）
│   ├── users.py          # 用户管理
│   ├── books.py          # 图书管理
│   ├── categories.py     # 分类管理
│   ├── borrow.py         # 借阅归还
│   └── stats.py          # 统计分析
├── services/             # 业务逻辑层
│   ├── __init__.py
│   ├── borrow_service.py # 借阅服务
│   └── stats_service.py  # 统计服务
├── utils/                # 工具模块
│   ├── __init__.py
│   └── decorators.py     # 权限装饰器
├── templates/            # 模板文件
│   ├── base.html         # 基础模板
│   ├── index.html        # 首页
│   ├── login.html        # 登录选择页
│   ├── user_login.html   # 用户登录页
│   ├── admin_login.html  # 管理员登录页
│   ├── register.html     # 用户注册页
│   ├── users/            # 用户管理模板
│   ├── books/            # 图书管理模板
│   ├── borrow/           # 借阅管理模板
│   ├── categories/       # 分类管理模板
│   └── stats/            # 统计分析模板
└── static/               # 静态资源
    └── css/
        └── style.css
```

## 数据库设计

系统包含5个核心实体类：

1. **User（用户）**
   - user_id, name, password, user_type
   - max_borrow, days_limit, penalty_per_day
   - borrowed_count, penalty_total

2. **Admin（管理员）**
   - admin_id, username, password

3. **Book（图书）**
   - book_id, isbn, title, author, publisher, pub_year
   - cat_id, total_stock, available_stock, shelf_location

4. **Category（分类）**
   - cat_id, cat_name, location, remark

5. **BorrowRecord（借阅记录）**
   - record_id, book_id, user_id
   - borrow_date, due_date, return_date
   - penalty, status

## 安装部署

### 1. 环境要求

- Python 3.13+
- SQL Server 或 MySQL 数据库

### 2. 安装依赖

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 3. 数据库配置

#### SQL Server 配置

1. 执行 `SQL Server数据库设计.txt` 中的建库脚本
2. 配置数据库连接（编辑 `config.py` 或设置环境变量）：

```bash
# Windows 身份验证
set DATABASE_URL=mssql+pyodbc://@localhost\SQLEXPRESS/LibraryManagementSystem?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes&TrustServerCertificate=yes

# 或使用用户名密码
set DATABASE_URL=mssql+pyodbc://sa:password@localhost/LibraryManagementSystem?driver=ODBC+Driver+17+for+SQL+Server&TrustServerCertificate=yes
```

#### MySQL 配置

```bash
set DATABASE_URL=mysql+pymysql://root:password@localhost/LibraryManagementSystem?charset=utf8mb4
```

### 4. 启动应用

```bash
python app.py
```

访问：http://127.0.0.1:5000

## 功能说明

### 用户功能

#### 用户注册

1. 访问首页，点击"用户登录"
2. 点击"注册新账号"
3. 填写注册信息：
   - **姓名**：必须唯一，用于身份识别
   - **密码**：至少6位字符
   - **用户类型**：本科生/研究生/教师
4. 注册成功后，系统自动分配用户ID

**用户类型配额**：

| 用户类型 | 最大借阅数 | 借阅期限 | 日违约金 |
|----------|------------|----------|----------|
| 本科生   | 10本       | 30天     | 0.20元   |
| 研究生   | 15本       | 45天     | 0.30元   |
| 教师     | 20本       | 60天     | 0.50元   |

#### 用户登录

1. 访问首页，点击"用户登录"
2. 输入用户ID和密码
3. 登录成功后进入用户功能界面

**预置用户账号**：

| 用户ID | 姓名     | 密码   | 用户类型 |
|--------|----------|--------|----------|
| 1      | 张教师   | 123456 | 教师     |
| 2      | 李研究生 | 123456 | 研究生   |
| 3      | 王本科生 | 123456 | 本科生   |

#### 借阅图书

1. 点击导航栏"借阅图书"
2. 输入图书ID（系统自动获取当前用户ID）
3. 确认借阅信息
4. 系统检查借阅权限并创建借阅记录

#### 归还图书

1. 点击导航栏"归还图书"
2. 输入借阅记录ID
3. 系统自动计算违约金
4. 确认归还

#### 借阅记录

- 查看所有借阅历史
- 支持按状态筛选（借阅中/已归还）
- 显示图书名称、借阅日期、应还日期、违约金等信息

#### 图书搜索

- 支持多维度组合搜索
- 可按书名、作者、ISBN、分类等条件搜索
- 显示图书详细信息和可借数量

### 管理员功能

#### 管理员登录

1. 访问首页，点击"管理员登录"
2. 输入管理员用户名和密码

**预置管理员账号**：

| 用户名 | 密码   |
|--------|--------|
| admin  | admin123 |

#### 用户管理

- 查看用户列表
- 添加新用户
- 编辑用户信息（显示当前密码）
- 删除用户（自动清理借阅记录）

#### 图书管理

- 查看图书列表
- 添加新图书
- 编辑图书信息
- 删除图书

#### 分类管理

- 查看分类列表
- 添加新分类
- 编辑分类信息
- 删除分类

#### 统计分析

- **借阅统计**：总借阅数、活跃用户数、超期记录数
- **图书排行**：热门图书排行榜
- **用户分析**：用户借阅情况统计

## 核心业务逻辑

### 1. 借阅权限校验

```python
# 检查用户是否达到最大借阅数
if user.borrowed_count >= user.max_borrow:
    raise Exception('已达到最大借阅数量')

# 检查图书库存
if book.available_stock <= 0:
    raise Exception('图书库存不足')
```

### 2. 违约金计算

```python
# 由数据库触发器自动计算
# 违约金 = 超期天数 × 日违约金率
```

### 3. 库存同步

```python
# 借阅时：available_stock -= 1, borrowed_count += 1
# 归还时：available_stock += 1, borrowed_count -= 1
# 由数据库触发器自动同步
```

## 安全性与健壮性

### 输入验证

- 所有ID参数验证为正整数
- 必填字段验证
- 邮箱格式验证（如使用）
- 密码长度验证（至少6位）
- 业务规则验证（借阅数量、库存等）

### 权限控制

- 用户权限：只能访问自己的借阅记录
- 管理员权限：可管理所有用户和图书
- 越权操作防护：通过装饰器验证权限

### 异常处理

- 数据库事务管理（自动回滚）
- 友好的错误提示
- 完整的日志记录

### 性能优化

- 数据库索引优化（isbn, title, author, book_id, user_id, status）
- 查询优化（使用JOIN减少查询次数）
- 分页支持（大数据量列表）

## 常见问题

### 1. 数据库连接失败

**问题**：启动时提示数据库连接失败

**解决**：
- 检查数据库服务是否启动
- 检查数据库连接字符串配置
- 确认数据库已创建并执行建表脚本
- 检查用户名密码是否正确

### 2. 用户注册失败

**问题**：注册时提示"该姓名已被注册"

**解决**：
- 姓名必须唯一，请更换其他姓名
- 或使用已注册的用户ID直接登录

### 3. 借阅时提示"已达到最大借阅数量"

**问题**：无法借阅更多图书

**解决**：
- 先归还部分图书
- 或联系管理员提升借阅配额

### 4. 违约金计算不正确

**问题**：归还时违约金与预期不符

**解决**：
- 违约金由数据库触发器自动计算
- 检查数据库触发器是否正常工作
- 确认用户类型的日违约金率设置

## 开发说明

### 运行开发服务器

```bash
python app.py
```

### 数据库迁移

系统不自动建表，需提前执行建库脚本。如需修改表结构，请手动更新数据库。

### 代码规范

- 遵循PEP 8编码规范
- 使用类型提示
- 添加必要的注释
- 保持函数简洁（单一职责）

## 更新日志

### v1.0.0 (2026-07-11)

- ✅ 实现用户注册功能
- ✅ 实现双入口登录（用户/管理员）
- ✅ 实现图书借阅归还功能
- ✅ 实现分类管理
- ✅ 实现统计分析
- ✅ 添加权限控制装饰器
- ✅ 优化借阅记录展示
- ✅ 修复删除用户外键约束问题
- ✅ 修复SQLAlchemy版本兼容性问题

## 许可证

本项目仅供学习和课程实践使用。

## 联系方式

如有问题或建议，请联系开发团队。
