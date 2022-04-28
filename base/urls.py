from django.urls import path
from .views import CustomLoginView ,RegisterPage, HomeView, StartArcadeView, ArcadeView
from django.contrib.auth.views import LogoutView
from django.contrib.staticfiles.urls import staticfiles_urlpatterns


urlpatterns = [
    path('login/', CustomLoginView.as_view(),name='login'),
    path('register/', RegisterPage.as_view(), name='register'),
    path('logout/', LogoutView.as_view(next_page="login"), name='logout'),
    path('', HomeView.as_view(),name='home'),
    path('startarcade/plan/<int:plan>/subject/<int:subject>', StartArcadeView.as_view(),name='startarcade'),
    path('startarcade/plan/<int:plan>/subject/<int:subject>/session/<int:session>', StartArcadeView.as_view(),name='startarcade'),
    path('arcade/<session>/', ArcadeView.as_view(),name='arcade'),
    path('arcade/<session>/<subjectSlug>', ArcadeView.as_view(),name='arcade'),
    path('arcade/<session>/<subjectSlug>/<direction>', ArcadeView.as_view(),name='arcade'),
]

urlpatterns += staticfiles_urlpatterns()