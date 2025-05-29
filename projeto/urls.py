from django.contrib import admin
from django.urls import path, include
from django.views.generic.base import RedirectView
from django.urls import path
from projeto.core import views as my_views

urlpatterns = [
    # redireciona o admin/login para o seu login customizado
    path('admin/login/', RedirectView.as_view(url='/accounts/login/', permanent=False)),

    path('accounts/', include('django.contrib.auth.urls')),  # login, logout, password reset etc.
    path('accounts/signup/', my_views.signup_view, name='signup'),

    path('admin/', admin.site.urls),

    # sua URL raiz
    path('', RedirectView.as_view(url='/admin/', permanent=False)),
]
