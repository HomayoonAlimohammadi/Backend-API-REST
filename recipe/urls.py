from django.urls import path, include
from recipe import views
from rest_framework.routers import DefaultRouter


app_name = 'recipe'

router = DefaultRouter()
router.register('tags', views.TagAPIViewSets)
router.register('ingredients', views.IngredientsAPIViewSets)
router.register('recipes', views.RecipeViewSets)

urlpatterns = [
    path('', include(router.urls))
]