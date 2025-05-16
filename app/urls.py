from django.urls import path

from app.views.views import (
    HomeView, AboutView, ContactView, ServicesView
)
from app.views.car.views import (
    VehicleDetailView, VehicleListView, DashboardView,
    VehicleSearchView
)
from app.views.search import SearchView

app_name = "app"


urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("about", AboutView.as_view(), name="about"),
    path("contact", ContactView.as_view(), name="contact"),
    path("services", ServicesView.as_view(), name="services"),
    path("search", SearchView.as_view(), name="search"),
    path("dashboard", DashboardView.as_view(), name="dashboard"),
    path("cars", VehicleListView.as_view(), name="cars_list"),
    path("cars/<int:pk>", VehicleDetailView.as_view(), name="car_detail"),
    path("cars/search", VehicleSearchView.as_view(), name="car_search"),
]
