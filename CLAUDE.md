# CLAUDE.md

此文件为 Claude Code (claude.ai/code) 在该代码库中工作时提供指导。

## 沟通准则

**语言**：在此项目中始终使用中文回应，除非明确要求使用其他语言。所有沟通、解释和文档都应使用中文。

## 项目概述

Intent Test Framework - AI驱动的Web自动化测试平台，提供完整的WebUI界面用于测试用例管理、执行监控和结果分析。系统使用MidSceneJS进行AI驱动的视觉测试，支持自然语言测试描述。

### 设计原则
1. **极简主义**：简洁、专注的界面，无多余元素
2. **纯文本**：纯文字按钮和界面，不使用图标或表情符号
3. **一致排版**：系统字体，特定的字重和间距
4. **中性配色**：主要色调使用灰色和白色
5. **网格布局**：一致的网格系统进行内容组织
6. **状态指示**：简单的彩色圆点表示状态
7. **统一组件**：一致的按钮样式、表单元素和列表项

## 始终使用下列脚本启动本地测试调试环境

### 标准启动流程

**首次使用时：**
```bash
# 1. 配置环境变量（必须）
cp .env.local.template .env
# 编辑 .env 文件，填写您的AI API密钥

# 2. 启动完整开发环境
./scripts/dev-start.sh
```

**日常开发调试：**
```bash
# 快速重启服务（代码更改后）
./scripts/dev-restart.sh

# 运行测试和健康检查
./scripts/dev-test.sh

# 查看实时日志
./scripts/dev-logs.sh tail
```

### 服务访问地址

启动成功后可访问以下地址：

- 🌐 **Web界面**: http://localhost:5001
- 🤖 **AI服务**: http://localhost:3001  
- 📊 **测试用例管理**: http://localhost:5001/testcases
- 🔧 **执行控制台**: http://localhost:5001/execution
- 📈 **测试报告**: http://localhost:5001/reports

### 重要提示

- ⚠️ **必须配置AI API密钥**：在`.env`文件中设置正确的API密钥才能使用AI功能
- ⚠️ **首次使用需要权限**：`chmod +x scripts/*.sh`
- ⚠️ **数据库自动备份**：每次重新初始化会备份现有数据库
- ⚠️ **相对路径支持**：使用相对路径确保跨机器可移植性

## 系统架构

### 核心组件

1. **Web GUI层** (`web_gui/`)
   - `app.py` / `app_enhanced.py`: 主Flask应用程序
   - `api_routes.py`: API端点
   - `models.py`: SQLAlchemy数据库模型
   - `templates/`: HTML模板
   - `services/ai_enhanced_parser.py`: 自然语言解析

2. **AI引擎层**
   - `midscene_python.py`: MidSceneJS的Python包装器
   - `midscene_server.js`: AI操作的Node.js服务器
   - 与MidSceneJS库集成进行视觉AI测试

3. **数据库层**
   - 所有环境统一使用SQLite（开发和生产）
   - 模型：TestCase、ExecutionHistory、Template、StepExecution

4. **云部署**
   - `api/index.py`: Vercel无服务器入口点
   - `vercel.json`: Vercel部署配置
   - 生成可下载的本地代理包

### 数据流

1. **测试创建**: 用户通过WebUI创建测试用例 → 存储到数据库
2. **自然语言处理**: AI将自然语言描述解析为结构化步骤
3. **测试执行**: MidSceneJS AI引擎在浏览器中执行测试
4. **实时更新**: WebSocket连接提供实时执行状态
5. **结果存储**: 执行结果、截图和日志存储在数据库中

### 关键架构模式

- **微服务**: Flask Web应用 + Node.js AI服务器
- **事件驱动**: WebSocket实现实时通信
- **AI优先**: 所有元素交互都使用AI视觉模型
- **混合部署**: 本地开发 + 云端分发

## 测试结构

测试用例以JSON格式结构化，步骤包含：
- `action`: 动作类型（navigate, ai_input, ai_tap, ai_assert等）
- `params`: 动作特定参数
- `description`: 人类可读的步骤描述

### 变量引用

框架支持使用 `${variable}` 语法的动态变量引用：

