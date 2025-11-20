#!/bin/bash
# 薪酬计算管理系统启动脚本

PYTHON=${PYTHON:-python3}

# 检查 Python 是否可用
if ! command -v $PYTHON &> /dev/null; then
    echo "错误: 找不到 Python 解释器: $PYTHON"
    echo "请设置 PYTHON 环境变量指定 Python 路径"
    exit 1
fi

echo "使用 Python 解释器: $($PYTHON --version)"
echo "Python 路径: $(which $PYTHON)"
echo ""

# 检查依赖是否安装
if ! $PYTHON -c "import flask" 2>/dev/null; then
    echo "Flask 未安装，正在安装依赖..."
    $PYTHON -m pip install -r requirements.txt
    echo ""
fi

if ! $PYTHON -c "import pymysql" 2>/dev/null; then
    echo "PyMySQL 未安装，正在安装依赖..."
    $PYTHON -m pip install -r requirements.txt
    echo ""
fi

# 初始化数据库
echo "检查数据库连接..."
$PYTHON init_db.py
echo ""

# 启动 Flask 应用
echo "启动薪酬计算管理系统..."
echo "访问地址: http://localhost:5000"
echo "按 Ctrl+C 停止服务"
echo ""
$PYTHON app.py
