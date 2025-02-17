
### 1. 数据模型定义 (models.py)
# data_engine/models.py
from django.db import models
from django.contrib.postgres.fields import ArrayField
# from timescale.db.models.models import TimescaleModel
from timescale.db.models.fields import TimescaleDateTimeField
from timescale.db.models.managers import TimescaleManager

class DataSource(models.Model):
    """数据源配置"""
    name = models.CharField(max_length=50, unique=True)
    source_type = models.CharField(max_length=20, choices=[
        ('database', '数据库'),
        ('csv', 'CSV文件'),
        ('api', 'API接口')
    ])
    config = models.JSONField(verbose_name="连接配置")
    last_updated = models.DateTimeField(null=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "数据源配置"

class MarketDataV2(models.Model):
    """行情数据模型（使用TimescaleDB Hypertable）"""
    symbol = models.CharField(max_length=50, db_index=True)
    timestamp = models.DateTimeField()
    open = models.DecimalField(max_digits=18, decimal_places=4)
    high = models.DecimalField(max_digits=18, decimal_places=4)
    low = models.DecimalField(max_digits=18, decimal_places=4)
    close = models.DecimalField(max_digits=18, decimal_places=4)
    volume = models.BigIntegerField()
    turnover = models.DecimalField(max_digits=20, decimal_places=4)
    bid_ask = models.JSONField(verbose_name="买卖盘口", null=True)
    time = TimescaleDateTimeField(interval="7 day", db_index=True, primary_key=True)
    objects = models.Manager()
    timescale = TimescaleManager()
    class Meta:
        unique_together = (('symbol', 'time'),)  # 如果使用复合主键
        verbose_name = "行情数据"

class FactorDefinition(models.Model):
    """因子定义模型"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    formula = models.TextField(verbose_name="计算公式")
    parameters = models.JSONField(blank=True, null=True)
    update_frequency = models.CharField(max_length=20, choices=[
        ('tick', '逐笔更新'),
        ('1min', '分钟级'),
        ('daily', '日频')
    ])
    dependencies = ArrayField(
        models.CharField(max_length=50),
        default=list,
        verbose_name="依赖字段"
    )

    def __str__(self):
        return f"{self.name} ({self.update_frequency})"

class FactorValue(models.Model):
    """因子值存储"""
    factor = models.ForeignKey(FactorDefinition, on_delete=models.CASCADE)
    symbol = models.CharField(max_length=20)
    timestamp = models.DateTimeField()
    value = models.FloatField()
    extra_data = models.JSONField(blank=True, null=True)

    class Meta:
        unique_together = [['factor', 'symbol', 'timestamp']]
        indexes = [
            models.Index(fields=['symbol', 'timestamp']),
        ]
