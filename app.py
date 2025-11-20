#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
薪酬计算管理系统 - 主应用
用户管理中心模块
"""

from flask import Flask, jsonify, request, render_template, session, redirect, url_for
from flask_cors import CORS
from functools import wraps
import sys
import os
import secrets

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from models.user import User

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False  # 支持中文
app.config['SECRET_KEY'] = secrets.token_hex(16)  # 用于 session 加密

# 启用 CORS 支持
CORS(app, resources={r"/api/*": {"origins": "*"}})


def login_required(f):
    """登录验证装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 检查 session 中是否有用户信息
        if 'user_id' not in session:
            return redirect(url_for('login_page'))
        return f(*args, **kwargs)
    return decorated_function


def permission_required(permission):
    """权限验证装饰器
    
    Args:
        permission: 需要的权限级别
            'super_admin': 超级管理员（所有权限）
            'admin': 管理员（用户管理部分的所有权限）
            'user': 普通用户（只能查看）
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                return redirect(url_for('login_page'))
            
            user_role = session.get('role', 'user')
            
            # 权限检查
            if permission == 'super_admin':
                if user_role != 'super_admin':
                    return jsonify({
                        'success': False,
                        'message': '需要超级管理员权限'
                    }), 403
            elif permission == 'admin':
                if user_role not in ['super_admin', 'admin']:
                    return jsonify({
                        'success': False,
                        'message': '需要管理员权限'
                    }), 403
            elif permission == 'view':
                # 所有登录用户都可以查看
                pass
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def can_edit():
    """检查当前用户是否有编辑权限"""
    if 'user_id' not in session:
        return False
    user_role = session.get('role', 'user')
    return user_role in ['super_admin', 'admin']


def can_delete():
    """检查当前用户是否有删除权限"""
    if 'user_id' not in session:
        return False
    user_role = session.get('role', 'user')
    return user_role == 'super_admin'


@app.route('/login', methods=['GET'])
def login_page():
    """登录页面"""
    # 如果已登录，重定向到首页
    if 'user_id' in session:
        return redirect(url_for('index_page'))
    return render_template('login.html')


@app.route('/register', methods=['GET'])
def register_page():
    """注册页面"""
    # 如果已登录，重定向到首页
    if 'user_id' in session:
        return redirect(url_for('index_page'))
    return render_template('register.html')


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    """登出"""
    session.clear()
    return redirect(url_for('login_page'))


@app.route('/', methods=['GET'])
@login_required
def index_page():
    """首页"""
    return render_template('index.html')


@app.route('/users', methods=['GET'])
@login_required
def users_page():
    """用户管理页面"""
    # 传递当前用户权限信息到模板
    user_role = session.get('role', 'user')
    can_edit_user = user_role in ['super_admin', 'admin']
    can_delete_user = user_role == 'super_admin'
    can_disable_user = user_role in ['super_admin', 'admin']
    return render_template('users.html', 
                         can_edit=can_edit_user, 
                         can_delete=can_delete_user,
                         can_disable=can_disable_user,
                         current_user_id=session.get('user_id'),
                         user_role=user_role)


@app.route('/api', methods=['GET'])
def api_index():
    """API 首页"""
    return jsonify({
        'message': '薪酬计算管理系统 - 用户管理中心',
        'version': '1.0.0',
        'modules': {
            'user_management': '用户管理中心'
        },
        'endpoints': {
            'GET /': '首页',
            'GET /users': '用户管理页面',
            'GET /api': 'API 信息',
            'GET /api/users': '获取用户列表',
            'GET /api/users/<id>': '获取用户详情',
            'POST /api/users': '创建用户',
            'PUT /api/users/<id>': '更新用户',
            'DELETE /api/users/<id>': '删除用户（彻底删除，仅超级管理员）',
            'POST /api/users/login': '用户登录',
            'GET /api/users/search': '搜索用户'
        }
    })


@app.route('/api/users', methods=['GET'])
@permission_required('view')
def get_users():
    """获取用户列表（支持分页和筛选）"""
    try:
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 20))
        status = request.args.get('status')
        department = request.args.get('department')
        keyword = request.args.get('keyword')
        
        if status is not None:
            status = int(status)
        
        # 获取当前用户的部门和角色（用于权限过滤）
        current_user = User.get_by_id(session.get('user_id'))
        user_department = current_user.department if current_user else None
        user_role = session.get('role', 'user')
        
        result = User.get_all(
            page=page,
            page_size=page_size,
            status=status,
            department=department,
            keyword=keyword,
            user_department=user_department,
            user_role=user_role
        )
        
        return jsonify({
            'success': True,
            'data': {
                'users': [user.to_dict() for user in result['users']],
                'pagination': {
                    'total': result['total'],
                    'page': result['page'],
                    'page_size': result['page_size'],
                    'total_pages': result['total_pages']
                }
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取用户列表失败: {str(e)}'
        }), 500


@app.route('/api/users/<int:user_id>', methods=['GET'])
@permission_required('view')
def get_user(user_id):
    """获取用户详情"""
    try:
        user = User.get_by_id(user_id)
        if not user:
            return jsonify({
                'success': False,
                'message': '用户不存在'
            }), 404
        
        # 权限检查：非超级管理员只能查看本部门的用户
        current_user = User.get_by_id(session.get('user_id'))
        user_role = session.get('role', 'user')
        if user_role != 'super_admin' and current_user:
            # 如果当前用户没有部门（注册用户），则不能查看任何用户
            if not current_user.department:
                return jsonify({
                    'success': False,
                    'message': '您还没有被分配部门，请联系管理员'
                }), 403
            if user.department != current_user.department:
                return jsonify({
                    'success': False,
                    'message': '您只能查看本部门的用户信息'
                }), 403
        
        return jsonify({
            'success': True,
            'data': user.to_dict()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取用户信息失败: {str(e)}'
        }), 500


@app.route('/api/users/register', methods=['POST'])
def register_user():
    """用户注册（公开接口，不需要权限）"""
    try:
        data = request.get_json()
        
        # 验证必需字段
        required_fields = ['username', 'password', 'real_name']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({
                    'success': False,
                    'message': f'缺少必需字段: {field}'
                }), 400
        
        # 检查用户名是否已存在
        if User.get_by_username(data['username']):
            return jsonify({
                'success': False,
                'message': '用户名已存在'
            }), 400
        
        # 创建用户（注册用户默认为普通用户，部门、职位、工号等为空）
        user = User(
            username=data['username'],
            password=data['password'],
            real_name=data['real_name'],
            email=data.get('email'),
            phone=data.get('phone'),
            department=None,  # 注册时不设置部门
            position=None,    # 注册时不设置职位
            employee_id=None, # 注册时不设置工号
            status=1,         # 默认状态为启用
            role='user'       # 注册用户默认为普通用户
        )
        
        user.save()
        
        return jsonify({
            'success': True,
            'message': '注册成功！请等待管理员为您分配部门和职位',
            'data': user.to_dict()
        }), 201
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'注册失败: {str(e)}'
        }), 500


@app.route('/api/users', methods=['POST'])
@permission_required('admin')
def create_user():
    """创建用户"""
    try:
        data = request.get_json()
        
        # 验证必需字段
        required_fields = ['username', 'password', 'real_name']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({
                    'success': False,
                    'message': f'缺少必需字段: {field}'
                }), 400
        
        # 检查用户名是否已存在
        if User.get_by_username(data['username']):
            return jsonify({
                'success': False,
                'message': '用户名已存在'
            }), 400
        
        # 检查工号是否已存在（如果提供了工号）
        if data.get('employee_id') and User.get_by_employee_id(data['employee_id']):
            return jsonify({
                'success': False,
                'message': '工号已存在'
            }), 400
        
        # 创建用户（根据职位自动设置角色）
        user = User(
            username=data['username'],
            password=data['password'],
            real_name=data['real_name'],
            email=data.get('email'),
            phone=data.get('phone'),
            department=data.get('department'),
            position=data.get('position'),
            employee_id=data.get('employee_id'),
            status=data.get('status', 1),
            role=None  # 角色会根据职位自动设置
        )
        
        user.save()
        
        return jsonify({
            'success': True,
            'message': '用户创建成功',
            'data': user.to_dict()
        }), 201
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'创建用户失败: {str(e)}'
        }), 500


@app.route('/api/users/<int:user_id>', methods=['PUT'])
@permission_required('admin')
def update_user(user_id):
    """更新用户"""
    try:
        user = User.get_by_id(user_id)
        if not user:
            return jsonify({
                'success': False,
                'message': '用户不存在'
            }), 404
        
        # 权限检查：部长只能修改本部门的用户
        current_user = User.get_by_id(session.get('user_id'))
        user_role = session.get('role', 'user')
        if user_role == 'admin' and current_user:
            if user.department != current_user.department:
                return jsonify({
                    'success': False,
                    'message': '您只能修改本部门的用户'
                }), 403
        
        data = request.get_json()
        
        # 更新字段
        if 'real_name' in data:
            user.real_name = data['real_name']
        if 'email' in data:
            user.email = data['email']
        if 'phone' in data:
            user.phone = data['phone']
        if 'department' in data:
            # 权限检查：部长不能修改部门
            if user_role == 'admin':
                return jsonify({
                    'success': False,
                    'message': '您没有权限修改部门'
                }), 403
            user.department = data['department']
        if 'position' in data:
            user.position = data['position']
            # 职位改变时，角色会自动更新
        if 'employee_id' in data:
            # 检查工号是否已被其他用户使用
            existing_user = User.get_by_employee_id(data['employee_id'])
            if existing_user and existing_user.id != user_id:
                return jsonify({
                    'success': False,
                    'message': '工号已被其他用户使用'
                }), 400
            user.employee_id = data['employee_id']
        if 'status' in data:
            # 权限检查：部长不能修改状态
            if user_role == 'admin':
                return jsonify({
                    'success': False,
                    'message': '您没有权限修改用户状态'
                }), 403
            user.status = int(data['status'])
        # 不再允许直接修改角色，角色由职位决定
        if 'password' in data and data['password']:
            user.password = data['password']
        
        user.save()
        
        return jsonify({
            'success': True,
            'message': '用户更新成功',
            'data': user.to_dict()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'更新用户失败: {str(e)}'
        }), 500


@app.route('/api/users/<int:user_id>', methods=['DELETE'])
@permission_required('super_admin')
def delete_user(user_id):
    """删除用户（彻底删除，仅超级管理员可用）"""
    try:
        user = User.get_by_id(user_id)
        if not user:
            return jsonify({
                'success': False,
                'message': '用户不存在'
            }), 404
        
        user.delete()
        
        return jsonify({
            'success': True,
            'message': '用户已彻底删除'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'删除用户失败: {str(e)}'
        }), 500


@app.route('/api/users/<int:user_id>/disable', methods=['POST'])
@permission_required('admin')
def disable_user(user_id):
    """停用用户（设置为禁用状态）"""
    try:
        user = User.get_by_id(user_id)
        if not user:
            return jsonify({
                'success': False,
                'message': '用户不存在'
            }), 404
        
        current_user = User.get_by_id(session.get('user_id'))
        user_role = session.get('role', 'user')
        
        # 管理员只能停用本部门用户
        if user_role == 'admin':
            if not current_user or not current_user.department:
                return jsonify({
                    'success': False,
                    'message': '您还没有被分配部门，无法执行此操作'
                }), 403
            if user.department != current_user.department:
                return jsonify({
                    'success': False,
                    'message': '您只能停用本部门的用户'
                }), 403
        
        if user.status == 0:
            return jsonify({
                'success': False,
                'message': '该用户已是禁用状态'
            }), 400
        
        # 设置状态为禁用
        user.status = 0
        user.password = None  # 避免更新密码字段
        user.save()
        
        return jsonify({
            'success': True,
            'message': '用户已停用'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'停用用户失败: {str(e)}'
        }), 500


@app.route('/api/users/login', methods=['POST'])
def login():
    """用户登录"""
    try:
        data = request.get_json()
        
        if 'username' not in data or 'password' not in data:
            return jsonify({
                'success': False,
                'message': '请提供用户名和密码'
            }), 400
        
        user = User.get_by_username(data['username'])
        if not user:
            return jsonify({
                'success': False,
                'message': '用户名或密码错误'
            }), 401
        
        if user.status == 0:
            return jsonify({
                'success': False,
                'message': '用户已被禁用'
            }), 403
        
        if not User.verify_password(data['password'], user.password):
            return jsonify({
                'success': False,
                'message': '用户名或密码错误'
            }), 401
        
        # 设置 session
        session['user_id'] = user.id
        session['username'] = user.username
        session['real_name'] = user.real_name
        session['role'] = user.role
        
        return jsonify({
            'success': True,
            'message': '登录成功',
            'data': user.to_dict()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'登录失败: {str(e)}'
        }), 500


@app.route('/api/users/current', methods=['GET'])
def get_current_user():
    """获取当前登录用户信息"""
    if 'user_id' not in session:
        return jsonify({
            'success': False,
            'message': '未登录'
        }), 401
    
    user = User.get_by_id(session['user_id'])
    if not user:
        session.clear()
        return jsonify({
            'success': False,
            'message': '用户不存在'
        }), 401
    
    return jsonify({
        'success': True,
        'data': user.to_dict()
    })


@app.route('/api/users/search', methods=['GET'])
@permission_required('view')
def search_users():
    """搜索用户"""
    try:
        keyword = request.args.get('keyword', '')
        if not keyword:
            return jsonify({
                'success': False,
                'message': '请提供搜索关键词'
            }), 400
        
        # 获取当前用户的部门和角色（用于权限过滤）
        current_user = User.get_by_id(session.get('user_id'))
        user_department = current_user.department if current_user else None
        user_role = session.get('role', 'user')
        
        result = User.get_all(
            keyword=keyword, 
            page_size=50,
            user_department=user_department,
            user_role=user_role
        )
        
        return jsonify({
            'success': True,
            'data': {
                'users': [user.to_dict() for user in result['users']],
                'total': result['total']
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'搜索失败: {str(e)}'
        }), 500


@app.errorhandler(404)
def not_found(error):
    """404 错误处理"""
    return jsonify({
        'success': False,
        'message': '请求的资源不存在'
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """500 错误处理"""
    return jsonify({
        'success': False,
        'message': '服务器内部错误'
    }), 500


if __name__ == '__main__':
    # 开发环境运行
    app.run(debug=True, host='0.0.0.0', port=5001)
