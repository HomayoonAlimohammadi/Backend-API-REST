from rest_framework import mixins, viewsets, authentication, permissions
from core import models
from recipe.serializers import (IngredientSerializer, RecipeDetailSerializer,
                                TagSerializer,
                                RecipeSerializer)


class RecipeAttributesViewSets(viewsets.GenericViewSet,
                               mixins.ListModelMixin,
                               mixins.CreateModelMixin,
                               mixins.UpdateModelMixin,
                               mixins.RetrieveModelMixin,
                               mixins.DestroyModelMixin):
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]    

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user) 


class TagAPIViewSets(RecipeAttributesViewSets):
    '''
    Tag API ViewSets for Listing and Creating
    '''
    queryset = models.Tag.objects.all()
    serializer_class = TagSerializer

    def perform_create(self, serializer):

        tag_names = [tag.name for tag in self.request.user.tags.all()]

        if serializer.validated_data['name'] in tag_names:
            msg = 'Duplicate Tags can not be created by the same user'
            raise ValueError(msg)

        serializer.save(user=self.request.user)


class IngredientsAPIViewSets(RecipeAttributesViewSets):
    '''
    Ingredients API ViewSets for Listing, and CRUD Operations
    '''
    queryset = models.Ingredient.objects.all()
    serializer_class = IngredientSerializer

    def perform_create(self, serializer):

        ingrd_related_qs = self.request.user.ingredients.all()
        ingrd_names = [ingrd.name for ingrd in ingrd_related_qs]

        if serializer.validated_data['name'] in ingrd_names:
            msg = 'Duplicate Ingredients can not be created by the same user'
            raise ValueError(msg)

        serializer.save(user=self.request.user)


class RecipeViewSets(viewsets.ModelViewSet):
    '''
    Recipe API ViewSets for Listing and CRUS Operations
    '''
    queryset = models.Recipe.objects.all()
    serializer_class = RecipeSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return RecipeDetailSerializer
        
        return self.serializer_class

    def perform_create(self, serializer):

        recipe_related_qs = self.request.user.recipes.all()
        recipe_titles = [recipe.title for recipe in recipe_related_qs]

        if serializer.validated_data['title'] in recipe_titles:
            msg = 'Duplicate Recipes can not be created by the same user'
            raise ValueError(msg)

        serializer.save(user=self.request.user)

    # def perform_create(self, serializer):
    #     '''
    #     Adding Recipe and Ingredients from database or creating them
    #     if not available.
    #     Also setting the recipe user as the request user
    #     '''
    #     recipe_related_qs = self.request.user.recipes.all()
    #     recipe_names = [recipe.name for recipe in recipe_related_qs]

    #     if serializer.validated_data['name'] in recipe_names:
    #         msg = 'Recipes can not have duplicate names'
    #         raise ValueError(msg)

    #     for tag_name in serializer.validated_data['tags']:

    #         tag = models.Tag.objects.filter(
    #             name=tag_name,
    #             user=self.request.user
    #             ).first()
            
    #         if not tag:
    #             tag = models.Tag.objects.create(
    #                 name=tag_name,
    #                 user=self.request.user
    #             )
            
    #         tag_serialized = TagSerializer(tag).data
    #         serializer.validated_data['tags'] += tag_serialized

    #     for ingredient_name in serializer.validated_data['ingredients']:

    #         ingredient = models.Ingredient.objects.filter(
    #             name=ingredient_name,
    #             user=self.request.user
    #         ).first()

    #         if not ingredient:
    #             ingredient = models.Ingredient.create(
    #                 name=ingredient_name,
    #                 user=self.request.user
    #             )
            
    #         ingredient_serialized = IngredientSerializer(ingredient).data
    #         serializer.validated_data['ingredients'] += ingredient_serialized

    #     serializer.save(user=self.request.user)