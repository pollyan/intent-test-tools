# STORY-007: 实现output_variable参数解析和存储

**Story ID**: STORY-007  
**Epic**: EPIC-001 数据流核心功能  
**Sprint**: Sprint 2  
**优先级**: High  
**估算**: 5 Story Points  
**分配给**: Backend Developer + 全栈工程师  
**创建日期**: 2025-01-30  
**产品经理**: John  

---

## 📖 故事描述

**作为** 测试工程师  
**我希望** 在现有的Midscene API Action中添加`output_variable`参数  
**以便** 我可以将API方法的返回值保存为变量供后续步骤使用  
**这样** 我就能创建数据驱动的测试流程，避免重复的数据提取操作  

---

## 🎯 验收标准

### AC-1: 支持output_variable参数配置
**给定** 我在编辑测试步骤时  
**当** 我为有返回值的Action添加`output_variable`参数  
**那么** 系统应该验证参数格式并保存配置  

**示例配置**:
```json
{
  "action": "aiQuery",
  "params": {
    "query": "提取商品价格和库存信息",
    "dataDemand": "{price: number, stock: number}"
  },
  "output_variable": "product_info",
  "description": "提取商品基本信息"
}
```

### AC-2: 返回值自动捕获和存储
**给定** 测试步骤配置了`output_variable`参数  
**当** 执行对应的Midscene API方法  
**那么** 系统应该自动捕获返回值并存储到执行上下文中  

**详细要求**:
- 支持的API方法：aiQuery, aiString, aiNumber, aiBoolean, aiAsk, aiLocate, evaluateJavaScript
- 自动检测返回值数据类型
- 存储到数据库的execution_variables表
- 记录变量来源（步骤索引、API方法、参数）

### AC-3: 数据类型正确识别和存储
**给定** API方法返回不同类型的数据  
**当** 系统捕获返回值  
**那么** 应该正确识别数据类型并以适当格式存储  

**数据类型支持**:
- `string`: 字符串类型
- `number`: 数字类型（整数和浮点数）
- `boolean`: 布尔值类型
- `object`: 复杂对象类型
- `array`: 数组类型

### AC-4: 错误处理和日志记录
**给定** API执行过程中发生错误  
**当** 尝试捕获返回值时  
**那么** 系统应该记录错误信息并继续执行后续步骤  

**错误场景**:
- API方法执行失败
- 返回值格式不符合预期
- 变量名称格式不正确
- 数据库存储失败

### AC-5: 向后兼容性保证
**给定** 现有测试用例没有使用`output_variable`参数  
**当** 执行这些测试用例  
**那么** 系统应该正常执行，不受新功能影响  

---

## 🔧 技术实现要求

### 后端实现 (Flask)
1. **API路由扩展**
   - 修改`/api/v1/testcases/{id}/execute`端点
   - 支持output_variable参数解析
   - 集成变量存储逻辑

2. **数据库操作**
   - 实现ExecutionVariable模型的CRUD操作
   - 优化查询性能（索引策略）
   - 确保数据一致性

3. **服务层组件**
   ```python
   class VariableStorageService:
       def store_variable(self, execution_id, variable_name, value, metadata)
       def get_variable(self, execution_id, variable_name)
       def list_variables(self, execution_id)
   ```

### MidSceneJS集成
1. **步骤执行器增强**
   - 修改enhanced_step_executor.py
   - 为每个有返回值的API方法添加捕获逻辑
   - 实现类型检测和转换

2. **执行流程修改**
   ```python
   # 执行API方法
   result = await page.aiQuery(params.query, params.dataDemand)
   
   # 如果配置了输出变量，则存储结果
   if step.get('output_variable'):
       variable_manager.store_variable(
           variable_name=step['output_variable'],
           value=result,
           source_step_index=step_index,
           source_api_method='aiQuery',
           source_api_params=params
       )
   ```

### 数据模型
```python
class ExecutionVariable(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    execution_id = db.Column(db.String(50), nullable=False)
    variable_name = db.Column(db.String(255), nullable=False)
    variable_value = db.Column(db.Text)  # JSON存储
    data_type = db.Column(db.String(50), nullable=False)
    source_step_index = db.Column(db.Integer, nullable=False)
    source_api_method = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
```

---

## 🧪 测试计划

### 单元测试
1. **变量存储功能测试**
   - 测试各种数据类型的存储
   - 测试边界条件和异常情况
   - 测试并发访问安全性

2. **API方法集成测试**
   - 测试每个有返回值的Midscene API方法
   - 验证返回值捕获的准确性
   - 测试错误场景处理

### 集成测试
1. **端到端测试场景**
   ```json
   [
     {
       "action": "navigate",
       "params": {"url": "https://example-shop.com"}
     },
     {
       "action": "aiQuery",
       "params": {
         "query": "提取商品价格",
         "dataDemand": "{price: number}"
       },
       "output_variable": "product_price"
     },
     {
       "action": "ai_assert",
       "params": {
         "condition": "价格显示为${product_price}"
       }
     }
   ]
   ```

2. **性能测试**
   - 大量变量存储的性能测试
   - 并发执行的数据隔离测试
   - 内存使用和数据库性能测试

---

## 📊 Definition of Done

- [ ] **代码完成**: 所有功能代码编写完成并通过代码审查
- [ ] **单元测试**: 测试覆盖率达到90%以上，所有测试通过
- [ ] **集成测试**: 端到端测试场景通过
- [ ] **文档更新**: API文档和用户指南更新
- [ ] **性能验证**: 变量存储操作响应时间<500ms
- [ ] **安全审查**: 数据存储安全性审查通过
- [ ] **向后兼容**: 现有测试用例100%兼容
- [ ] **产品验收**: 产品经理验收通过

---

## 🔗 依赖关系

**前置依赖**:
- STORY-001: ExecutionContext数据模型已完成
- STORY-002: 数据库Schema迁移已部署
- STORY-003: VariableResolverService基础架构就绪

**后续依赖**:
- STORY-008: 变量引用语法解析（依赖此Story的变量存储功能）
- STORY-009: 集成变量解析到步骤执行流程

---

## 💡 技术注意事项

1. **性能优化**
   - 变量数据使用JSON格式存储，便于复杂对象处理
   - 实施变量数据缓存策略，减少数据库查询
   - 为execution_id + variable_name建立复合索引

2. **安全考虑**
   - 敏感数据变量支持加密存储
   - 变量访问权限控制
   - SQL注入防护

3. **可扩展性**
   - 支持自定义数据类型扩展
   - 变量元数据支持扩展字段
   - 预留变量转换和验证钩子

---

**状态**: 待开始  
**创建人**: John (Product Manager)  
**最后更新**: 2025-01-30  

*此用户故事将根据开发进展和反馈持续更新*