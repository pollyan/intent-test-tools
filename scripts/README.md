# 意图测试平台 - 本地开发环境脚本

本目录包含了用于本地开发和调试的各种脚本工具，帮助您快速搭建、启动和调试意图测试平台。

## 🚀 快速开始

### 首次使用

1. **配置环境变量**
   ```bash
   # 复制环境变量模板
   cp .env.local.template .env
   
   # 编辑配置文件，填写您的AI API密钥
   nano .env
   ```

2. **启动开发环境**
   ```bash
   # Linux/Mac
   chmod +x scripts/*.sh
   ./scripts/dev-start.sh
   
   # Windows
   scripts\dev-start.bat
   ```

### 日常开发

```bash
# 快速重启服务（代码更改后）
./scripts/dev-restart.sh

# 运行测试套件
./scripts/dev-test.sh

# 查看实时日志
./scripts/dev-logs.sh tail
```

## 📜 脚本详细说明

### 1. dev-start.sh / dev-start.bat
**主要的开发环境启动脚本**

**功能：**
- 自动检查和安装Python/Node.js依赖
- 创建Python虚拟环境
- 初始化SQLite数据库
- 启动MidScene AI服务器和Web应用
- 提供完整的服务健康检查

**使用方法：**
```bash
./scripts/dev-start.sh
```

**启动后的服务地址：**
- Web界面: http://localhost:5001
- AI服务: http://localhost:3001
- 测试用例管理: http://localhost:5001/testcases
- 执行控制台: http://localhost:5001/execution
- 测试报告: http://localhost:5001/reports

### 2. dev-restart.sh
**快速重启脚本**

**使用场景：**
- 代码更改后需要重启服务
- 服务出现异常需要重新启动
- 更换配置后重新加载

**功能：**
- 优雅停止现有服务
- 清理端口占用
- 快速重新启动所有服务

```bash
./scripts/dev-restart.sh
```

### 3. dev-test.sh
**综合测试和健康检查脚本**

**可用命令：**
```bash
./scripts/dev-test.sh check     # 检查服务状态
./scripts/dev-test.sh api       # 测试API端点
./scripts/dev-test.sh test      # 运行单元测试
./scripts/dev-test.sh quality   # 代码质量检查
./scripts/dev-test.sh db        # 数据库健康检查
./scripts/dev-test.sh bench     # 性能基准测试
./scripts/dev-test.sh logs      # 查看服务日志
./scripts/dev-test.sh clean     # 清理临时文件
./scripts/dev-test.sh all       # 运行所有检查（默认）
```

### 4. dev-logs.sh
**日志查看和调试工具**

**可用命令：**
```bash
./scripts/dev-logs.sh tail              # 实时查看所有日志
./scripts/dev-logs.sh midscene errors   # 查看MidScene错误日志
./scripts/dev-logs.sh web follow        # 实时跟踪Web应用日志
./scripts/dev-logs.sh errors            # 分析所有错误
./scripts/dev-logs.sh monitor           # 监控系统资源
./scripts/dev-logs.sh logs clean        # 清理日志文件
```

**日志选项：**
- `recent` - 显示最近50行（默认）
- `all` - 显示全部日志
- `errors` - 只显示错误日志
- `follow` - 实时跟踪日志

### 5. init_db.py
**数据库初始化脚本**

**功能：**
- 创建SQLite数据库表结构
- 插入示例测试用例和执行历史
- 创建必要的索引优化性能

**直接运行：**
```bash
python3 scripts/init_db.py
```

## ⚙️ 环境配置

### .env配置文件说明

环境变量模板位于 `.env.local.template`，主要配置项：

```env
# 数据库配置（使用SQLite）
DATABASE_URL=sqlite:///data/app.db

# AI服务配置（选择其一）
# 阿里云DashScope
OPENAI_API_KEY=sk-your-dashscope-api-key
OPENAI_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
MIDSCENE_MODEL_NAME=qwen-vl-max-latest

# OpenAI
# OPENAI_API_KEY=sk-your-openai-api-key
# OPENAI_BASE_URL=https://api.openai.com/v1
# MIDSCENE_MODEL_NAME=gpt-4o

# 服务端口配置
WEB_PORT=5001
MIDSCENE_PORT=3001

# 开发环境配置
DEBUG=true
LOG_LEVEL=INFO
```

