from rest_framework import mixins, viewsets, authentication, permissions
from core import models
from recipe.serializers import IngredientSerializer, TagSerializer


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