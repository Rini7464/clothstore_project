from django.urls import path 
from clothstore_app import views
from django.conf.urls.static import static
from clothstore import settings

urlpatterns = [
    path('create',views.create),
    path('home',views.home),
    path('pdetails/<pid>',views.product_details),
    path('register',views.register),
    path('contact',views.contact),
    path('about',views.about),
    path('login',views.user_login),
    path('logout',views.user_logout),
    path('logout',views.user_logout),
    path('catfilter/<cv>',views.catfilter),
    path('colorfilter/<cv>',views.colorfilter),
    path('brandfilter/<cv>',views.brandfilter),
    path('sort/<sv>',views.sort),
    path('range', views.range),
    path('addtocart/<pid>',views.addtocart),
    path('viewcart',views.viewcart),
    path('remove/<cid>',views.remove),
    path('updateqty/<qv>/<cid>',views.updateqty),
    path('placeorder',views.placeorder),
    path('makepayment',views.makepayment),
    path('sendmail/<uemail>',views.sendusermail),
    
] 


if settings.DEBUG:
    urlpatterns +=static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)