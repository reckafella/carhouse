from django.urls import path

from app.views.views import (
    HomeView, AboutView, ContactView, ServicesView
)
from app.views.car.views import (
    VehicleDetailView, VehicleListView
)
from app.views.car.contact_seller import ContactSellerView
from app.views.car.dashboard import DashboardView
from app.views.car.vehicle_review import VehicleReviewCreateView
from app.views.car.views import VehicleCreateView
from app.views.car.views import VehicleUpdateView
from app.views.car.views import VehicleDeleteView
from app.views.car.save_vehicle import SaveVehicleView
from app.views.car.user_vehicle import UserVehiclesView
from app.views.car.save_vehicle import SavedVehiclesView
from app.views.car.vehicle_search import VehicleSearchView
from app.views.search import SearchView

app_name = "app"


urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("about", AboutView.as_view(), name="about"),
    path("contact", ContactView.as_view(), name="contact"),
    path("services", ServicesView.as_view(), name="services"),
    path("search", SearchView.as_view(), name="search"),
    path("dashboard", DashboardView.as_view(), name="dashboard"),

    # Vehicle URLs
    path("cars", VehicleListView.as_view(), name="cars_list"),
    path("cars/create", VehicleCreateView.as_view(), name="car_create"),
    path("cars/my-vehicles", UserVehiclesView.as_view(), name="user_vehicles"),
    path("cars/saved", SavedVehiclesView.as_view(), name="saved_vehicles"),
    path("cars/search", VehicleSearchView.as_view(), name="car_search"),
    path("cars/<int:pk>", VehicleDetailView.as_view(), name="car_detail"),
    path("cars/<int:pk>/edit", VehicleUpdateView.as_view(), name="car_edit"),
    path("cars/<int:pk>/delete", VehicleDeleteView.as_view(),
         name="car_delete"),
    path("cars/<int:vehicle_pk>/review", VehicleReviewCreateView.as_view(),
         name="add_review"),
    path("cars/<int:vehicle_pk>/contact", ContactSellerView.as_view(),
         name="contact_seller"),

    # AJAX endpoints
    path("api/save-vehicle", SaveVehicleView.as_view(), name="save_vehicle"),
]
