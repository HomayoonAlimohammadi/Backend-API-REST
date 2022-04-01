from rest_framework import mixins, viewsets, authentication, permissions
from core import models
from recipe.serializers import TagSerializer


class TagAPIViewSets(viewsets.GenericViewSet, mixins.ListModelMixin):

    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    queryset = models.Tag.objects.all()
    serializer_class = TagSerializer

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user) 