### 目录结构

开发环境会自动创建以下目录：

```
intent-test-tools/
├── scripts/              # 开发脚本
├── logs/                 # 日志文件
│   ├── midscene.log     # MidScene服务日志
│   ├── app.log          # Web应用日志
│   └── midscene.pid     # MidScene进程ID
├── data/                 # SQLite数据库
│   └── app.db           # 主数据库文件
├── screenshots/          # 测试截图
├── venv/                 # Python虚拟环境
└── node_modules/         # Node.js依赖
```

## 🔧 故障排除

### 常见问题

1. **端口被占用**
   ```bash
   # 检查端口占用
   lsof -i :3001  # MidScene端口
   lsof -i :5001  # Web端口
   
   # 或使用测试脚本
   ./scripts/dev-test.sh check
   ```

2. **依赖安装失败**
   ```bash
   # 清理并重新安装
   rm -rf venv node_modules
   ./scripts/dev-start.sh
   ```

3. **数据库问题**
   ```bash
   # 重新初始化数据库
   rm data/app.db
   python3 scripts/init_db.py
   ```

4. **日志分析**
   ```bash
   # 查看错误日志
   ./scripts/dev-logs.sh errors
   
   # 实时监控
   ./scripts/dev-logs.sh tail
   ```

### 调试模式

启用详细调试输出：

```bash
# 设置调试模式
./scripts/dev-logs.sh debug

# 重启服务应用调试设置
./scripts/dev-restart.sh
```

## 🧪 测试和质量保证

### 自动化测试

```bash
# 运行完整测试套件
./scripts/dev-test.sh all

# 只运行API测试
./scripts/dev-test.sh api

# 代码质量检查
./scripts/dev-test.sh quality
```

### 性能监控

```bash
# 系统资源监控
./scripts/dev-logs.sh monitor

# 性能基准测试
./scripts/dev-test.sh bench
```

### 日志管理

```bash
# 查看日志状态
./scripts/dev-logs.sh logs status

# 轮转日志文件
./scripts/dev-logs.sh logs rotate

# 清理旧日志
./scripts/dev-logs.sh logs clean

# 归档日志
./scripts/dev-logs.sh logs archive
```

## 🔄 开发工作流

推荐的日常开发工作流程：

1. **启动开发环境**
   ```bash
   ./scripts/dev-start.sh
   ```

2. **进行代码修改**
   - 编辑Python/JavaScript代码
   - 修改模板或配置文件

3. **测试更改**
   ```bash
   # 快速重启应用更改
   ./scripts/dev-restart.sh
   
   # 运行测试验证
   ./scripts/dev-test.sh api
   ```

4. **调试问题**
   ```bash
   # 查看实时日志
   ./scripts/dev-logs.sh tail
   
   # 分析错误
   ./scripts/dev-logs.sh errors
   ```

5. **质量检查**
   ```bash
   # 运行完整测试套件
   ./scripts/dev-test.sh all
   
   # 清理临时文件
   ./scripts/dev-test.sh clean
   ```

## 📋 脚本权限设置

在Linux/Mac系统上，首次使用需要设置执行权限：

```bash
chmod +x scripts/*.sh
```

## 🎯 使用技巧

1. **多终端开发**
   - 终端1：运行 `./scripts/dev-start.sh`
   - 终端2：运行 `./scripts/dev-logs.sh tail` 监控日志
   - 终端3：进行开发和测试

2. **快速验证**
   - 代码更改后使用 `./scripts/dev-restart.sh`
   - 定期运行 `./scripts/dev-test.sh api` 验证API

3. **问题诊断**
   - 使用 `./scripts/dev-logs.sh errors` 快速定位错误
   - 使用 `./scripts/dev-logs.sh monitor` 检查资源使用

4. **环境清理**
   - 定期运行 `./scripts/dev-test.sh clean`
   - 使用 `./scripts/dev-logs.sh logs clean` 清理日志

通过这套脚本工具，您可以大大提高本地开发效率，快速定位和解决问题！