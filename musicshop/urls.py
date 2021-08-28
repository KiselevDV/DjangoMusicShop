from django.urls import path

from .views import (
    LoginView, RegistrationView, BaseView, ArtistDetailView, AlbumDetailView,
)

urlpatterns = [
    path('<str:artist_slug>/<str:album_slug>/', AlbumDetailView.as_view(),
         name='album_detail'),
    path('<str:artist_slug>/', ArtistDetailView.as_view(), name='artist_detail'),

    path('registration/', RegistrationView.as_view(), name='registration'),
    path('login/', LoginView.as_view(), name='login'),

    path('', BaseView.as_view(), name='base')
]
