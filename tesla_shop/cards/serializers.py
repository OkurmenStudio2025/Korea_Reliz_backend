from rest_framework import serializers
from .models import Category, Product, Marka

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class MarkaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Marka
        fields = '__all__'

class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.SerializerMethodField() 

    class Meta:
        model = Product
        fields = '__all__'

    def get_category_name(self, obj):
        return obj.category.category  
