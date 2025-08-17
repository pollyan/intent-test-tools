"""
数据模型定义
"""
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()

class TestCase(db.Model):
    """测试用例模型"""
    __tablename__ = 'test_cases'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    steps = db.Column(db.Text, nullable=False)  # JSON string
    tags = db.Column(db.String(500))
    category = db.Column(db.String(100))
    priority = db.Column(db.Integer, default=3)
    created_by = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # 索引优化
    __table_args__ = (
        db.Index('idx_testcase_active', 'is_active'),
        db.Index('idx_testcase_category', 'category', 'is_active'),
        db.Index('idx_testcase_created', 'created_at'),
        db.Index('idx_testcase_priority', 'priority', 'is_active'),
    )
    
    def to_dict(self, include_stats=True):
        """转换为字典"""
        data = {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'steps': json.loads(self.steps) if self.steps else [],
            'tags': self.tags.split(',') if self.tags else [],
            'category': self.category,
            'priority': self.priority,
            'created_by': self.created_by,
            'created_at': self.created_at.strftime('%Y-%m-%dT%H:%M:%S.%fZ') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%dT%H:%M:%S.%fZ') if self.updated_at else None,
            'is_active': self.is_active
        }
        
        # 可选的统计信息计算，避免N+1查询问题
        if include_stats:
            # 计算执行次数和成功率
            execution_count = ExecutionHistory.query.filter_by(test_case_id=self.id).count()
            success_count = ExecutionHistory.query.filter_by(
                test_case_id=self.id, 
                status='success'
            ).count()
            success_rate = (success_count / execution_count * 100) if execution_count > 0 else 0
            
            data.update({
                'execution_count': execution_count,
                'success_rate': round(success_rate, 1)
            })
        else:
            data.update({
                'execution_count': 0,
                'success_rate': 0
            })
        
        return data
    
    @classmethod
    def get_with_stats(cls, limit=None, offset=None):
        """批量获取测试用例及其统计信息，优化查询性能"""
        from sqlalchemy import func
        
        # 使用子查询优化执行统计计算
        execution_stats = db.session.query(
            ExecutionHistory.test_case_id,
            func.count(ExecutionHistory.id).label('total_executions'),
            func.count(db.case([(ExecutionHistory.status == 'success', 1)])).label('successful_executions')
        ).group_by(ExecutionHistory.test_case_id).subquery()
        
        query = db.session.query(
            cls,
            execution_stats.c.total_executions.label('execution_count'),
            execution_stats.c.successful_executions.label('success_count')
        ).outerjoin(
            execution_stats, cls.id == execution_stats.c.test_case_id
        ).filter(cls.is_active == True)
        
        if limit:
            query = query.limit(limit)
        if offset:
            query = query.offset(offset)
            
        return query.all()
    
    @classmethod
    def from_dict(cls, data):
        """从字典创建实例"""
        return cls(
            name=data.get('name'),
            description=data.get('description'),
            steps=json.dumps(data.get('steps', [])),
            tags=','.join(data.get('tags', [])),
            category=data.get('category'),
            priority=data.get('priority', 3),
            created_by=data.get('created_by', 'system')
        )

class ExecutionHistory(db.Model):
    """执行历史模型"""
    __tablename__ = 'execution_history'
    
    id = db.Column(db.Integer, primary_key=True)
    execution_id = db.Column(db.String(50), unique=True, nullable=False)
    test_case_id = db.Column(db.Integer, db.ForeignKey('test_cases.id'), nullable=False)
    status = db.Column(db.String(50), nullable=False)  # running, success, failed, stopped
    mode = db.Column(db.String(20), default='headless')  # browser, headless
    browser = db.Column(db.String(50), default='chrome')
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime)
    duration = db.Column(db.Integer)  # 执行时间(秒)
    steps_total = db.Column(db.Integer)
    steps_passed = db.Column(db.Integer)
    steps_failed = db.Column(db.Integer)
    result_summary = db.Column(db.Text)  # JSON string
    screenshots_path = db.Column(db.Text)
    logs_path = db.Column(db.Text)
    error_message = db.Column(db.Text)
    error_stack = db.Column(db.Text)
    executed_by = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 索引优化
    __table_args__ = (
        db.Index('idx_execution_testcase_status', 'test_case_id', 'status'),
        db.Index('idx_execution_start_time', 'start_time'),
        db.Index('idx_execution_status', 'status'),
        db.Index('idx_execution_executed_by', 'executed_by'),
        db.Index('idx_execution_created_at', 'created_at'),
    )
    
    # 关系
    test_case = db.relationship('TestCase', backref=db.backref('executions', lazy=True))
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'execution_id': self.execution_id,
            'test_case_id': self.test_case_id,
            'test_case_name': self.test_case.name if self.test_case else None,
            'status': self.status,
            'mode': self.mode,
            'browser': self.browser,
            'start_time': self.start_time.strftime('%Y-%m-%dT%H:%M:%S.%fZ') if self.start_time else None,
            'end_time': self.end_time.strftime('%Y-%m-%dT%H:%M:%S.%fZ') if self.end_time else None,
            'duration': self.duration,
            'steps_total': self.steps_total,
            'steps_passed': self.steps_passed,
            'steps_failed': self.steps_failed,
            'result_summary': json.loads(self.result_summary) if self.result_summary else {},
            'screenshots_path': self.screenshots_path,
            'logs_path': self.logs_path,
            'error_message': self.error_message,
            'executed_by': self.executed_by,
            'created_at': self.created_at.strftime('%Y-%m-%dT%H:%M:%S.%fZ') if self.created_at else None
        }

