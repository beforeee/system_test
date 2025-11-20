#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
用户模型
"""

import hashlib
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import db


class User:
    """用户模型类"""
    
    def __init__(self, username=None, password=None, real_name=None, 
                 email=None, phone=None, department_id=None, position_id=None,
                 employee_id=None, status=1, role='user', user_id=None,
                 department_name=None, position_name=None):
        self.id = user_id
        self.username = username
        self.password = password
        self.real_name = real_name
        self.email = email
        self.phone = phone
        self.department_id = department_id
        self.position_id = position_id
        self.employee_id = employee_id
        self.status = status
        self.role = role or 'user'
        self.department = department_name
        self.position = position_name
    
    @staticmethod
    def hash_password(password):
        """密码加密"""
        return hashlib.sha256(password.encode('utf-8')).hexdigest()
    
    @staticmethod
    def verify_password(password, hashed):
        """验证密码"""
        return User.hash_password(password) == hashed
    
    def to_dict(self, exclude_password=True):
        """转换为字典"""
        data = {
            'id': self.id,
            'username': self.username,
            'real_name': self.real_name,
            'email': self.email,
            'phone': self.phone,
            'department_id': self.department_id,
            'position_id': self.position_id,
            'department': getattr(self, 'department', None),
            'position': getattr(self, 'position', None),
            'employee_id': self.employee_id,
            'status': self.status,
            'role': self.role
        }
        if not exclude_password:
            data['password'] = self.password
        return data
    
    def save(self):
        """保存用户（新增或更新）"""
        # 如果提供了position_id，根据职位更新角色
        if self.position_id:
            from models.position import Position
            pos = Position.get_by_id(self.position_id)
            if pos:
                self.role = pos.role
        
        if self.id:
            # 更新
            sql = """
            UPDATE users SET 
                username=%s, real_name=%s, email=%s, phone=%s,
                department_id=%s, position_id=%s, employee_id=%s,
                status=%s, role=%s
            WHERE id=%s
            """
            params = (
                self.username, self.real_name, self.email, self.phone,
                self.department_id, self.position_id, self.employee_id,
                self.status, self.role, self.id
            )
            if self.password:
                sql = """
                UPDATE users SET 
                    username=%s, password=%s, real_name=%s, email=%s, phone=%s,
                    department_id=%s, position_id=%s, employee_id=%s,
                    status=%s, role=%s
                WHERE id=%s
                """
                params = (
                    self.username, User.hash_password(self.password),
                    self.real_name, self.email, self.phone,
                    self.department_id, self.position_id, self.employee_id,
                    self.status, self.role, self.id
                )
            db.execute_update(sql, params)
        else:
            # 新增
            if not self.password:
                raise ValueError("新用户必须设置密码")
            
            sql = """
            INSERT INTO users 
            (username, password, real_name, email, phone, department_id, position_id, employee_id, status, role)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            params = (
                self.username, User.hash_password(self.password),
                self.real_name, self.email, self.phone,
                self.department_id, self.position_id, self.employee_id,
                self.status, self.role
            )
            db.execute_update(sql, params)
            # 获取新插入的ID
            result = db.execute_query("SELECT LAST_INSERT_ID() as id")
            if result:
                self.id = result[0]['id']
    
    @staticmethod
    def get_by_id(user_id):
        """根据ID获取用户（带关联查询）"""
        sql = """
        SELECT u.*, d.name as department_name, p.name as position_name, p.role as position_role
        FROM users u
        LEFT JOIN departments d ON u.department_id = d.id
        LEFT JOIN positions p ON u.position_id = p.id
        WHERE u.id=%s
        """
        result = db.execute_query(sql, (user_id,))
        if result:
            return User._from_dict(result[0])
        return None
    
    @staticmethod
    def get_by_username(username):
        """根据用户名获取用户（带关联查询）"""
        sql = """
        SELECT u.*, d.name as department_name, p.name as position_name, p.role as position_role
        FROM users u
        LEFT JOIN departments d ON u.department_id = d.id
        LEFT JOIN positions p ON u.position_id = p.id
        WHERE u.username=%s
        """
        result = db.execute_query(sql, (username,))
        if result:
            return User._from_dict(result[0])
        return None
    
    @staticmethod
    def get_by_employee_id(employee_id):
        """根据工号获取用户（带关联查询）"""
        sql = """
        SELECT u.*, d.name as department_name, p.name as position_name, p.role as position_role
        FROM users u
        LEFT JOIN departments d ON u.department_id = d.id
        LEFT JOIN positions p ON u.position_id = p.id
        WHERE u.employee_id=%s
        """
        result = db.execute_query(sql, (employee_id,))
        if result:
            return User._from_dict(result[0])
        return None
    
    @staticmethod
    def get_all(page=1, page_size=20, status=None, department_id=None, keyword=None, user_department_id=None, user_role='user'):
        """获取用户列表（分页，支持部门和角色过滤，带关联查询）"""
        where_clauses = []
        params = []
        
        if status is not None:
            where_clauses.append("u.status=%s")
            params.append(status)
        
        if department_id:
            where_clauses.append("u.department_id=%s")
            params.append(department_id)
        
        if keyword:
            where_clauses.append("(u.username LIKE %s OR u.real_name LIKE %s OR u.employee_id LIKE %s)")
            keyword_pattern = f"%{keyword}%"
            params.extend([keyword_pattern, keyword_pattern, keyword_pattern])
        
        # 基于部门的权限过滤：管理员和普通用户只能查看本部门的用户
        if user_role in ['admin', 'user']:
            if user_department_id:
                where_clauses.append("u.department_id=%s")
                params.append(user_department_id)
            else:
                # 没有部门的用户（注册用户）看不到任何用户
                where_clauses.append("1=0")  # 永远不匹配任何记录
        
        where_sql = " WHERE " + " AND ".join(where_clauses) if where_clauses else ""
        
        # 获取总数
        count_sql = f"""
        SELECT COUNT(*) as total 
        FROM users u {where_sql}
        """
        total_result = db.execute_query(count_sql, params)
        total = total_result[0]['total'] if total_result else 0
        
        # 获取分页数据
        offset = (page - 1) * page_size
        sql = f"""
        SELECT u.id, u.username, u.real_name, u.email, u.phone, 
               u.department_id, u.position_id, u.employee_id, u.status, u.role,
               u.created_at, u.updated_at,
               d.name as department_name, p.name as position_name, p.role as position_role
        FROM users u
        LEFT JOIN departments d ON u.department_id = d.id
        LEFT JOIN positions p ON u.position_id = p.id
        {where_sql}
        ORDER BY u.id DESC
        LIMIT %s OFFSET %s
        """
        params.extend([page_size, offset])
        result = db.execute_query(sql, params)
        
        users = [User._from_dict(row) for row in result]
        return {
            'users': users,
            'total': total,
            'page': page,
            'page_size': page_size,
            'total_pages': (total + page_size - 1) // page_size
        }
    
    def delete(self):
        """删除用户（彻底删除，从数据库中删除记录）"""
        sql = "DELETE FROM users WHERE id=%s"
        db.execute_update(sql, (self.id,))
    
    @staticmethod
    def _from_dict(data):
        """从字典创建用户对象"""
        return User(
            user_id=data.get('id'),
            username=data.get('username'),
            password=data.get('password'),
            real_name=data.get('real_name'),
            email=data.get('email'),
            phone=data.get('phone'),
            department_id=data.get('department_id'),
            position_id=data.get('position_id'),
            employee_id=data.get('employee_id'),
            status=data.get('status'),
            role=data.get('role') or data.get('position_role'),
            department_name=data.get('department_name'),
            position_name=data.get('position_name')
        )