- **Basic variable**: `${product_name}`
- **Object property**: `${product_info.name}`
- **Multi-level property**: `${step_1_result.data.items.price}`
- **Mixed text**: `"商品名称：${product_info.name}，价格：${product_info.price}元"`

Variables are automatically resolved during test execution. If a variable is not found, the original text is preserved and a warning is logged.

Example test case with variables:
```json
{
  "name": "Product Search Test",
  "steps": [
    {
      "action": "navigate",
      "params": {"url": "https://example.com"},
      "description": "Navigate to example.com"
    },
    {
      "action": "aiQuery",
      "params": {
        "query": "提取商品信息",
        "dataDemand": "{name: string, price: number, stock: number}"
      },
      "output_variable": "product_info",
      "description": "Extract product information"
    },
    {
      "action": "ai_input", 
      "params": {
        "text": "${product_info.name}",
        "locate": "search box"
      },
      "description": "Enter product name from extracted data"
    },
    {
      "action": "ai_assert",
      "params": {
        "condition": "商品价格显示为${product_info.price}元"
      },
      "description": "Verify product price matches extracted data"
    }
  ]
}
```

## Database Schema

### Core Tables
- `test_cases`: Test case definitions and metadata
- `execution_history`: Test execution records
- `step_executions`: Individual step execution details
- `templates`: Reusable test templates

### Key Relationships
- TestCase → ExecutionHistory (1:N)
- ExecutionHistory → StepExecution (1:N)
- Template → TestCase (1:N)

## Environment Configuration

### Required Environment Variables
```env
# AI Service Configuration
OPENAI_API_KEY=your_api_key
OPENAI_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
MIDSCENE_MODEL_NAME=qwen-vl-max-latest

# Database Configuration  
DATABASE_URL=sqlite:///data/app.db

# Application Settings
DEBUG=false
SECRET_KEY=your_secret_key
```

### AI Model Support
- Primary: Qwen VL (Alibaba Cloud DashScope)
- Alternative: GPT-4V (OpenAI)
- Configured via `MIDSCENE_MODEL_NAME` and `OPENAI_BASE_URL`

## Cloud Deployment

### Vercel Deployment
- Entry point: `api/index.py`
- Serverless function generates local proxy packages
- Automatic deployment from GitHub pushes

### Local Proxy Distribution
- Users download proxy packages from cloud interface
- Packages include MidSceneJS server + dependencies
- Self-contained for local AI testing execution

## Development Guidelines

### Code Quality
- Follow PEP 8 for Python code
- Use type hints where appropriate
- Comprehensive docstrings for all public functions
- Error handling with custom exception classes

### Testing
- Unit tests in `tests/` directory
- Integration tests for API endpoints
- AI functionality tests with mock responses

### Commit Standards
```
<type>(<scope>): <subject>

Examples:
feat(webui): add screenshot history feature
fix(api): resolve test case deletion error
docs(readme): update installation instructions
```

### File Organization
- Python files: `snake_case`
- JavaScript files: `camelCase`
- HTML templates: `template_name.html`
- Configuration: Environment variables over hardcoded values

## Local Proxy Package Management

The system generates downloadable local proxy packages containing:
- `midscene_server.js`: AI testing server
- `package.json`: Dependencies including @playwright/test, axios
- `start.sh/.bat`: Smart startup scripts with dependency checking
- Enhanced error handling and auto-repair functionality

Users download from https://intent-test-framework.vercel.app/local-proxy for the latest version.

## UI/UX Implementation Guidelines

### Template Structure
All templates should follow the minimal design pattern:
1. Use `base_layout.html` as parent template
2. Reference `minimal-preview/` designs for layout structure
3. Apply consistent spacing and typography
4. Use grid layouts for content organization

### Component Standards
- **Buttons**: Use `btn`, `btn-primary`, `btn-ghost`, `btn-small` classes
- **Forms**: Use `form-group`, `form-label`, `form-input`, `form-select` classes
- **Lists**: Use `list`, `list-item`, `list-item-content` structure
- **Cards**: Use `card`, `card-title`, `card-subtitle` hierarchy
- **Status**: Use `status` with color variants (`status-success`, `status-warning`, `status-error`)

### List Item Design Standards
Based on the testcases management page implementation, all list items should follow these design patterns:

