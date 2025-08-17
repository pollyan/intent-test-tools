# 🏛️ 整体系统架构

## 高层架构图
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │  AI Engine     │
│                 │    │                 │    │                 │
│ • React UI      │────│ • Flask API     │────│ • MidSceneJS    │
│ • Smart Input   │    │ • Variable      │    │ • Playwright    │
│ • Form Builder  │    │   Resolver      │    │ • Data Extract  │
│                 │    │ • Validation    │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Data Layer    │    │  Execution      │    │  Infrastructure │
│                 │    │  Context        │    │                 │
│ • PostgreSQL    │    │                 │    │ • Vercel        │
│ • Variable      │────│ • Memory Store  │    │ • Supabase      │
│   Storage       │    │ • Session Mgmt  │    │ • Local Proxy   │
│ • Schema Mgmt   │    │ • Lifecycle     │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 数据流架构
```
用户输入 → 智能提示 → 参数验证 → 步骤执行 → 数据提取 → 变量存储 → 后续引用
    ↑         ↓         ↓         ↓         ↓         ↓         ↓
智能建议 ← UI组件 ← 表单生成 ← AI引擎 ← 解析器 ← 上下文 ← 变量解析
```

---
