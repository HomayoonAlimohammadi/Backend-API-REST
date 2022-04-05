from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import (mixins, viewsets, authentication, 
                            permissions, status)
from core import models
from recipe.serializers import (IngredientSerializer, RecipeDetailSerializer, 
                                RecipeImageSerializer, TagSerializer,
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
        
        elif self.action == 'upload_image':
            return RecipeImageSerializer

        return self.serializer_class

    def perform_create(self, serializer):

        recipe_related_qs = self.request.user.recipes.all()
        recipe_titles = [recipe.title for recipe in recipe_related_qs]

        if serializer.validated_data['title'] in recipe_titles:
            msg = 'Duplicate Recipes can not be created by the same user'
            raise ValueError(msg)

        serializer.save(user=self.request.user)

    @action(methods=['POST'], detail=True, url_path='upload-image')
    def upload_image(self, request, pk=None):

        recipe = self.get_object()
        serializer = self.get_serializer(
            recipe,
            data=request.data
        )

        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )
        
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )