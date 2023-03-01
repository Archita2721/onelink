from django.urls import path
from .views import *;
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path('', homepage, name = 'homepage'),  
    path('homepage', homepage, name = 'homepage'),  
    path('register/', register, name = 'register'),  
    path('activate/<uidb64>/<token>', activate, name='activate'),
    path("login",login_request,name="login"),
    path("logout", logout_request, name= "logout"),
    path("password_reset", password_reset_request, name="password_reset"),
    path('redirect/',redirect ,name='redirect'),
    path('url',url ,name='url'),
    path('urls/<int:id>',urls ,name='urls'),
    path('url/<int:id>',url ,name='url'),
    path('<str:short_code>/', redirect_short_url, name='short_url'),
   
    #path('redirect_to_app_store/<str:android_link>/<str:ios_link>/', redirect_to_app_store, name='redirect_to_app_store'),

    
]
if settings.DEBUG:
        urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)