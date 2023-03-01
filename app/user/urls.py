"""
URL mappings for the user API.
"""
from django.urls import path
from user import views

# app_name is going to be used for the reverse() mapping of the URL pattern.
# Example on test_user_api.py, line 10 : CREATE_USER_URL = reverse('user:create') will returhn the url pattern for the view with the name 'create.
app_name = 'user'

urlpatterns = [
    path('create/', views.CreateUserView.as_view(), name='create'),
    path('token/', views.CreateTokenView.as_view(), name='token'),
    path('me/', views.ManageUserView.as_view(), name='me')
]