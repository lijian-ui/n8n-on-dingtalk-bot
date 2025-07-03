# 钉钉AI机器人

一个基于钉钉流式API的AI聊天机器人，支持接收钉钉群消息并通过n8n Webhook获取AI回复。

## 功能特性

- 🤖 自动接收钉钉群消息
- 🔄 调用n8n Webhook获取AI回复
- 📝 发送格式化的Markdown消息到钉钉群
- 🔐 支持Token缓存和自动刷新
- 📊 完整的日志记录
- ⚡ 异步处理，高性能响应

## 项目结构

```
dingtalk-ai-bot/
├── config.py                 # 配置管理
├── main.py                   # 主程序入口
├── requirements.txt          # 依赖包列表
├── env.example              # 环境变量示例
├── README.md                # 项目说明
├── utils/                   # 工具模块
│   ├── __init__.py
│   └── token_manager.py     # Token管理器
├── services/                # 服务模块
│   ├── __init__.py
│   ├── ai_service.py        # AI服务
│   └── dingtalk_service.py  # 钉钉服务
└── handlers/                # 处理器模块
    ├── __init__.py
    └── chatbot_handler.py   # 聊天机器人处理器
```

## 安装和配置

### 1. 克隆项目

```bash
git clone <repository-url>
cd dingtalk-ai-bot
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置环境变量

复制 `env.example` 为 `.env` 并填写配置：

```bash
cp env.example .env
```

编辑 `.env` 文件：

```env
# 钉钉应用配置
DINGTALK_CLIENT_ID=your_app_key_here
DINGTALK_CLIENT_SECRET=your_app_secret_here
DINGTALK_ROBOT_CODE=your_robot_code_here

# n8n Webhook配置
N8N_WEBHOOK_URL=https://your-n8n-instance.com/webhook/your-webhook-id
N8N_API_KEY=your_n8n_api_key_here

# 机器人配置
BOT_NAME=AI助手
MAX_MESSAGE_LENGTH=2000

# 日志配置
LOG_LEVEL=INFO
```

### 4. 获取钉钉应用配置

1. 访问 [钉钉开放平台](https://open-dev.dingtalk.com)
2. 创建企业内部应用
3. 获取 AppKey 和 AppSecret
4. 在机器人管理页面获取 RobotCode
5. 配置机器人权限和回调地址

### 5. 配置n8n Webhook

在n8n中创建一个Webhook节点，配置接收以下格式的数据：

```json
{
  "message": "用户消息内容",
  "user_id": "用户ID",
  "conversation_id": "会话ID",
  "timestamp": 1234567890
}
```

n8n应该返回以下格式的响应：

```json
{
  "response": "AI回复内容"
}
```

## 运行

```bash
python main.py
```

程序启动后会：
1. 验证配置
2. 连接钉钉流式API
3. 开始监听群消息
4. 自动处理@机器人的消息

## 使用方式

在钉钉群中@机器人并发送消息，机器人会：

1. 接收您的消息
2. 调用n8n Webhook获取AI回复
3. 以Markdown格式发送回复到群中

## 日志

程序会生成详细的日志文件 `dingtalk_ai_bot.log`，包含：
- 消息接收记录
- AI调用状态
- 错误信息
- 系统运行状态

## 故障排除

### 常见问题

1. **配置错误**
   - 检查 `.env` 文件中的配置是否正确
   - 确保钉钉应用权限配置正确

2. **Token获取失败**
   - 检查 AppKey 和 AppSecret 是否正确
   - 确认网络连接正常

3. **AI回复失败**
   - 检查 n8n Webhook URL 是否正确
   - 确认 n8n 工作流正常运行
   - 查看日志中的错误信息

4. **消息发送失败**
   - 检查 RobotCode 是否正确
   - 确认机器人已添加到群中
   - 验证机器人权限设置

### 调试模式

设置日志级别为 DEBUG 获取更详细的信息：

```env
LOG_LEVEL=DEBUG
```

## 开发

### 添加新的消息类型

在 `services/dingtalk_service.py` 中添加新的消息发送方法。

### 自定义AI响应处理

在 `services/ai_service.py` 中修改 `_parse_ai_response` 方法以适应不同的n8n响应格式。

### 扩展功能

- 支持图片、文件等多媒体消息
- 添加用户权限控制
- 实现消息历史记录
- 添加管理命令

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！ 