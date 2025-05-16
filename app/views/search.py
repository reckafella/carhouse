from django.views.generic import ListView
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.urls import reverse

from app.models.car import Vehicle
from app.views.helpers.helpers import is_ajax


class SearchView(ListView):
    template_name = "app/search/search.html"
    context_object_name = "search_results"
    items_per_page = 6

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._sorting_options = {
            "relevance": "Relevance",
            "date": "Date (Oldest)",
            "date_desc": "Date (Newest)",
            "title": "Title (A-Z)",
            "title_desc": "Title (Z-A)",
            "year": "Year (Oldest)",
            "year_desc": "Year (Newest)",
            "color": "Color (A-Z)",
            "color_desc": "Color (Z-A)",
            "fuel_type": "Fuel Type (A-Z)",
            "fuel_type_desc": "Fuel Type (Z-A)",
            "price": "Price (Low to High)",
            "price_desc": "Price (High to Low)",
            "mileage": "Mileage (Low to High)",
            "mileage_desc": "Mileage (High to Low)",
            "transmission": "Transmission (A-Z)",
            "transmission_desc": "Transmission (Z-A)",
        }

        self.transmission_options = {
            "all": "All",
            "manual": "Manual",
            "automatic": "Automatic",
        }
        self.color_options = {
            "all": "All",
            "red": "Red",
            "blue": "Blue",
            "green": "Green",
            "black": "Black",
            "white": "White",
        }
        self.fuel_type_options = {
            "all": "All",
            "petrol": "Petrol",
            "diesel": "Diesel",
            "electric": "Electric",
            "hybrid": "Hybrid",
        }

    def get_queryset(self):
        """
        Override the get_queryset method to filter results based on query
        """
        # Get parameters from request
        self.query = self.request.GET.get("q", "") or\
            self.request.POST.get("q", "")
        self.transmission = self.request.GET.get("transmission", "all") or\
            self.request.POST.get("transmission", "all")
        self.color = self.request.GET.get("color", "all") or\
            self.request.POST.get("color", "all")
        self.fuel_type = self.request.GET.get("fuel_type", "all") or\
            self.request.POST.get("fuel_type", "all")
        self.price = self.request.GET.get("price") or\
            self.request.POST.get("price")
        self.year = self.request.GET.get("year") or\
            self.request.POST.get("year")
        self.sort = self.request.GET.get("sort", "relevance") or\
            self.request.POST.get("sort", "relevance")
        self.page = self.request.GET.get("page", 1) or\
            self.request.POST.get("page", 1)

        # Get filtered results
        self.vehicle_results = self._get_filtered_results()

        # Apply sorting
        self.vehicle_results = self._apply_sorting()

        # Pagination handled in get_context_data,
        return self.vehicle_results

    def _get_filtered_results(self):
        """
        Helper method to get filtered results based on query and category
        """
        vehicle_results = Vehicle.objects.none()

        # If no query, show all results
        if not self.query:
            if self.category in ["all", "posts"]:
                vehicle_results = Vehicle.objects.live()

        # If query exists, filter results
        if self.category in ["all", "posts"]:
            vehicle_results = Vehicle.objects.filter(
                Q(title__icontains=self.query) |
                Q(description__icontains=self.query)
            )
        return vehicle_results

    def _apply_sorting(self):
        """
        Helper method to sort results based on the selected sorting option
        """
        sorting_options = {
            "date": "first_published_at",
            "title": "title",
            "price": "price",
            "mileage": "mileage",
            "year": "year",
            "transmission": "transmission",
            "color": "color",
            "fuel_type": "fuel_type",
        }

        if not self.sort or self.sort == "relevance":
            return self.vehicle_results

        field, direction = self.sort.rsplit("_", 1)

        field_name = sorting_options.get(field)
        if not field_name:
            return self.vehicle_results

        if direction == "desc":
            field_name = f"-{field_name}"

        return self.vehicle_results.order_by(field_name)

    def _paginate_results(self, queryset):
        """Helper method to paginate results"""
        paginator = Paginator(queryset, self.items_per_page)
        try:
            return paginator.page(self.page)
        except PageNotAnInteger:
            return paginator.page(1)
        except EmptyPage:
            return paginator.page(paginator.num_pages)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Paginate results
        search_results = self._paginate_results(self.vehicle_results)

        results_count = search_results.paginator.count
        _q = self.query

        # Add custom context
        context.update({
            "q": self.request.GET.get("q", ""),
            "category": self.category,
            "sort": self.sort,
            "results": search_results,
            "page_title": f"You Searched For: {_q}" if _q else "Search",
            "data_loading_text": "Searching...",
            "results_count": results_count,
            "sort_options": self._sorting_options,
            "transmission_options": self.transmission_options,
            "color_options": self.color_options,
            "fuel_type_options": self.fuel_type_options,
            "selected_transmission": self.transmission,
            "selected_color": self.color,
            "selected_fuel_type": self.fuel_type,
            "selected_price": self.price,
            "selected_year": self.year,
            "selected_sort": self.sort,
            "selected_page": self.page,
        })

        return context

    def render_to_response(self, context, **response_kwargs):
        if is_ajax(self.request):
            _q = self.query
            response = {
                "success": True,
                "message": f"Results for: {_q}" if _q else "Search",
                "redirect_url": reverse("search"),
            }
            return JsonResponse(response)

        return super().render_to_response(context, **response_kwargs)
