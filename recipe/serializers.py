from rest_framework import serializers
from core import models


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Tag
        fields = ['id', 'name']
        read_only_fields = ['id']


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Ingredient
        fields = ['id', 'name']
        read_only_fields = ['id']


class RecipeSerializer(serializers.ModelSerializer):

    ingredients = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=models.Ingredient.objects.all()
    )
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=models.Tag.objects.all()
    )

    class Meta:
        model = models.Recipe
        fields = ['id', 'title', 'ingredients', 
                  'tags', 'time_minutes', 'price', 'link']
        read_only_fields = ['id'] 
        # depth = 1   