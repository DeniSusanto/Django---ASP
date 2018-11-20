from django.urls import include
from django.conf import settings
from django.conf.urls import url
from django.conf.urls.static import static
from . import views

urlpatterns = [

    ###pls delete###
    url(r'^boredaf$', views.boredaf),
    url(r'^debug$', views.debug),
    ###pls delete###

    #General
    url(r'registration$',views.registration),
    url(r'^login$', views.loginSession, name='loginSession'),
    url(r'^logout$', views.logout, name='logout'),

    #CM
    url(r'^cm_home$', views.onlineOrder, name='cm_home'),
    url(r'^cm_cart$', views.cm_cart, name='cm_cart'),
    url(r'^submitorder$', views.submitorder, name='submitorder'),
    url(r'^myorders$', views.myorders, name='myorders'),
    url(r'^deleteOrder$', views.deleteOrder, name='deleteOrder'),
    url(r'^confirmReceived$', views.confirmReceived, name='confirmReceived'),

    #WP
    url(r'^wp_home$', views.wp_home, name='wp_home'),
    url(r'^order_details$', views.order_details, name='order_details'),
    url(r'^pdf_download$', views.pdf_download, name='pdf_download'),

    #DP
    url(r'^dp_dashboard$', views.dp_dashboard, name='dp_dashboard'),
    url(r'^dp_session$', views.dp_session, name='dp_session'),
    url(r'^itinerary_download$', views.itineraryDownload, name='itinerary_download'),
    url(r'^close_session$', views.dp_close_session, name='dp_close_session'),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
