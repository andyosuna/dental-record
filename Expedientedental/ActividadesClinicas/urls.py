from django.conf.urls import patterns, url

urlpatterns = patterns('ActividadesClinicas.views',

    url(r'^$', 'inicio'),
    url(r'^interrogatorio/$', 'HistoriaClinica'),
    url(r'^odontograma/$', 'odontograma'),
    url(r'^diagnosticos/$', 'diagnosticos'),

)
