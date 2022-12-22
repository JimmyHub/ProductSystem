# from drf_yasg import openapi

from .models import ProductProfile, ProductManager, ProductReceipt
from rest_framework import serializers


class ProductSerializer(serializers.HyperlinkedModelSerializer):

    def create(self, validated_data):
        return ProductProfile.objects.create(**validated_data)

    class Meta:
        model = ProductProfile
        fields = "__all__"
        # 這個欄位 的設定部分 會影響在 openapi 的 model 提示有關
        # fields = ('pname', 'pkind', 'pprice')


class PmanagerSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ProductManager
        fields = "__all__"


class PreceiptSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ProductReceipt
        fields = "__all__"