class StepExecution(db.Model):
    """步骤执行详情模型"""
    __tablename__ = 'step_executions'
    
    id = db.Column(db.Integer, primary_key=True)
    execution_id = db.Column(db.String(50), db.ForeignKey('execution_history.execution_id'), nullable=False)
    step_index = db.Column(db.Integer, nullable=False)
    step_description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), nullable=False)  # success, failed, skipped
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime)
    duration = db.Column(db.Integer)
    screenshot_path = db.Column(db.Text)
    ai_confidence = db.Column(db.Float)
    ai_decision = db.Column(db.Text)  # JSON string
    error_message = db.Column(db.Text)
    
    # 索引优化
    __table_args__ = (
        db.Index('idx_step_execution_id_index', 'execution_id', 'step_index'),
        db.Index('idx_step_status', 'execution_id', 'status'),
        db.Index('idx_step_start_time', 'start_time'),
    )
    
    # 关系
    execution = db.relationship('ExecutionHistory', backref=db.backref('step_executions', lazy=True))
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'execution_id': self.execution_id,
            'step_index': self.step_index,
            'step_description': self.step_description,
            'status': self.status,
            'start_time': self.start_time.strftime('%Y-%m-%dT%H:%M:%S.%fZ') if self.start_time else None,
            'end_time': self.end_time.strftime('%Y-%m-%dT%H:%M:%S.%fZ') if self.end_time else None,
            'duration': self.duration,
            'screenshot_path': self.screenshot_path,
            'ai_confidence': self.ai_confidence,
            'ai_decision': json.loads(self.ai_decision) if self.ai_decision else {},
            'error_message': self.error_message
        }

class Template(db.Model):
    """测试模板模型"""
    __tablename__ = 'templates'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(100))
    steps_template = db.Column(db.Text, nullable=False)  # JSON string
    parameters = db.Column(db.Text)  # JSON string - 模板参数定义
    usage_count = db.Column(db.Integer, default=0)
    created_by = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_public = db.Column(db.Boolean, default=False)
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'category': self.category,
            'steps_template': json.loads(self.steps_template) if self.steps_template else [],
            'parameters': json.loads(self.parameters) if self.parameters else {},
            'usage_count': self.usage_count,
            'created_by': self.created_by,
            'created_at': self.created_at.strftime('%Y-%m-%dT%H:%M:%S.%fZ') if self.created_at else None,
            'is_public': self.is_public
        }
    
    @classmethod
    def from_dict(cls, data):
        """从字典创建实例"""
        return cls(
            name=data.get('name'),
            description=data.get('description'),
            category=data.get('category'),
            steps_template=json.dumps(data.get('steps_template', [])),
            parameters=json.dumps(data.get('parameters', {})),
            created_by=data.get('created_by', 'system'),
            is_public=data.get('is_public', False)
        )

