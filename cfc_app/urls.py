"""Defines URL patterns for this application"""

from django.urls import path
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from . import views

app_name = 'cfc_app'

urlpatterns = [
    # Home page
    path('', views.index, name='index'),

    # Page that shows all locations.
    path('locations/', views.locations, name='locations'),

    # Page that shows all impacts.
    path('impacts/', views.impacts, name='impacts'),

    # Page for starting a search
    path('search/', views.search, name='search'),

    # Page for updating a search template (states)
    path('search/stateload', views.load_state, name='stateload'),

    # Page for updating a search template (county)
    path('search/countyload', views.load_county, name='countyload'),

    # Page for updating a search template (city)
    path('search/cityload', views.load_city, name='cityload'),

    # Page for showing search results
    path('results/<int:search_id>/',
         views.results, name='results'),

    # Page for showing search criteria
    path('criteria/<int:search_id>/',
         views.criteria, name='criteria'),

    # Page for showing saved search critera
    path('criterias/', views.criterias, name='criterias'),

    # Page for sending saved search critera via email
    path('sendmail/<int:search_id>/', views.sendmail, name='sendmail'),

    # Page for sending saved search critera via email
    path('download/<int:search_id>/', views.download, name='download'),

    # Page for dumping curated laws into CSV file
    path('lawdump/', views.lawdump, name='lawdump'),

    # health endpoint
    path('health/', views.health, name='health'),
]
