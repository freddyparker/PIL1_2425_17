# urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.RideListCreateView.as_view(), name='ride_list_create'),
    path('<int:pk>/', views.RideDetailView.as_view(), name='ride_detail'),
    path('search/', views.search_rides, name='search_rides'),
    path('<int:ride_id>/request/', views.request_ride, name='request_ride'),
    path('requests/<int:request_id>/respond/', views.respond_to_request, name='respond_to_request'),
    path('my-rides/', views.MyRidesView.as_view(), name='my_rides'),
    path('requests/', views.RideRequestsView.as_view(), name='ride_requests'),
]