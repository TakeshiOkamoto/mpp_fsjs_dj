from django.urls import path
from .views import JournalListView
from .views import JournalCreateView
from .views import JournalDetailView
from .views import JournalUpdateView
from .views import JournalDeleteView

app_name = 'fsjs_journals'

urlpatterns = [
   path('', JournalListView.as_view(), name='index'),
   path('create', JournalCreateView.as_view(), name='create'),
   path('show/<int:pk>', JournalDetailView.as_view(), name='show'), 
   path('edit/<int:pk>', JournalUpdateView.as_view(), name='edit'),
   path('delete/<int:pk>', JournalDeleteView.as_view(), name='delete'),
]