#### HTML Structure
```html
<div class="list-item" title="点击进入编辑模式" onclick="editItem(id)">
    <div class="list-item-content">
        <div class="list-item-title">主标题</div>
        <div class="list-item-subtitle">副标题或描述</div>
        <div class="list-item-meta">
            <span class="text-gray-600">元数据1</span>
            <span class="text-gray-400">•</span>
            <span class="text-gray-600">元数据2</span>
            <!-- 更多元数据... -->
        </div>
    </div>
    <div class="flex items-center gap-1">
        <button class="btn btn-small btn-ghost" onclick="event.stopPropagation(); action1()">操作1</button>
        <button class="btn btn-small btn-primary" onclick="event.stopPropagation(); action2()">操作2</button>
        <button class="btn btn-small btn-ghost" onclick="event.stopPropagation(); action3()">操作3</button>
        <div class="status status-success" title="状态描述"></div>
    </div>
</div>
```

#### CSS Styling
```css
/* 列表项目点击效果样式 */
.list-item {
    cursor: pointer;
    transition: background-color 0.2s ease, transform 0.1s ease;
}

.list-item:hover {
    background-color: #f8f9fa;
    transform: translateY(-1px);
}

.list-item:active {
    transform: translateY(0);
}

/* 状态指示器增强效果 */
.status {
    cursor: help;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.status:hover {
    transform: scale(1.3);
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}
```

#### JavaScript Interaction
```javascript
// 创建列表项目
function createListItem(item) {
    const listItem = document.createElement('div');
    listItem.className = 'list-item';
    listItem.title = '点击进入编辑模式';  // 适当的提示文本
    listItem.onclick = () => editItem(item.id);
    
    // 设置HTML内容...
    
    return listItem;
}

// 按钮事件处理必须包含 event.stopPropagation()
function handleButtonClick(event, action) {
    event.stopPropagation();
    action();
}
```

#### Design Principles
1. **可点击性**: 整个列表项目都应该可以点击进入主要操作（通常是编辑）
2. **视觉反馈**: 悬停时有背景色变化和轻微上移效果
3. **事件隔离**: 按钮区域使用 `event.stopPropagation()` 防止冒泡
4. **一致的布局**: 左侧内容区域 + 右侧操作区域
5. **状态指示**: 使用彩色圆点表示状态，支持悬停放大效果
6. **元数据展示**: 使用灰色文本和分隔符展示次要信息

### Interactive Features
- Implement real-time filtering and search
- Use debouncing for search inputs (500ms)
- Provide immediate feedback for user actions
- Maintain consistent pagination patterns
- All list items should be clickable with hover effects
- Use consistent button layouts and event handling

# important-instruction-reminders
Do what has been asked; nothing more, nothing less.
NEVER create files unless they're absolutely necessary for achieving your goal.
ALWAYS prefer editing an existing file to creating a new one.
NEVER proactively create documentation files (*.md) or README files. Only create documentation files if explicitly requested by the User.
ALWAYS reference the minimal-preview directory designs when implementing or modifying UI components.
NEVER add icons or emoji symbols to interfaces - use text-only approach.
ALWAYS maintain the extreme minimalist design philosophy.
永远不要做假功能，真实实现所有功能，如果有问题及时反馈，不能骗人。

## 🏗️ 架构设计原则

### 核心架构原则

**🔴 架构优先原则**：在实现任何功能时，必须优先考虑架构的合理性和代码质量，不能为了快速实现功能而忽视架构设计的基本原则。

### 关键设计原则

1. **单一职责原则（SRP）**
   - 每个类和函数应该只有一个改变的理由
   - 避免创建过于庞大的类或函数

2. **DRY原则（Don't Repeat Yourself）**
   - 避免重复代码，特别是数据库连接、错误处理等通用逻辑
   - 创建可复用的服务层和工具函数
   - 统一的配置管理和资源管理

3. **依赖倒置原则**
   - 高层模块不应该依赖低层模块，两者都应该依赖抽象
   - 使用服务层抽象数据访问逻辑
   - 避免在控制器中直接编写SQL或复杂业务逻辑

4. **关注点分离**
   - 数据访问层：统一的数据库操作服务
   - 业务逻辑层：核心业务规则和流程
   - 控制器层：HTTP请求处理和响应格式化
   - 表示层：用户界面和交互逻辑

