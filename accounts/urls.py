from django.urls import path
from .views import RegisterView, LoginView, UserDetailView, UserOrganizationsView, OrganizationCreateView, OrganizationDetailView

urlpatterns = [
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login', LoginView.as_view(), name='login'),
    path('users/<int:id>', UserDetailView.as_view(), name='user-detail'),
    path('organisations', UserOrganizationsView.as_view(), name='user-organisations'),
    path('organisations/<int:org_id>', OrganizationDetailView.as_view(), name='organisation-detail'),
    path('organisations', OrganizationCreateView.as_view(), name='organisation-create'),
]