class ExecutionVariable(db.Model):
    """执行变量模型 - 存储测试执行过程中的变量数据"""
    __tablename__ = 'execution_variables'
    
    id = db.Column(db.Integer, primary_key=True)
    execution_id = db.Column(db.String(50), db.ForeignKey('execution_history.execution_id'), nullable=False)
    variable_name = db.Column(db.String(255), nullable=False)
    variable_value = db.Column(db.Text)  # JSON string存储变量值
    data_type = db.Column(db.String(50), nullable=False)  # string, number, boolean, object, array
    source_step_index = db.Column(db.Integer, nullable=False)  # 来源步骤索引
    source_api_method = db.Column(db.String(100))  # 来源API方法(aiQuery, aiString等)
    source_api_params = db.Column(db.Text)  # JSON string存储API参数
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_encrypted = db.Column(db.Boolean, default=False)  # 是否加密存储
    
    # 复合索引优化查询性能和唯一约束
    __table_args__ = (
        db.Index('idx_execution_variable', 'execution_id', 'variable_name'),
        db.Index('idx_execution_step', 'execution_id', 'source_step_index'),
        db.Index('idx_variable_type', 'execution_id', 'data_type'),
        db.UniqueConstraint('execution_id', 'variable_name', name='uk_execution_variable_name'),
    )
    
    # 关系
    execution = db.relationship('ExecutionHistory', backref=db.backref('variables', lazy=True))
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'execution_id': self.execution_id,
            'variable_name': self.variable_name,
            'variable_value': json.loads(self.variable_value) if self.variable_value else None,
            'data_type': self.data_type,
            'source_step_index': self.source_step_index,
            'source_api_method': self.source_api_method,
            'source_api_params': json.loads(self.source_api_params) if self.source_api_params else {},
            'created_at': self.created_at.strftime('%Y-%m-%dT%H:%M:%S.%fZ') if self.created_at else None,
            'is_encrypted': self.is_encrypted
        }
    
    @classmethod
    def from_dict(cls, data):
        """从字典创建实例"""
        return cls(
            execution_id=data.get('execution_id'),
            variable_name=data.get('variable_name'),
            variable_value=json.dumps(data.get('variable_value')),
            data_type=data.get('data_type', 'string'),
            source_step_index=data.get('source_step_index', 0),
            source_api_method=data.get('source_api_method'),
            source_api_params=json.dumps(data.get('source_api_params', {})),
            is_encrypted=data.get('is_encrypted', False)
        )
    
    def get_typed_value(self):
        """根据数据类型返回正确类型的值"""
        if not self.variable_value:
            return None
            
        value = json.loads(self.variable_value)
        
        if self.data_type == 'number':
            return float(value) if isinstance(value, (int, float)) else value
        elif self.data_type == 'boolean':
            return bool(value) if isinstance(value, bool) else value
        elif self.data_type in ['object', 'array']:
            return value  # 已经是解析后的Python对象
        else:
            return str(value)  # string类型或其他
    
    def validate(self):
        """验证数据完整性"""
        errors = []
        
        if not self.execution_id:
            errors.append("execution_id是必需的")
        
        if not self.variable_name:
            errors.append("variable_name是必需的")
        
        if not self.data_type:
            errors.append("data_type是必需的")
        
        if self.data_type not in ['string', 'number', 'boolean', 'object', 'array']:
            errors.append(f"不支持的数据类型: {self.data_type}")
        
        if self.source_step_index < 0:
            errors.append("source_step_index必须是非负整数")
        
        return errors
    
    @classmethod
    def get_by_execution(cls, execution_id: str):
        """获取指定执行的所有变量"""
        return cls.query.filter_by(execution_id=execution_id).order_by(cls.source_step_index).all()
    
    @classmethod
    def get_variable(cls, execution_id: str, variable_name: str):
        """获取指定变量"""
        return cls.query.filter_by(execution_id=execution_id, variable_name=variable_name).first()

class VariableReference(db.Model):
    """变量引用模型 - 跟踪变量在测试步骤中的使用情况"""
    __tablename__ = 'variable_references'
    
    id = db.Column(db.Integer, primary_key=True)
    execution_id = db.Column(db.String(50), db.ForeignKey('execution_history.execution_id'), nullable=False)
    step_index = db.Column(db.Integer, nullable=False)  # 使用变量的步骤
    variable_name = db.Column(db.String(255), nullable=False)  # 引用的变量名
    reference_path = db.Column(db.String(500))  # 引用路径，如 product_info.price
    parameter_name = db.Column(db.String(255))  # 使用变量的参数名
    original_expression = db.Column(db.String(500))  # 原始引用表达式 ${product_info.price}
    resolved_value = db.Column(db.Text)  # 解析后的值
    resolution_status = db.Column(db.String(20), default='success')  # success, failed, pending
    error_message = db.Column(db.Text)  # 解析错误信息
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 复合索引
    __table_args__ = (
        db.Index('idx_reference_execution_step', 'execution_id', 'step_index'),
        db.Index('idx_reference_variable', 'execution_id', 'variable_name'),
        db.Index('idx_reference_status', 'execution_id', 'resolution_status'),
    )
    
    # 关系
    execution = db.relationship('ExecutionHistory', backref=db.backref('variable_references', lazy=True))
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'execution_id': self.execution_id,
            'step_index': self.step_index,
            'variable_name': self.variable_name,
            'reference_path': self.reference_path,
            'parameter_name': self.parameter_name,
            'original_expression': self.original_expression,
            'resolved_value': self.resolved_value,
            'resolution_status': self.resolution_status,
            'error_message': self.error_message,
            'created_at': self.created_at.strftime('%Y-%m-%dT%H:%M:%S.%fZ') if self.created_at else None
        }
