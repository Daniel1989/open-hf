
### 1. 在`data_engine`应用中创建`urls.py`

# data_engine/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api import MarketDataViewSet, FactorDataAPI

router = DefaultRouter()
router.register(r'market-data', MarketDataViewSet, basename='marketdata')

urlpatterns = [
    path('', include(router.urls)),
    
    # 自定义因子值端点
    path('factors/<str:name>/values/',
         FactorDataAPI.as_view({'get': 'get_factor_values'}),
         name='factor-values'),
]
