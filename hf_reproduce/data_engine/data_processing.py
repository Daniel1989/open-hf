
### 4. 数据处理管道 (data_processing.py)

# data_engine/data_processing.py
import numpy as np
from django.db import transaction
from .models import MarketData, FactorValue
import pandas as pd

class DataProcessor:
    """数据清洗处理管道"""
    @staticmethod
    def clean_ohlcv_data(raw_df):
        """数据清洗逻辑"""
        df = raw_df.copy()
        
        # 处理缺失值
        df = df.ffill().bfill()
        
        # 去除异常值
        df = df[(df['high'] - df['low']) < (df['close'].rolling(5).std() * 3)]
        
        # 生成时间序列索引
        df = df.set_index('timestamp').asfreq('1T').reset_index()
        
        return df

    @classmethod
    @transaction.atomic
    def bulk_save_market_data(cls, symbol, cleaned_df):
        """批量存储清洗后的数据"""
        objs = [
            MarketData(
                symbol=symbol,
                timestamp=row['timestamp'],
                open=row['open'],
                high=row['high'],
                low=row['low'],
                close=row['close'],
                volume=row['volume'],
                turnover=row.get('turnover', 0),
                bid_ask=row.get('bid_ask')
            )
            for _, row in cleaned_df.iterrows()
        ]
        MarketData.objects.bulk_create(objs, batch_size=1000)

class FactorCalculator:
    """因子计算引擎"""
    def __init__(self, factor_def):
        self.factor_def = factor_def
        self.context = {
            'np': np,
            'pd': pd,
            'log': np.log,
            'rolling_mean': lambda x, w: x.rolling(w).mean()
        }
    
    def calculate(self, data_df):
        """执行因子计算"""
        try:
            # 动态执行计算公式
            exec(self.factor_def.formula, self.context)
            result = self.context['result']
            
            # 转换为标准格式
            return pd.DataFrame({
                'symbol': data_df['symbol'],
                'timestamp': data_df['timestamp'],
                'value': result.values
            })
        except Exception as e:
            raise RuntimeError(f"Factor calculation failed: {e}")

    @classmethod
    def save_factor_values(cls, factor_df):
        """存储因子计算结果"""
        objs = [
            FactorValue(
                factor=factor_df['factor'],
                symbol=row['symbol'],
                timestamp=row['timestamp'],
                value=row['value']
            )
            for _, row in factor_df.iterrows()
        ]
        FactorValue.objects.bulk_create(objs, ignore_conflicts=True)
