from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('blog/', views.post_list, name='post_list'),
    path('blog/<slug:slug>/', views.post_detail, name='post_detail'),
    path('category/<slug:slug>/', views.category_detail, name='category_detail'),
    path('contact/', views.contact, name='contact'),
    path('about/', views.about, name='about'),
    path('newsletter/subscribe/', views.newsletter_subscribe, name='newsletter_subscribe'),
]
