
### 2. `calculate_factors` 命令实现
# data_engine/management/commands/calculate_factors.py
from django.core.management.base import BaseCommand
from data_engine.models import FactorDefinition, MarketData
from data_engine.data_processing import FactorCalculator
import pandas as pd
class Command(BaseCommand):
    help = '计算指定因子的历史值'
    
    def add_arguments(self, parser):
        parser.add_argument('--factor', type=str, required=True, help="因子名称")
        parser.add_argument('--start', type=str, help="开始日期（YYYYMMDD）")
        parser.add_argument('--symbol', type=str, help="限定标的代码")

    def handle(self, *args, **options):
        try:
            factor = FactorDefinition.objects.get(name=options['factor'])
            qs = MarketData.objects.all()
            
            if options['start']:
                qs = qs.filter(timestamp__date__gte=options['start'])
            if options['symbol']:
                qs = qs.filter(symbol=options['symbol'])
                
            data_df = pd.DataFrame.from_records(qs.values())
            
            calculator = FactorCalculator(factor)
            result_df = calculator.calculate(data_df)
            FactorCalculator.save_factor_values(result_df)
            
            self.stdout.write(
                self.style.SUCCESS(f"成功计算 {len(result_df)} 条因子值")
            )
        except FactorDefinition.DoesNotExist:
            self.stderr.write(self.style.ERROR("因子不存在"))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"计算失败: {str(e)}"))
