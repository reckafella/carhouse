"""
URL configuration for carhouse project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
# from django.conf.urls import handler404, handler500, handler403, handler400
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
import django.contrib.auth.urls as django_auth_urls
from wagtail.admin import urls as wagtailadmin_urls
from wagtail import urls as wagtail_urls
from wagtail.documents import urls as wagtaildocs_urls

from app.views.views import CustomRedirectView
from app.views.captcha.captcha import CaptchaRefreshView

redirect_to = CustomRedirectView.as_view(redirect_to='/login', permanent=True)

urlpatterns = [
    path('admin/login/', redirect_to),
    path('admin/', admin.site.urls),
    path('accounts/', include(django_auth_urls)),
    path('wagtail/admin/login', redirect_to),
    path('wagtail/admin/', include(wagtailadmin_urls)),
    path('documents/', include(wagtaildocs_urls)),
    path('wagtail/', include(wagtail_urls)),
    path('wagtail/login', redirect_to),
    path('robots.txt', include('robots.urls')),
    path('', include('app.urls')),
    path('', include('auth.urls')),
    path('captcha/refresh/', CaptchaRefreshView.as_view(),
         name='captcha-refresh'),
    path('captcha/', include('captcha.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
