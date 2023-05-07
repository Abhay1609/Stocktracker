from django.urls import path
from . import views
urlpatterns=[
    path('',views.stockPicker),
    path('stock/',views.stockTracker),


]