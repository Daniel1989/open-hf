
### 2. 数据获取层 (data_acquisition.py)

# data_engine/data_acquisition.py
import pandas as pd
from django.db import connections
from .models import DataSource

class DataFetcher:
    """统一数据获取接口"""
    def __init__(self, source_name):
        self.source = DataSource.objects.get(name=source_name)
        self.conn = None
        
    def __enter__(self):
        if self.source.source_type == 'database':
            self.conn = connections[self.source.config['connection']]
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.conn:
            self.conn.close()
    
    def fetch_ohlcv(self, symbol, start, end):
        """获取OHLCV数据"""
        if self.source.source_type == 'database':
            return self._fetch_from_sql(symbol, start, end)
        elif self.source.source_type == 'csv':
            return self._fetch_from_csv(symbol, start, end)
        elif self.source.source_type == 'api':
            return self._fetch_from_api(symbol, start, end)
    
    def _fetch_from_sql(self, symbol, start, end):
        query = f"""
            SELECT dt, open, high, low, close, volume 
            FROM {self.source.config['table']}
            WHERE symbol = %s AND dt BETWEEN %s AND %s
        """
        with self.conn.cursor() as cursor:
            cursor.execute(query, [symbol, start, end])
            return pd.DataFrame(
                cursor.fetchall(),
                columns=['timestamp', 'open', 'high', 'low', 'close', 'volume']
            )
    
    def _fetch_from_csv(self, symbol, start, end):
        # CSV文件路径模板配置
        path = self.source.config['path_template'].format(
            symbol=symbol,
            date=start.strftime('%Y%m%d')
        )
        return pd.read_csv(path, parse_dates=['timestamp'])
    
    def _fetch_from_api(self, symbol, start, end):
        # 实现API调用逻辑
        pass
