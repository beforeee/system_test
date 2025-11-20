#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
创建测试用户账号
职位与角色自动关联：总经理→超级管理员，部长→管理员，员工→普通用户
"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from models.user import User

# 测试用户数据
test_users = [
    # 总经理（超级管理员）
    {
        'username': 'superadmin',
        'password': '123456',
        'real_name': '张总经理',
        'email': 'superadmin@example.com',
        'phone': '13800000001',
        'department': '综合部',
        'position': '总经理',
        'employee_id': 'E001',
        'status': 1
    },
    # 部长（管理员）- 综合部
    {
        'username': 'admin_zh',
        'password': '123456',
        'real_name': '李部长',
        'email': 'admin_zh@example.com',
        'phone': '13800000002',
        'department': '综合部',
        'position': '部长',
        'employee_id': 'E002',
        'status': 1
    },
    # 部长（管理员）- 船务部
    {
        'username': 'admin_cw',
        'password': '123456',
        'real_name': '王部长',
        'email': 'admin_cw@example.com',
        'phone': '13800000003',
        'department': '船务部',
        'position': '部长',
        'employee_id': 'E003',
        'status': 1
    },
    # 员工（普通用户）- 综合部
    {
        'username': 'user_zh1',
        'password': '123456',
        'real_name': '赵小明',
        'email': 'user_zh1@example.com',
        'phone': '13800000004',
        'department': '综合部',
        'position': '员工',
        'employee_id': 'E004',
        'status': 1
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
        'status': 1
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
        'status': 1
    },
    # 员工（普通用户）- 船务部
    {
        'username': 'user_cw1',
        'password': '123456',
        'real_name': '周小丽',
        'email': 'user_cw1@example.com',
        'phone': '13800000007',
        'department': '船务部',
        'position': '员工',
        'employee_id': 'E007',
        'status': 1
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
        'status': 1
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
        'status': 1
    }
]


def create_users():
    """创建测试用户"""
    print("开始创建测试用户...")
    print("=" * 60)
    
    success_count = 0
    error_count = 0
    
    for user_data in test_users:
        try:
            # 检查用户是否已存在
            existing_user = User.get_by_username(user_data['username'])
            if existing_user:
                print(f"⚠️  用户 {user_data['username']} 已存在，跳过")
                continue
            
            # 创建用户（不指定role，由position自动设置）
            user = User(
                username=user_data['username'],
                password=user_data['password'],
                real_name=user_data['real_name'],
                email=user_data['email'],
                phone=user_data['phone'],
                department=user_data['department'],
                position=user_data['position'],
                employee_id=user_data['employee_id'],
                status=user_data['status'],
                role=None  # 角色由职位自动设置
            )
            
            user.save()
            
            role_name = {
                'super_admin': '超级管理员',
                'admin': '管理员',
                'user': '普通用户'
            }.get(user.role, user.role)
            
            print(f"✅ 创建成功: {user_data['username']} ({user_data['real_name']}) - {user_data['position']} - {role_name} - {user_data['department']}")
            success_count += 1
            
        except Exception as e:
            print(f"❌ 创建失败: {user_data['username']} - {str(e)}")
            error_count += 1
    
    print("=" * 60)
    print(f"创建完成！成功: {success_count} 个，失败: {error_count} 个")
    print("\n测试账号信息：")
    print("-" * 60)
    print(f"{'用户名':<15} {'密码':<10} {'职位':<8} {'角色':<10} {'部门':<8}")
    print("-" * 60)
    for user_data in test_users:
        position = user_data['position']
        role_map = {
            '总经理': '超级管理员',
            '部长': '管理员',
            '员工': '普通用户'
        }
        role_name = role_map.get(position, '普通用户')
        print(f"{user_data['username']:<15} {'123456':<10} {position:<8} {role_name:<10} {user_data['department']:<8}")


if __name__ == '__main__':
    create_users()