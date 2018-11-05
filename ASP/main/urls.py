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

    ###FOR PARTIAL EXECUTABLE ONLY##
    url(r'^logincm1$', views.loginSimulationCM1),
    url(r'^logincm2$', views.loginSimulationCM2),
    url(r'^logincm3$', views.loginSimulationCM3),
    url(r'^logincm4$', views.loginSimulationCM4),
    url(r'^logincm5$', views.loginSimulationCM5),
    url(r'^logindp1$', views.loginSimulationDP1),


    url(r'^cm_home$', views.onlineOrder, name='cm_home'),
    url(r'^cm_cart$', views.cm_cart, name='cm_cart'),
    url(r'^submitorder$', views.submitorder, name='submitorder'),
    url(r'^dp_dashboard$', views.dp_dashboard, name='dp_dashboard'),
    url(r'^dp_session$', views.dp_session, name='dp_session'),
    url(r'^itinerary_download$', views.itineraryDownload, name='itinerary_download'),
    url(r'^close_session$', views.dp_close_session, name='dp_close_session'),
]
#urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)