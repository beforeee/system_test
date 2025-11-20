#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库初始化脚本
"""

from database import Database

if __name__ == '__main__':
    print("正在初始化数据库...")
    try:
        db = Database()
        print("数据库初始化成功！")
        print("用户表已创建")
    except Exception as e:
        print(f"数据库初始化失败: {e}")
        import traceback
        traceback.print_exc()
