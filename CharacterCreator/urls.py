from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('char/<int:character_id>/', views.character, name='character'),
    path('npc/<int:npc_id>/', views.npc, name='npc'),
]


