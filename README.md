# 薪酬计算管理系统

基于 Flask 的薪酬计算管理系统，当前包含用户管理中心模块。

## 系统架构

- **后端框架**: Flask
- **数据库**: MySQL
- **ORM**: 自定义数据库操作类

## 功能模块

### 用户管理中心

- **Web 界面**: 现代化的用户管理界面
- 用户列表查询（支持分页、筛选、搜索）
- 用户详情查询
- 用户创建
- 用户信息更新
- 用户删除（软删除）
- 用户登录验证

## Web 界面访问

启动应用后，可以通过浏览器访问：

- **首页**: `http://localhost:5001/`
- **用户管理页面**: `http://localhost:5001/users`
- **API 文档**: `http://localhost:5001/api`

Web 界面功能：
- 📋 用户列表展示（表格形式）
- 🔍 实时搜索和筛选
- ➕ 添加新用户（模态框表单）
- ✏️ 编辑用户信息
- 🗑️ 删除用户（软删除）
- 📄 分页浏览
- 🎨 现代化 UI 设计，响应式布局

## 安装和配置

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

或使用指定的 Python 解释器：

```bash
python3 -m pip install -r requirements.txt
```

### 2. 配置数据库

编辑 `config.json` 文件，确保数据库配置正确：

```json
{
  "database": {
    "host": "49.232.75.178",
    "port": 3306,
    "username": "admin",
    "password": "wlshyph!2017",
    "database": "salary_management",
    "charset": "utf8mb4",
    "connection_timeout": 30
  }
}
```

**注意**: 如果 `database` 字段为空，系统会自动创建名为 `salary_management` 的数据库。

### 3. 初始化数据库

```bash
python3 init_db.py
```

这将自动：
- 创建数据库（如果不存在）
- 创建用户表

### 4. 启动应用

**方式 1: 使用启动脚本（推荐）**

```bash
./run.sh
```

**方式 2: 直接运行**

```bash
python3 app.py
```

应用将在 `http://localhost:5000` 启动

### 5. （可选）导入示例数据

在空库环境下，可以运行脚本快速创建基础账号：

```bash
python3 create_test_users.py
```

脚本会自动确保示例部门、职位存在，并写入若干测试用户。

## API 接口文档

### 基础信息

- **Base URL**: `http://localhost:5000`
- **Content-Type**: `application/json`

### 用户管理接口

#### 1. 获取用户列表

- **URL**: `GET /api/users`
- **参数**:
  - `page` (可选): 页码，默认 1
- `page_size` (可选): 每页数量，默认 20
- `status` (可选): 状态筛选，1-启用，0-禁用
- `department_id` (可选): 部门 ID 筛选
- `keyword` (可选): 关键词搜索（用户名、姓名、工号）

**示例**:
```bash
curl http://localhost:5000/api/users?page=1&page_size=10
curl http://localhost:5000/api/users?department_id=1
curl http://localhost:5000/api/users?keyword=张三
```

**响应**:
```json
{
  "success": true,
  "data": {
    "users": [
      {
        "id": 1,
        "username": "zhangsan",
        "real_name": "张三",
        "email": "zhangsan@example.com",
        "phone": "13800138000",
        "department_id": 1,
        "department": "技术部",
        "position_id": 2,
        "position": "部长",
        "employee_id": "E001",
        "status": 1,
        "role": "admin"
      }
    ],
    "pagination": {
      "total": 100,
      "page": 1,
      "page_size": 10,
      "total_pages": 10
    }
  }
}
```

#### 2. 获取用户详情

- **URL**: `GET /api/users/<id>`
- **示例**: `GET /api/users/1`

#### 3. 创建用户

- **URL**: `POST /api/users`
- **请求体**:
```json
{
  "username": "zhangsan",
  "password": "123456",
  "real_name": "张三",
  "email": "zhangsan@example.com",
  "phone": "13800138000",
  "department_id": 1,
  "position_id": 2,
  "employee_id": "E001",
  "status": 1
}
```

**必需字段**: `username`, `password`, `real_name`, `department_id`, `position_id`

#### 4. 更新用户

- **URL**: `PUT /api/users/<id>`
- **请求体**: 同创建用户，但所有字段都是可选的

#### 5. 删除用户（软删除）

