from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile_view, name='profile'),
    path('logout/', views.logout_view, name='logout'),
    path('add_workout/', views.add_workout, name='add_workout'),
    path('add_stats/', views.add_stats, name='add_stats'),
    path('add_goal/', views.add_goal, name='add_goal'),
    path('profile/', views.profile_view, name='profile'),
    path('add_food/', views.add_food, name='add_food'),
    path('delete_food/<int:food_id>/', views.delete_food, name='delete_food'),
    path('delete-workout/<int:id>/', views.delete_workout, name='delete_workout'),
]
