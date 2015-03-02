from django.conf.urls import patterns, url
from ActividadesClinicas.views import InterrogatorioPDF
from Inventario.views import ProductosPDF

urlpatterns = patterns('ActividadesClinicas.views',

    url(r'^$', 'inicio'),
    url(r'^interrogatorio/$', 'HistoriaClinicaView'),
 		url(r'^odontograma/(?P<paciente_id>\d+)$', 'odontograma'),
    url(r'^diagnosticos/$', 'diagnosticos'),
    url(r'^evaluacion/$', 'buscarpaciente'),
    url(r'^detalles/$', 'detallespaciente'),

)

urlpatterns += patterns('',

    #Reportes PDF
    url(r'^productos/pdf/$',ProductosPDF.as_view()),
    url(r'^interrogatorios/pdf/$',InterrogatorioPDF.as_view()),

)