FROM python:3.12-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
#RUN apt-get update && apt-get install -y \
#    gcc \
#    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/

# 复制应用代码
COPY . .

# 创建日志目录
RUN mkdir -p /app/logs

# 设置环境变量
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# 暴露端口（如果需要HTTP服务）
# EXPOSE 8000

# 启动命令
CMD ["python", "main.py"] 
