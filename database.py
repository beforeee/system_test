#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库连接模块
"""

import json
import pymysql
from pymysql.cursors import DictCursor
from contextlib import contextmanager

DEFAULT_DEPARTMENTS = [
    ('综合部', '综合管理部门'),
    ('船务部', '船务与运营部门')
]

DEFAULT_POSITIONS = [
    ('总经理', 'super_admin', '公司总经理'),
    ('部长', 'admin', '部门负责人'),
    ('部门管理员', 'admin', '部门管理人员'),
    ('员工', 'user', '普通员工')
]


class DatabaseConfig:
    """数据库配置类"""
    
    def __init__(self, config_file='config.json'):
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
            db_config = config.get('database', {})
            
        self.host = db_config.get('host', 'localhost')
        self.port = db_config.get('port', 3306)
        self.username = db_config.get('username', 'root')
        self.password = db_config.get('password', '')
        self.database = db_config.get('database', 'salary_management')
        self.charset = db_config.get('charset', 'utf8mb4')
        self.connection_timeout = db_config.get('connection_timeout', 30)
    
    def get_connection_params(self):
        """获取数据库连接参数"""
        return {
            'host': self.host,
            'port': self.port,
            'user': self.username,
            'password': self.password,
            'database': self.database,
            'charset': self.charset,
            'connect_timeout': self.connection_timeout,
            'cursorclass': DictCursor
        }


class Database:
    """数据库操作类"""
    
    def __init__(self, config_file='config.json'):
        self.config = DatabaseConfig(config_file)
        self._init_database()
    
    def _init_database(self):
        """初始化数据库（如果不存在则创建）"""
        try:
            # 先连接不指定数据库
            params = self.config.get_connection_params()
            database_name = params.pop('database')
            
            conn = pymysql.connect(**params)
            cursor = conn.cursor()
            
            # 创建数据库（如果不存在）
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{database_name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            conn.commit()
            cursor.close()
            conn.close()
            
            # 重新连接指定数据库
            params['database'] = database_name
            conn = pymysql.connect(**params)
            cursor = conn.cursor()
            
            # 创建基础表（先创建部门表和职位表）
            self._create_department_table(cursor)
            self._create_position_table(cursor)
            # 创建用户表（依赖部门和职位表）
            self._create_user_table(cursor)
            self._seed_reference_data(cursor)
            conn.commit()
            cursor.close()
            conn.close()
            
        except Exception as e:
            print(f"数据库初始化错误: {e}")
            raise
    
    def _create_department_table(self, cursor):
        """创建部门表"""
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS `departments` (
            `id` INT AUTO_INCREMENT PRIMARY KEY,
            `name` VARCHAR(100) NOT NULL UNIQUE COMMENT '部门名称',
            `description` VARCHAR(255) COMMENT '部门描述',
            `status` TINYINT DEFAULT 1 COMMENT '状态：1-启用，0-禁用',
            `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
            `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
            INDEX `idx_name` (`name`),
            INDEX `idx_status` (`status`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='部门表';
        """
        cursor.execute(create_table_sql)
    
    def _create_position_table(self, cursor):
        """创建职位表"""
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS `positions` (
            `id` INT AUTO_INCREMENT PRIMARY KEY,
            `name` VARCHAR(100) NOT NULL UNIQUE COMMENT '职位名称',
            `role` VARCHAR(20) NOT NULL COMMENT '对应角色：super_admin-超级管理员，admin-管理员，user-普通用户',
            `description` VARCHAR(255) COMMENT '职位描述',
            `status` TINYINT DEFAULT 1 COMMENT '状态：1-启用，0-禁用',
            `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
            `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
            INDEX `idx_name` (`name`),
            INDEX `idx_role` (`role`),
            INDEX `idx_status` (`status`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='职位表';
        """
        cursor.execute(create_table_sql)
    
    def _create_user_table(self, cursor):
        """创建用户表"""
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS `users` (
            `id` INT AUTO_INCREMENT PRIMARY KEY,
            `username` VARCHAR(50) NOT NULL UNIQUE COMMENT '用户名',
            `password` VARCHAR(255) NOT NULL COMMENT '密码（加密）',
            `real_name` VARCHAR(50) NOT NULL COMMENT '真实姓名',
            `email` VARCHAR(100) COMMENT '邮箱',
            `phone` VARCHAR(20) COMMENT '手机号',
            `department_id` INT COMMENT '部门ID（外键关联departments表）',
            `position_id` INT COMMENT '职位ID（外键关联positions表）',
            `employee_id` VARCHAR(50) UNIQUE COMMENT '工号',
            `status` TINYINT DEFAULT 1 COMMENT '状态：1-启用，0-禁用',
            `role` VARCHAR(20) DEFAULT 'user' COMMENT '角色：super_admin-超级管理员，admin-管理员，user-普通用户',
            `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
            `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
            INDEX `idx_username` (`username`),
            INDEX `idx_employee_id` (`employee_id`),
            INDEX `idx_status` (`status`),
            INDEX `idx_department_id` (`department_id`),
            INDEX `idx_position_id` (`position_id`),
            FOREIGN KEY (`department_id`) REFERENCES `departments`(`id`) ON DELETE SET NULL,
            FOREIGN KEY (`position_id`) REFERENCES `positions`(`id`) ON DELETE SET NULL
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户表';
        """
        cursor.execute(create_table_sql)
    
    def _seed_reference_data(self, cursor):
        """初始化基础数据"""
        for name, description in DEFAULT_DEPARTMENTS:
            cursor.execute(
                "INSERT IGNORE INTO departments (name, description, status) VALUES (%s, %s, 1)",
                (name, description)
            )
        
        for name, role, description in DEFAULT_POSITIONS:
            cursor.execute(
                "INSERT IGNORE INTO positions (name, role, description, status) VALUES (%s, %s, %s, 1)",
                (name, role, description)
            )
    
    @contextmanager
    def get_connection(self):
        """获取数据库连接的上下文管理器"""
        conn = None
        try:
            conn = pymysql.connect(**self.config.get_connection_params())
            yield conn
            conn.commit()
        except Exception as e:
            if conn:
                conn.rollback()
            raise e
        finally:
            if conn:
                conn.close()
    
    def execute_query(self, sql, params=None):
        """执行查询语句"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, params)
            result = cursor.fetchall()
            cursor.close()
            return result
    
    def execute_update(self, sql, params=None):
        """执行更新语句"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, params)
            affected_rows = cursor.rowcount
            cursor.close()
            return affected_rows


# 全局数据库实例
db = Database()
