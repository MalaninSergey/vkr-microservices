from django.urls import path, include
from .views import UserProjectApiView, put_data_to_index, delete_index

urlpatterns = [
    path('create/', UserProjectApiView.as_view()),
    path('add/', put_data_to_index, name='add-data'),
    path('delete/', delete_index, name='delete-index')
]
