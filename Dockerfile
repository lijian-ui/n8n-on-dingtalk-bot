FROM python:3.11-slim

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

# 设置环境变量
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1



# 启动命令
CMD ["python", "main.py"] 
