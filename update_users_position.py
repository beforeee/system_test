#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
更新现有用户的职位和角色
根据职位自动更新角色
"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from models.user import User
from database import db

def update_users_position():
    """更新所有用户的职位和角色"""
    print("开始更新用户职位和角色...")
    print("=" * 60)
    
    # 获取所有用户
    result = User.get_all(page=1, page_size=1000)
    users = result['users']
    
    updated_count = 0
    
    for user in users:
        try:
            # 如果用户没有职位，根据角色设置职位
            if not user.position:
                if user.role == 'super_admin':
                    user.position = '总经理'
                elif user.role == 'admin':
                    user.position = '部长'
                else:
                    user.position = '员工'
                user.save()
                print(f"✅ 更新用户 {user.username}: 设置职位为 {user.position}")
                updated_count += 1
            # 如果用户有职位，确保角色正确
            elif user.position in ['总经理', '部长', '员工']:
                # 根据职位更新角色
                mapped_role = User.POSITION_ROLE_MAP.get(user.position)
                if mapped_role and user.role != mapped_role:
                    user.role = mapped_role
                    user.save()
                    print(f"✅ 更新用户 {user.username}: 职位 {user.position} -> 角色 {mapped_role}")
                    updated_count += 1
        except Exception as e:
            print(f"❌ 更新用户 {user.username} 失败: {str(e)}")
    
    print("=" * 60)
    print(f"更新完成！共更新 {updated_count} 个用户")


if __name__ == '__main__':
    update_users_position()
