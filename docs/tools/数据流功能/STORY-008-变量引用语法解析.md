# STORY-008: 实现变量引用语法解析

**Story ID**: STORY-008  
**Epic**: EPIC-001 数据流核心功能  
**Sprint**: Sprint 2  
**优先级**: High  
**估算**: 8 Story Points  
**分配给**: Backend Developer + 全栈工程师  
**创建日期**: 2025-01-30  
**产品经理**: John  

---

## 📖 故事描述

**作为** 测试工程师  
**我希望** 在测试步骤的参数中使用`${variable_name}`和`${variable.property}`语法  
**以便** 我可以引用之前步骤存储的变量数据  
**这样** 我就能创建动态的、数据驱动的测试流程，步骤间可以传递和使用数据  

---

## 🎯 验收标准

### AC-1: 基础变量引用语法支持
**给定** 我在步骤参数中使用`${variable_name}`语法  
**当** 系统执行该步骤时  
**那么** 变量引用应该被正确解析为实际的变量值  

**示例**:
```json
{
  "action": "ai_input",
  "params": {
    "text": "搜索${product_name}",
    "locate": "搜索框"
  }
}
```

### AC-2: 对象属性访问语法支持
**给定** 我使用`${variable.property}`语法引用对象属性  
**当** 系统解析变量引用时  
**那么** 应该正确提取对象中的指定属性值  

**示例**:
```json
{
  "action": "ai_assert",
  "params": {
    "condition": "价格显示为${product_info.price}元"
  }
}
```

### AC-3: 嵌套属性访问支持
**给定** 我使用深层嵌套语法如`${user.profile.address.city}`  
**当** 系统解析变量引用时  
**那么** 应该支持最多5层的嵌套属性访问  

### AC-4: 数组元素访问支持
**给定** 变量是数组类型  
**当** 我使用`${products[0].name}`语法  
**那么** 系统应该正确提取数组指定索引的元素  

**支持特性**:
- 正数索引：`${items[0]}`, `${items[1]}`
- 负数索引：`${items[-1]}` (最后一个元素)
- 嵌套访问：`${items[0].property}`

### AC-5: 错误处理和用户友好提示
**给定** 变量引用存在问题  
**当** 系统尝试解析时  
**那么** 应该提供清晰的错误信息并记录到日志  

**错误场景**:
- 变量不存在：`变量 'unknown_var' 未定义`
- 属性不存在：`对象中不存在属性 'unknown_prop'`
- 数组索引越界：`数组索引 5 超出范围 (长度: 3)`
- 类型错误：`无法在非对象类型上访问属性`

### AC-6: 多个变量引用在同一参数中
**给定** 单个参数中包含多个变量引用  
**当** 系统解析参数时  
**那么** 所有变量引用都应该被正确替换  

**示例**:
```json
{
  "action": "ai_input",
  "params": {
    "text": "${user_name}购买了${product_count}个${product_name}"
  }
}
```

---

## 🔧 技术实现要求

### 核心变量解析器
```python
class VariableResolver:
    def __init__(self, variable_manager: VariableManager):
        self.variable_manager = variable_manager
        self.pattern = re.compile(r'\$\{([^}]+)\}')
    
    def resolve_text(self, text: str, step_index: int = None) -> str:
        """解析文本中的所有变量引用"""
        
    def resolve_variable_path(self, reference: str) -> Any:
        """解析变量路径，支持嵌套属性和数组访问"""
        
    def validate_reference(self, reference: str) -> bool:
        """验证变量引用语法的正确性"""
```

### 语法解析规则
1. **基础语法**: `${variable_name}`
2. **属性访问**: `${object.property}`
3. **嵌套访问**: `${object.nested.property}` (最多5层)
4. **数组访问**: `${array[index]}` 或 `${array[index].property}`
5. **混合使用**: `${data.items[0].name}`

