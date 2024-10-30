from django.urls import path, include
from borrowing.views import BorrowingViewSet
from rest_framework import routers

router = routers.DefaultRouter()
router.register("borrowing", BorrowingViewSet, basename="borrowing")

urlpatterns = [path("", include(router.urls)),]

app_name = "borrowing"
