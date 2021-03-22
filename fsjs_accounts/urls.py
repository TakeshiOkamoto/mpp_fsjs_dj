from django.urls import path
from .views import AccountListView
from .views import AccountCreateView
from .views import AccountDetailView
from .views import AccountUpdateView
from .views import AccountDeleteView

app_name = 'fsjs_accounts'

urlpatterns = [
   path('', AccountListView.as_view(), name='index'),
   path('create', AccountCreateView.as_view(), name='create'),
   path('show/<int:pk>', AccountDetailView.as_view(), name='show'), 
   path('edit/<int:pk>', AccountUpdateView.as_view(), name='edit'),
   path('delete/<int:pk>', AccountDeleteView.as_view(), name='delete'),
]