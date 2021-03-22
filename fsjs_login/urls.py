from django.urls import path
from .views import LoginView
from .views import LoguotView


app_name = 'fsjs_login'

urlpatterns = [
   path('', LoginView.as_view(), name='login'),
   path('out/', LoguotView.as_view(), name='loguot'),
]
