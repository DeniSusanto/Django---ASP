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
    url(r'^order_record$', views.orderRecords, name='order_record'),
    url(r'^change_password$', views.change_password, name='change_password'),
    url(r'^forget_password$', views.forget_password, name='forget_password'),
    url(r'^reset_password$', views.reset_password, name='reset_password'),
    #url(r'^email_close_session$', views.email_close_session, name='email_close_session'),
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
