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

    class Meta:
        model = models.Recipe
        fields = ['id', 'name', 'ingredients', 'tags']
        read_only_fields = ['id']    