### 具体实施要求

#### 数据访问层设计
- **禁止**在API控制器中直接编写数据库连接代码
- **禁止**在多个地方重复相同的数据库连接逻辑
- **必须**使用统一的数据库服务层（DatabaseService）
- **必须**正确使用SQLAlchemy ORM和Flask应用上下文
- **必须**统一处理数据库事务和错误

#### 代码质量要求
- **重构优于修补**：当发现架构问题时，优先进行重构而不是局部修补
- **服务层抽象**：将复杂的业务逻辑抽象为服务层，避免在控制器中堆积代码
- **错误处理统一**：使用统一的错误处理机制，避免散落的try-catch块
- **资源管理**：使用上下文管理器和连接池管理数据库连接

#### 架构决策记录
- 当遇到SQLAlchemy上下文问题时，正确的解决方案是修复应用上下文，而不是绕过ORM
- 当发现重复代码时，立即进行抽象和重构，而不是继续复制
- 在添加新功能时，首先评估对现有架构的影响，必要时先改善架构再添加功能

### 架构评审清单

在提交代码前，必须确认：
- [ ] 是否遵循了单一职责原则？
- [ ] 是否存在重复代码？
- [ ] 是否正确使用了服务层抽象？
- [ ] 是否有适当的错误处理和资源管理？
- [ ] 数据库操作是否使用了统一的服务接口？
- [ ] 是否符合项目的整体架构风格？

## 🚫 严格禁止事项

**绝对禁止添加模拟数据或假数据**：
- 永远不要在API中返回模拟数据、示例数据或假数据
- 永远不要创建mock响应来"临时解决"问题
- 所有API必须返回真实的数据库数据或明确的错误信息
- 如果数据库查询有问题，必须真正修复查询问题，而不是返回假数据
- 如果功能暂时无法实现，必须明确告知用户，不能用假数据欺骗
- 用户要求看到真实数据时，必须确保连接的是真实的数据库并返回真实数据

**绝对禁止违反架构原则的临时修复**：
- ❌ **绕过ORM使用直接SQL**：即使遇到SQLAlchemy上下文问题，也不能用直接SQL绕过
- ❌ **违反单一职责原则**：不能为了快速实现而在一个函数中混合多种职责
- ❌ **忽略错误处理**：不能用简单的try-except来掩盖架构设计缺陷
- ❌ **破坏依赖注入**：不能为了方便而硬编码依赖关系
- ❌ **跳过测试驱动开发**：不能为了速度而跳过测试先行的开发流程

**核心原则提醒**：
- 🎯 **架构完整性** > 实现速度
- 🎯 **长期可维护性** > 短期便利  
- 🎯 **深入问题分析** > 表面修补
- 🎯 **真实功能实现** > 临时解决方案

## 🧪 测试驱动开发原则

### 核心TDD理念

**🔴 测试优先原则**：任何新功能开发必须遵循TDD流程，先编写测试，再实现功能。

### TDD开发流程

1. **🔴 Red**: 编写失败的测试用例
2. **🟢 Green**: 实现最小可工作代码使测试通过
3. **🔵 Refactor**: 重构优化代码质量

### 测试策略

#### 单元测试 (`tests/unit/`)
- 测试单个函数和类方法
- 覆盖数据模型、服务层、工具函数
- 覆盖率要求：≥ 80%

#### API测试 (`tests/api/`)
- 测试HTTP API端点完整流程
- 覆盖状态码、参数验证、响应格式
- 覆盖率要求：100%（所有API端点）
---

## ⚡ 重要指令提醒

### 🔴 开发时的核心原则
1. **架构优先**：架构完整性 > 实现速度
2. **真实功能**：真实实现 > 临时解决方案  
3. **深入分析**：问题根因 > 表面修补
4. **中文优先**：所有交流都使用中文

### 🚫 绝对禁止
- ❌ 返回假数据或模拟数据欺骗用户
- ❌ 绕过架构原则的临时修复
- ❌ 违反单一职责和DRY原则
- ❌ 跳过测试驱动开发流程

### ✅ 必须遵循
- ✅ 使用极简设计参考文件
- ✅ 遵循TDD测试优先原则
- ✅ 通过架构评审清单检查
- ✅ 真实实现所有功能