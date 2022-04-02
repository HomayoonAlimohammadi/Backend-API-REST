from rest_framework import mixins, viewsets, authentication, permissions
from core import models
from recipe.serializers import TagSerializer


class TagAPIViewSets(viewsets.GenericViewSet,
                     mixins.ListModelMixin,
                     mixins.CreateModelMixin):
    '''
    Tag API ViewSets for Listing and Creating
    '''
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    queryset = models.Tag.objects.all()
    serializer_class = TagSerializer

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user) 

    def perform_create(self, serializer):

        tag_names = [tag.name for tag in self.request.user.tags.all()]
        msg = 'Tags with duplicate names can not be created for the same user'

        if serializer.validated_data['name'] in tag_names:
            raise ValueError(msg)

        serializer.save(user=self.request.user)