from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("about/", views.about, name="about"),
    path("contact/", views.contact, name="contact"),
    path("thankyou/", views.thankyou, name="thankyou"),
    # Blog (la búsqueda es el mismo listado con ?searchTerm=...)
    path("blog/", views.blog_list, name="blog"),
    path("blog/new/", views.new_post, name="new_post"),
    path("single_post/<slug:slug>/", views.single_post, name="single_post"),
    path("single_post/<slug:slug>/like/", views.post_like, name="post_like"),
    # Autenticación
    path("login/", auth_views.LoginView.as_view(), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("register/", views.register, name="register"),
    # Administración
    path("admin/images/", views.admin_images, name="app_images"),
    path("admin/categories/", views.admin_categories, name="app_categories"),
]
