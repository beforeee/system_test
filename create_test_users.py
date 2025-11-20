#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
创建测试数据：部门、职位、用户
"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from models.user import User
from models.department import Department
from models.position import Position

DEFAULT_DEPARTMENTS = [
    {'name': '综合部', 'description': '综合管理部门'},
    {'name': '船务部', 'description': '船务与运营部门'}
]

DEFAULT_POSITIONS = [
    {'name': '总经理', 'role': 'super_admin', 'description': '公司总经理'},
    {'name': '部长', 'role': 'admin', 'description': '部门负责人'},
    {'name': '部门管理员', 'role': 'admin', 'description': '部门管理人员'},
    {'name': '员工', 'role': 'user', 'description': '普通员工'}
]

# 测试用户数据
TEST_USERS = [
    {
        'username': 'superadmin',
        'password': '123456',
        'real_name': '张总经理',
        'email': 'superadmin@example.com',
        'phone': '13800000001',
        'department': '综合部',
        'position': '总经理',
        'employee_id': 'E001',
        'status': 1,
    },
    {
        'username': 'admin_zh',
        'password': '123456',
        'real_name': '李部长',
        'email': 'admin_zh@example.com',
        'phone': '13800000002',
        'department': '综合部',
        'position': '部长',
        'employee_id': 'E002',
        'status': 1,
    },
    {
        'username': 'admin_cw',
        'password': '123456',
        'real_name': '王部长',
        'email': 'admin_cw@example.com',
        'phone': '13800000003',
        'department': '船务部',
        'position': '部长',
        'employee_id': 'E003',
        'status': 1,
    },
    {
        'username': 'user_zh1',
        'password': '123456',
        'real_name': '赵小明',
        'email': 'user_zh1@example.com',
        'phone': '13800000004',
        'department': '综合部',
        'position': '员工',
        'employee_id': 'E004',
        'status': 1,
    },
    {
        'username': 'user_zh2',
        'password': '123456',
        'real_name': '钱小红',
        'email': 'user_zh2@example.com',
        'phone': '13800000005',
        'department': '综合部',
        'position': '员工',
        'employee_id': 'E005',
        'status': 1,
    },
    {
        'username': 'user_zh3',
        'password': '123456',
        'real_name': '孙小刚',
        'email': 'user_zh3@example.com',
        'phone': '13800000006',
        'department': '综合部',
        'position': '员工',
        'employee_id': 'E010',
        'status': 1,
    },
    {
        'username': 'user_cw1',
        'password': '123456',
        'real_name': '周小丽',
        'email': 'user_cw1@example.com',
        'phone': '13800000007',
        'department': '船务部',
        'position': '员工',
        'employee_id': 'E007',
        'status': 1,
    },
    {
        'username': 'user_cw2',
        'password': '123456',
        'real_name': '吴小强',
        'email': 'user_cw2@example.com',
        'phone': '13800000008',
        'department': '船务部',
        'position': '员工',
        'employee_id': 'E008',
        'status': 1,
    },
    {
        'username': 'user_cw3',
        'password': '123456',
        'real_name': '郑小美',
        'email': 'user_cw3@example.com',
        'phone': '13800000009',
        'department': '船务部',
        'position': '员工',
        'employee_id': 'E009',
        'status': 1,
    },
]


def ensure_departments():
    mapping = {}
    for item in DEFAULT_DEPARTMENTS:
        dept = Department.get_by_name(item['name'])
        if not dept:
            dept = Department(name=item['name'], description=item['description'])
            dept.save()
            print(f"✓ 新增部门 {item['name']}")
        mapping[item['name']] = dept.id
    return mapping


def ensure_positions():
    mapping = {}
    for item in DEFAULT_POSITIONS:
        pos = Position.get_by_name(item['name'])
        if not pos:
            pos = Position(name=item['name'], role=item['role'], description=item['description'])
            pos.save()
            print(f"✓ 新增职位 {item['name']} -> {item['role']}")
        mapping[item['name']] = pos.id
    return mapping


def create_users():
    """创建测试用户"""
    print("开始创建测试数据...")
    print("=" * 60)
    
    department_map = ensure_departments()
    position_map = ensure_positions()
    
    success_count = 0
    error_count = 0
    
    for user_data in TEST_USERS:
        try:
            existing_user = User.get_by_username(user_data['username'])
            if existing_user:
                print(f"⚠️ 用户 {user_data['username']} 已存在，跳过")
                continue
            
            dept_id = department_map.get(user_data['department'])
            pos_id = position_map.get(user_data['position'])
            
            if not dept_id or not pos_id:
                print(f"⚠️ 用户 {user_data['username']} 所需的部门或职位不存在，跳过")
                continue
            
            user = User(
                username=user_data['username'],
                password=user_data['password'],
                real_name=user_data['real_name'],
                email=user_data['email'],
                phone=user_data['phone'],
                department_id=dept_id,
                position_id=pos_id,
                employee_id=user_data['employee_id'],
                status=user_data.get('status', 1),
                role=None
            )
            
            user.save()
            print(f"✅ 创建成功: {user.username} / {user.real_name} / {user.position}")
            success_count += 1
        except Exception as e:
            print(f"❌ 创建失败: {user_data['username']} - {str(e)}")
            error_count += 1
    
    print("=" * 60)
    print(f"创建完成！成功: {success_count} 个，失败: {error_count} 个")
    print("\n测试账号信息：")
    print("-" * 60)
    print(f"{'用户名':<15} {'密码':<10} {'职位':<10} {'部门':<10}")
    print("-" * 60)
    for user_data in TEST_USERS:
        print(f"{user_data['username']:<15} {'123456':<10} {user_data['position']:<10} {user_data['department']:<10}")


if __name__ == '__main__':
    create_users()