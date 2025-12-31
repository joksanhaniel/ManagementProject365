"""
URL configuration for mpp365_system project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.views import LogoutView
from proyectos import views as proyectos_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    # Landing page principal con planes
    path('', proyectos_views.landing, name='landing'),

    # Login y autenticación
    path('login/', proyectos_views.CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='/'), name='logout'),

    # Registro público (SaaS)
    path('registro/', proyectos_views.registro_publico, name='registro_publico'),
    path('terminos-condiciones/', proyectos_views.terminos_condiciones, name='terminos_condiciones'),

    # Selección de empresa (solo para superusuarios)
    path('seleccionar-empresa/', proyectos_views.seleccionar_empresa, name='seleccionar_empresa'),

    # Confirmar pagos (solo para superusuarios) - URL global sin empresa
    path('pagos/confirmar/', proyectos_views.confirmar_pagos, name='confirmar_pagos_global'),

    # URLs con prefijo de empresa
    path('<str:empresa_codigo>/', include('proyectos.urls')),

    path('api-auth/', include('rest_framework.urls')),
]

# Servir archivos media en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
