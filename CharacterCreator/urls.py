from django.urls import path

from . import views

urlpatterns = [
    path('', views.search, name='index'),
    # path('search/', views.search, name='search'),
    # # path('results/', views.CharacterTableView.as_view(), name='results'),
    # path('defstat/', views.get_default_statistic, name='get_default_statistic'),
    # path('statnames/', views.manage_statistic_names, name='manage_statistic_names'),
    # path('statentry/', views.multi_statistic, name='multi_statistic'),
    path('char/<int:character_id>/', views.character, name='character'),
    path('npc/<int:npc_id>/', views.npc, name='npc'),
]
