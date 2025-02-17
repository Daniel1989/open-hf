
### 5. API接口 (api.py)

# data_engine/api.py
from rest_framework import serializers, viewsets
from rest_framework.response import Response
from .models import MarketDataV2, FactorDefinition, FactorValue
from rest_framework.decorators import action

class MarketDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = MarketDataV2
        fields = '__all__'
        read_only_fields = ['id']

class MarketDataViewSet(viewsets.ReadOnlyModelViewSet):
    """行情数据API"""
    serializer_class = MarketDataSerializer
    filterset_fields = ['symbol', 'timestamp__gte', 'timestamp__lte']
    
    def get_queryset(self):
        return MarketDataV2.objects.all().order_by('timestamp')
    
    

class FactorDefinitionSerializer(serializers.ModelSerializer):
    class Meta:
        model = FactorDefinition
        fields = '__all__'

class FactorValueSerializer(serializers.ModelSerializer):
    class Meta:
        model = FactorValue
        fields = ['timestamp', 'value', 'symbol']

class FactorDataAPI(viewsets.ModelViewSet):
    """因子数据API"""
    queryset = FactorDefinition.objects.all()
    serializer_class = FactorDefinitionSerializer
    
    @action(detail=True, methods=['GET'])
    def get_factor_values(self, request, pk=None):
        """获取特定因子的值"""
        factor = self.get_object()
        symbol = request.query_params.get('symbol')
        
        queryset = FactorValue.objects.filter(factor=factor)
        if symbol:
            queryset = queryset.filter(symbol=symbol)
            
        page = self.paginate_queryset(queryset)
        serializer = FactorValueSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)
