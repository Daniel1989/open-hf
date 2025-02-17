
### 3. 数据校验模块 (data_validation.py)

# data_engine/data_validation.py
from django.core.exceptions import ValidationError
from .models import MarketData

class DataValidator:
    """数据质量校验器"""
    @staticmethod
    def validate_ohlcv(df):
        """校验OHLCV数据"""
        required_cols = ['open', 'high', 'low', 'close', 'volume']
        if not all(col in df.columns for col in required_cols):
            raise ValidationError("Missing required columns")
        
        # 检查时间戳顺序
        if not df['timestamp'].is_monotonic_increasing:
            raise ValidationError("Timestamp not in order")
        
        # 价格合理性检查
        price_check = (
            (df['high'] >= df['low']) &
            (df['high'] >= df['close']) &
            (df['low'] <= df['open'])
        )
        if not price_check.all():
            raise ValidationError("Invalid price values")
        
        # 成交量非负检查
        if (df['volume'] < 0).any():
            raise ValidationError("Negative volume values")
        
        return df.drop_duplicates('timestamp')

class FactorValidator:
    """因子数据校验"""
    @staticmethod
    def validate_factor(factor_def):
        # 检查公式语法
        try:
            compile(factor_def.formula, '<string>', 'exec')
        except SyntaxError as e:
            raise ValidationError(f"Invalid formula syntax: {e}")
        
        # 检查依赖字段是否存在
        for dep in factor_def.dependencies:
            if dep not in MarketData._meta.get_all_field_names():
                raise ValidationError(f"Invalid dependency: {dep}")
