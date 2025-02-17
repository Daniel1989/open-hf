
### 1. `import_ohlcv` 命令实现
# data_engine/management/commands/import_ohlcv.py
from django.core.management.base import BaseCommand
from data_engine.data_acquisition import DataFetcher
from data_engine.data_processing import DataProcessor

class Command(BaseCommand):
    help = '从指定数据源导入OHLCV数据'
    
    def add_arguments(self, parser):
        parser.add_argument('source', type=str, help="数据源名称（在DataSource中配置）")
        parser.add_argument('symbol', type=str, help="合约代码")
        parser.add_argument('start_date', type=str, help="开始日期（YYYY-MM-DD）")
        parser.add_argument('end_date', type=str, help="结束日期（YYYY-MM-DD）")

    def handle(self, *args, **options):
        try:
            with DataFetcher(options['source']) as fetcher:
                raw_df = fetcher.fetch_ohlcv(
                    options['symbol'],
                    options['start_date'],
                    options['end_date']
                )
                
            cleaned_df = DataProcessor.clean_ohlcv_data(raw_df)
            DataProcessor.bulk_save_market_data(options['symbol'], cleaned_df)
            
            self.stdout.write(
                self.style.SUCCESS(f"成功导入 {len(cleaned_df)} 条数据")
            )
        except Exception as e:
            self.stderr.write(
                self.style.ERROR(f"导入失败: {str(e)}")
            )
