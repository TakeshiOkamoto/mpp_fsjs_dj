from django.urls import path
from .views import CapitalListView
from .views import CapitalCreateView
from .views import CapitalUpdateView
from .views import CapitalDeleteView

app_name = 'fsjs_capitals'

urlpatterns = [
   path('', CapitalListView.as_view(), name='index'),
   path('create', CapitalCreateView.as_view(), name='create'),
   path('edit/<int:pk>', CapitalUpdateView.as_view(), name='edit'),
   path('delete/<int:pk>', CapitalDeleteView.as_view(), name='delete'),
]