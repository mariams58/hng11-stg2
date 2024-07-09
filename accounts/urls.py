from django.urls import path
from .views import RegisterView, LoginView, UserDetailView, UserOrganizationsView, OrganizationCreateView, OrganizationDetailView, AddUserToOrganizationView

urlpatterns = [
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login', LoginView.as_view(), name='login'),
    path('users/<str:user_id>/', UserDetailView.as_view(), name='user-detail'),
    path('organisations', UserOrganizationsView.as_view(), name='user-organisations'),
    path('organisations/<str:org_id>/', OrganizationDetailView.as_view(), name='organisation-detail'),
    path('organisations', OrganizationCreateView.as_view(), name='organisation-create'),
    path('organisations/<str:org_id>/users/', AddUserToOrganizationView.as_view(), name='add_user_to_organization'),
]
