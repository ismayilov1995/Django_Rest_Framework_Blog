from django.urls import path

from favorite.api.views import FavoriteListCreateAPIView, FavoriteAPIView

app_name = "favorite"
urlpatterns = [
    path('list-create/', FavoriteListCreateAPIView.as_view(), name='list-create'),
    path('update-delete/<pk>/', FavoriteAPIView.as_view(), name='update-delete'),
]