- **URL**: `DELETE /api/users/<id>`
- **说明**: 将用户状态设置为禁用（status=0）

#### 6. 用户登录

- **URL**: `POST /api/users/login`
- **请求体**:
```json
{
  "username": "zhangsan",
  "password": "123456"
}
```

#### 7. 搜索用户

- **URL**: `GET /api/users/search?keyword=关键词`
- **说明**: 根据用户名、姓名、工号搜索

## 数据库表结构

### users 表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT | 主键，自增 |
| username | VARCHAR(50) | 用户名（唯一） |
| password | VARCHAR(255) | 密码（SHA256加密） |
| real_name | VARCHAR(50) | 真实姓名 |
| email | VARCHAR(100) | 邮箱 |
| phone | VARCHAR(20) | 手机号 |
| department_id | INT | 部门 ID（外键） |
| position_id | INT | 职位 ID（外键） |
| employee_id | VARCHAR(50) | 工号（唯一） |
| status | TINYINT | 状态：1-启用，0-禁用 |
| role | VARCHAR(20) | 角色：super_admin / admin / user |
| created_at | DATETIME | 创建时间 |
| updated_at | DATETIME | 更新时间 |

### departments 表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT | 主键，自增 |
| name | VARCHAR(100) | 部门名称（唯一） |
| description | VARCHAR(255) | 描述 |
| status | TINYINT | 状态：1-启用，0-禁用 |
| created_at | DATETIME | 创建时间 |
| updated_at | DATETIME | 更新时间 |

### positions 表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT | 主键，自增 |
| name | VARCHAR(100) | 职位名称（唯一） |
| role | VARCHAR(20) | 对应角色（super_admin / admin / user） |
| description | VARCHAR(255) | 描述 |
| status | TINYINT | 状态：1-启用，0-禁用 |
| created_at | DATETIME | 创建时间 |
| updated_at | DATETIME | 更新时间 |

## 使用示例

### Python 示例

```python
import requests

base_url = "http://localhost:5000"

# 创建用户
user_data = {
    "username": "testuser",
    "password": "123456",
    "real_name": "测试用户",
    "email": "test@example.com",
    "department_id": 1,
    "position_id": 2,
    "employee_id": "E001"
}
response = requests.post(f"{base_url}/api/users", json=user_data)
print(response.json())

# 获取用户列表
response = requests.get(f"{base_url}/api/users?page=1&page_size=10")
print(response.json())

# 用户登录
login_data = {
    "username": "testuser",
    "password": "123456"
}
response = requests.post(f"{base_url}/api/users/login", json=login_data)
print(response.json())
```

### curl 示例

```bash
# 创建用户
curl -X POST http://localhost:5000/api/users \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "123456",
    "real_name": "测试用户",
    "email": "test@example.com",
    "department_id": 1,
    "position_id": 2
  }'

# 获取用户列表
curl http://localhost:5000/api/users

# 用户登录
curl -X POST http://localhost:5000/api/users/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "123456"
  }'
```

## 项目结构

```
xl/
├── app.py              # Flask 主应用
├── database.py         # 数据库连接模块
├── config.json         # 配置文件
├── init_db.py          # 数据库初始化脚本
├── requirements.txt    # 依赖文件
├── run.sh              # 启动脚本
├── README.md           # 说明文档
├── models/
│   ├── __init__.py
│   └── user.py         # 用户模型
├── templates/          # HTML 模板
│   ├── base.html       # 基础模板
│   ├── index.html      # 首页
│   └── users.html      # 用户管理页面
└── static/             # 静态文件
    ├── css/
    │   └── style.css   # 样式文件
    └── js/
        ├── main.js     # 通用 JavaScript
        └── users.js    # 用户管理 JavaScript
```

## 注意事项

1. 密码使用 SHA256 加密存储
2. 用户删除采用软删除机制（更新状态为禁用）
3. 用户名和工号必须唯一
4. 首次运行会自动创建数据库和表结构
5. 确保 MySQL 服务器可访问且配置正确

## 后续开发

- [ ] 薪酬管理模块
- [ ] 考勤管理模块
- [ ] 权限管理系统
- [ ] JWT 认证
- [ ] 日志记录
- [ ] 单元测试
