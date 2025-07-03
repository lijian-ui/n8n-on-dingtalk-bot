#!/usr/bin/env python3
"""
钉钉AI机器人快速启动脚本
包含配置检查和初始化功能
"""

import os
import sys
import subprocess
from pathlib import Path

def check_python_version():
    """检查Python版本"""
    if sys.version_info < (3, 8):
        print("❌ 错误: 需要Python 3.8或更高版本")
        print(f"当前版本: {sys.version}")
        return False
    print(f"✅ Python版本检查通过: {sys.version.split()[0]}")
    return True

def check_dependencies():
    """检查依赖包"""
    try:
        import dingtalk_stream
        import alibabacloud_dingtalk
        import requests
        import aiohttp
        print("✅ 依赖包检查通过")
        return True
    except ImportError as e:
        print(f"❌ 缺少依赖包: {e}")
        print("请运行: pip install -r requirements.txt")
        return False

def check_env_file():
    """检查环境变量文件"""
    env_file = Path(".env")
    if not env_file.exists():
        print("⚠️  未找到 .env 文件")
        print("请复制 env.example 为 .env 并填写配置")
        return False
    
    print("✅ 找到 .env 文件")
    return True

def check_config():
    """检查配置"""
    try:
        from config import Config
        Config.validate()
        print("✅ 配置验证通过")
        return True
    except Exception as e:
        print(f"❌ 配置错误: {e}")
        return False

def install_dependencies():
    """安装依赖"""
    print("正在安装依赖包...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                      check=True, capture_output=True, text=True)
        print("✅ 依赖包安装完成")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 依赖包安装失败: {e}")
        return False

def main():
    """主函数"""
    print("🚀 钉钉AI机器人启动检查")
    print("=" * 50)
    
    # 检查Python版本
    if not check_python_version():
        sys.exit(1)
    
    # 检查依赖包
    if not check_dependencies():
        print("\n是否要自动安装依赖包? (y/n): ", end="")
        if input().lower() == 'y':
            if not install_dependencies():
                sys.exit(1)
        else:
            sys.exit(1)
    
    # 检查环境变量文件
    if not check_env_file():
        print("\n请按照以下步骤配置:")
        print("1. 复制 env.example 为 .env")
        print("2. 编辑 .env 文件，填写钉钉应用配置")
        print("3. 配置n8n webhook地址")
        sys.exit(1)
    
    # 检查配置
    if not check_config():
        print("\n请检查 .env 文件中的配置是否正确")
        sys.exit(1)
    
    print("\n" + "=" * 50)
    print("✅ 所有检查通过，启动机器人...")
    print("按 Ctrl+C 停止程序")
    print("=" * 50)
    
    # 启动主程序
    try:
        from main import main as start_bot
        start_bot()
    except KeyboardInterrupt:
        print("\n👋 程序已停止")
    except Exception as e:
        print(f"\n❌ 程序运行异常: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main() 