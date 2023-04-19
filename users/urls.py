from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, RegistrationView, LoginView, LogoutView, obtain_jwt_token

router = DefaultRouter()
router.register(r'users', UserViewSet)

authpatterns = [
    path('register/', RegistrationView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('obtain/', obtain_jwt_token, name='obtain')
]

urlpatterns = [
    path('', include(router.urls)),
] + authpatterns