### 正则表达式模式
```python
# 匹配 ${...} 格式的变量引用
VARIABLE_PATTERN = r'\$\{([^}]+)\}'

# 解析变量路径的子模式
PATH_PATTERN = r'^([a-zA-Z_][a-zA-Z0-9_]*)((?:\.[a-zA-Z_][a-zA-Z0-9_]*|\[\d+\]|\[-\d+\])*)$'
```

### 错误处理策略
```python
class VariableResolutionError(Exception):
    def __init__(self, reference: str, reason: str, step_index: int = None):
        self.reference = reference
        self.reason = reason
        self.step_index = step_index
        super().__init__(f"变量引用错误 '{reference}': {reason}")
```

---

## 🧪 测试计划

### 单元测试场景
1. **基础变量引用测试**
   ```python
   def test_simple_variable_reference():
       # 测试 ${var_name} 格式
       assert resolver.resolve_text("Hello ${name}") == "Hello World"
   ```

2. **对象属性访问测试**
   ```python
   def test_object_property_access():
       # 测试 ${obj.prop} 格式
       assert resolver.resolve_text("Price: ${product.price}") == "Price: 99.99"
   ```

3. **数组访问测试**
   ```python
   def test_array_access():
       # 测试 ${arr[0]} 格式
       assert resolver.resolve_text("${items[0]}") == "first_item"
       assert resolver.resolve_text("${items[-1]}") == "last_item"
   ```

4. **复杂嵌套测试**
   ```python
   def test_nested_access():
       # 测试深层嵌套访问
       assert resolver.resolve_text("${user.profile.address.city}") == "北京"
   ```

5. **错误处理测试**
   ```python
   def test_undefined_variable_error():
       with pytest.raises(VariableResolutionError):
           resolver.resolve_text("${undefined_var}")
   ```

### 集成测试场景
1. **端到端数据流测试**
   ```json
   [
     {
       "action": "aiQuery",
       "params": {"query": "提取用户信息", "dataDemand": "{name: string, age: number}"},
       "output_variable": "user_info"
     },
     {
       "action": "ai_input",
       "params": {
         "text": "用户${user_info.name}，年龄${user_info.age}岁",
         "locate": "输入框"
       }
     }
   ]
   ```

2. **复杂数据结构测试**
   ```json
   {
     "action": "ai_assert",
     "params": {
       "condition": "订单包含${order.items[0].name}，数量${order.items[0].quantity}个"
     }
   }
   ```

### 性能测试
- 大量变量引用的解析性能
- 深层嵌套访问的性能影响
- 并发解析的线程安全性

---

## 📊 Definition of Done

- [ ] **核心功能**: 所有变量引用语法正确支持
- [ ] **错误处理**: 完善的错误检测和用户友好提示
- [ ] **性能要求**: 变量解析响应时间<100ms
- [ ] **测试覆盖**: 单元测试覆盖率>95%
- [ ] **集成测试**: 端到端场景测试通过
- [ ] **文档更新**: 变量引用语法文档完善
- [ ] **代码审查**: 代码质量审查通过
- [ ] **向后兼容**: 不影响现有功能

---

## 🔗 依赖关系

**前置依赖**:
- STORY-007: output_variable参数解析和存储（必须先有变量数据）
- STORY-003: VariableResolverService基础架构

**后续依赖**:
- STORY-009: 集成变量解析到步骤执行流程
- STORY-010: SmartVariableInput组件（智能提示功能）

---

## 💡 实现注意事项

### 性能优化
- 使用编译后的正则表达式提升匹配性能
- 实现变量解析结果缓存
- 避免重复的深层对象访问

### 安全考虑
- 防止无限递归的嵌套访问
- 限制变量路径长度，防止拒绝服务攻击
- 输入验证防止代码注入

### 扩展性设计
- 支持自定义变量引用格式
- 预留变量转换函数钩子
- 支持变量引用的调试模式

---

**状态**: 待开始  
**创建人**: John (Product Manager)  
**最后更新**: 2025-01-30  

*此用户故事是数据流功能的核心，完成后将实现完整的变量引用能力*