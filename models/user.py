#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
用户模型
"""

import hashlib
import sys
import os
from datetime import datetime

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import db


class User:
    """用户模型类"""
    
    # 职位到角色的映射
    POSITION_ROLE_MAP = {
        '总经理': 'super_admin',
        '部长': 'admin',
        '员工': 'user'
    }
    
    def __init__(self, username=None, password=None, real_name=None, 
                 email=None, phone=None, department=None, position=None,
                 employee_id=None, status=1, role=None, user_id=None):
        self.id = user_id
        self.username = username
        self.password = password
        self.real_name = real_name
        self.email = email
        self.phone = phone
        self.department = department
        self.position = position
        self.employee_id = employee_id
        self.status = status
        
        # 如果提供了职位但没有提供角色，根据职位自动设置角色
        if position and not role:
            self.role = self.POSITION_ROLE_MAP.get(position, 'user')
        elif role:
            self.role = role
        else:
            self.role = 'user'
    
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
            'department': self.department,
            'position': self.position,
            'employee_id': self.employee_id,
            'status': self.status,
            'role': self.role
        }
        if not exclude_password:
            data['password'] = self.password
        return data
    
    def save(self):
        """保存用户（新增或更新）"""
        # 根据职位自动更新角色
        if self.position:
            mapped_role = self.POSITION_ROLE_MAP.get(self.position)
            if mapped_role:
                self.role = mapped_role
        
        if self.id:
            # 更新
            sql = """
            UPDATE users SET 
                username=%s, real_name=%s, email=%s, phone=%s,
                department=%s, position=%s, employee_id=%s,
                status=%s, role=%s
            WHERE id=%s
            """
            params = (
                self.username, self.real_name, self.email, self.phone,
                self.department, self.position, self.employee_id,
                self.status, self.role, self.id
            )
            if self.password:
                sql = """
                UPDATE users SET 
                    username=%s, password=%s, real_name=%s, email=%s, phone=%s,
                    department=%s, position=%s, employee_id=%s,
                    status=%s, role=%s
                WHERE id=%s
                """
                params = (
                    self.username, User.hash_password(self.password),
                    self.real_name, self.email, self.phone,
                    self.department, self.position, self.employee_id,
                    self.status, self.role, self.id
                )
            db.execute_update(sql, params)
        else:
            # 新增
            if not self.password:
                raise ValueError("新用户必须设置密码")
            
            sql = """
            INSERT INTO users 
            (username, password, real_name, email, phone, department, position, employee_id, status, role)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            params = (
                self.username, User.hash_password(self.password),
                self.real_name, self.email, self.phone,
                self.department, self.position, self.employee_id,
                self.status, self.role
            )
            db.execute_update(sql, params)
            # 获取新插入的ID
            result = db.execute_query("SELECT LAST_INSERT_ID() as id")
            if result:
                self.id = result[0]['id']
    
    @staticmethod
    def get_by_id(user_id):
        """根据ID获取用户"""
        sql = "SELECT * FROM users WHERE id=%s"
        result = db.execute_query(sql, (user_id,))
        if result:
            return User._from_dict(result[0])
        return None
    
    @staticmethod
    def get_by_username(username):
        """根据用户名获取用户"""
        sql = "SELECT * FROM users WHERE username=%s"
        result = db.execute_query(sql, (username,))
        if result:
            return User._from_dict(result[0])
        return None
    
    @staticmethod
    def get_by_employee_id(employee_id):
        """根据工号获取用户"""
        sql = "SELECT * FROM users WHERE employee_id=%s"
        result = db.execute_query(sql, (employee_id,))
        if result:
            return User._from_dict(result[0])
        return None
    
    @staticmethod
    def get_all(page=1, page_size=20, status=None, department=None, keyword=None, user_department=None, user_role='user'):
        """获取用户列表（分页，支持部门和角色过滤）"""
        where_clauses = []
        params = []
        
        if status is not None:
            where_clauses.append("status=%s")
            params.append(status)
        
        if department:
            where_clauses.append("department=%s")
            params.append(department)
        
        if keyword:
            where_clauses.append("(username LIKE %s OR real_name LIKE %s OR employee_id LIKE %s)")
            keyword_pattern = f"%{keyword}%"
            params.extend([keyword_pattern, keyword_pattern, keyword_pattern])
        
        # 基于部门的权限过滤：管理员和普通用户只能查看本部门的用户
        # 如果用户没有部门（注册用户），则看不到任何用户
        if user_role in ['admin', 'user']:
            if user_department:
                where_clauses.append("department=%s")
                params.append(user_department)
            else:
                # 没有部门的用户（注册用户）看不到任何用户
                where_clauses.append("1=0")  # 永远不匹配任何记录
        
        where_sql = " WHERE " + " AND ".join(where_clauses) if where_clauses else ""
        
        # 获取总数
        count_sql = f"SELECT COUNT(*) as total FROM users {where_sql}"
        total_result = db.execute_query(count_sql, params)
        total = total_result[0]['total'] if total_result else 0
        
        # 获取分页数据
        offset = (page - 1) * page_size
        sql = f"""
        SELECT id, username, real_name, email, phone, department, position, 
               employee_id, status, role, created_at, updated_at
        FROM users {where_sql}
        ORDER BY id DESC
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
        user = User(
            user_id=data.get('id'),
            username=data.get('username'),
            password=data.get('password'),
            real_name=data.get('real_name'),
            email=data.get('email'),
            phone=data.get('phone'),
            department=data.get('department'),
            position=data.get('position'),
            employee_id=data.get('employee_id'),
            status=data.get('status'),
            role=data.get('role')
        )
        return user
