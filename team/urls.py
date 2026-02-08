from django.urls import path
from . import views

app_name = 'team'

urlpatterns = [
    path('dashboard/', views.user_dashboard, name='dashboard'),
    path('', views.team_list, name='list'),
    path('create/', views.team_create, name='create'),
    path('<int:pk>/update/', views.team_update, name='update'),
    path('<int:pk>/', views.team_detail, name='detail'),
    path('<int:pk>/members/', views.team_members, name='members'),
    path('<int:team_pk>/members/create/', views.team_member_create, name='member_create'),
    path('members/<int:pk>/', views.team_member_detail, name='member_detail'),
    path('questionnaires/', views.questionnaire_staff_list, name='questionnaire_staff_list'),
    path('questionnaires/create/', views.questionnaire_create_global, name='questionnaire_create_global'),
    path('members/<int:member_pk>/questionnaires/', views.questionnaire_list, name='questionnaire_list'),
    path('members/<int:member_pk>/questionnaires/create/', views.questionnaire_create, name='questionnaire_create'),
    path('questionnaires/<int:pk>/', views.questionnaire_detail, name='questionnaire_detail'),
    path('questionnaires/<int:pk>/update/', views.questionnaire_update, name='questionnaire_update'),
    path('questionnaires/<int:pk>/delete/', views.questionnaire_delete, name='questionnaire_delete'),
    path('questionnaires/<int:pk>/respond/', views.questionnaire_respond, name='questionnaire_respond'),
    path('members/<int:pk>/update/', views.team_member_update, name='member_update'),
    path('members/<int:pk>/delete/', views.team_member_delete, name='member_delete'),
    path('payments/', views.payment_list, name='payment_list'),
    path('payments/create/', views.payment_create, name='payment_create'),
    path('payments/<int:pk>/update/', views.payment_update, name='payment_update'),
    path('payments/<int:pk>/delete/', views.payment_delete, name='payment_delete'),
    path('trainings/', views.training_list, name='training_list'),
    path('trainings/create/', views.training_create, name='training_create'),
    path('trainings/<int:pk>/update/', views.training_update, name='training_update'),
    path('trainings/<int:pk>/delete/', views.training_delete, name='training_delete'),
    path('trainings/weekly/', views.training_weekly, name='training_weekly'),
    path('trainings/<int:pk>/edit-inline/', views.training_edit_inline, name='training_edit_inline'),
    path('trainings/<int:pk>/view-inline/', views.training_view_inline, name='training_view_inline'),
    path('trainings/<int:pk>/delete-inline/', views.training_delete_inline, name='training_delete_inline'),
    path('trainings/create-inline/', views.training_create_inline, name='training_create_inline'),
]