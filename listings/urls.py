from django.urls import path
from . import views

urlpatterns = [
    path('', views.agent_list, name='agent-list'),
    path('favorites/', views.favorite_list, name='favorite-list'),
    path('<str:mls_id>/', views.agent_detail, name='agent-detail'),
    path('<str:mls_id>/generate-email/', views.generate_email, name='generate-email'),
    path('<str:mls_id>/favorite/', views.add_favorite, name='add-favorite'),
    path('<str:mls_id>/unfavorite/', views.remove_favorite, name='remove-favorite'),
]
