#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
部门模型
"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import db


class Department:
    """部门模型类"""
    
    def __init__(self, name=None, description=None, status=1, department_id=None):
        self.id = department_id
        self.name = name
        self.description = description
        self.status = status
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'status': self.status
        }
    
    def save(self):
        """保存部门（新增或更新）"""
        if self.id:
            # 更新
            sql = """
            UPDATE departments SET 
                name=%s, description=%s, status=%s
            WHERE id=%s
            """
            params = (self.name, self.description, self.status, self.id)
            db.execute_update(sql, params)
        else:
            # 新增
            sql = """
            INSERT INTO departments 
            (name, description, status)
            VALUES (%s, %s, %s)
            """
            params = (self.name, self.description, self.status)
            db.execute_update(sql, params)
            # 获取新插入的ID
            result = db.execute_query("SELECT LAST_INSERT_ID() as id")
            if result:
                self.id = result[0]['id']
    
    @staticmethod
    def get_by_id(department_id):
        """根据ID获取部门"""
        sql = "SELECT * FROM departments WHERE id=%s"
        result = db.execute_query(sql, (department_id,))
        if result:
            return Department._from_dict(result[0])
        return None
    
    @staticmethod
    def get_by_name(name):
        """根据名称获取部门"""
        sql = "SELECT * FROM departments WHERE name=%s"
        result = db.execute_query(sql, (name,))
        if result:
            return Department._from_dict(result[0])
        return None
    
    @staticmethod
    def get_all(status=None):
        """获取所有部门列表"""
        where_clauses = []
        params = []
        
        if status is not None:
            where_clauses.append("status=%s")
            params.append(status)
        
        where_sql = " WHERE " + " AND ".join(where_clauses) if where_clauses else ""
        
        sql = f"""
        SELECT * FROM departments {where_sql}
        ORDER BY id ASC
        """
        result = db.execute_query(sql, params)
        return [Department._from_dict(row) for row in result]
    
    def delete(self):
        """删除部门（软删除，设置为禁用）"""
        self.status = 0
        self.save()
    
    @staticmethod
    def _from_dict(data):
        """从字典创建部门对象"""
        return Department(
            department_id=data.get('id'),
            name=data.get('name'),
            description=data.get('description'),
            status=data.get('status', 1)
        )

