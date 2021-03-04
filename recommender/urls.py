from django.urls import path
from . import views

app_name = 'recommender'

urlpatterns = [
    path('best/', views.searchform_get, name='best'),
    path('bestp/', views.searchform_post, name='bestp'),
    path('curator/', views.curator_get, name='curator'),
    path('curatorp/', views.curator_post, name='curatorp')
]
