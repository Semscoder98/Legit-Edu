from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('blog.urls')),
    path('scholarship/', include('scholarship.urls')),
    path('accounts/', include('accounts.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('api/', include('blog.api_urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = 'blog.views.error_404'
handler500 = 'blog.views.error_500'

handler400 = 'blog.views.error_400'
handler403 = 'blog.views.error_403'
