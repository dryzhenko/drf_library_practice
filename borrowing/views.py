from rest_framework import viewsets, permissions

from borrowing.models import Borrowing
from borrowing.serializers import BorrowingSerializer, BorrowingListSerializer, BorrowingCreateSerializer


class BorrowingViewSet(viewsets.ModelViewSet):
    queryset = Borrowing.objects.all()
    serializer_class = BorrowingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            queryset = Borrowing.objects.all()
            user_id = self.request.query_params.get("user_id")
            if user_id:
                queryset = Borrowing.objects.filter(user_id=user_id)
        else:
            queryset = Borrowing.objects.filter(user_id=self.request.user)

        is_active = self.request.query_params.get("is_active")

        if is_active is not None:
            if is_active.lower() == "true":
                queryset = queryset.filter(actual_return_date__isnull=True)
            elif is_active.lower() == "false":
                queryset = queryset.filter(actual_return_date__isnull=False)

        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return BorrowingListSerializer
        if self.action == "create":
            return BorrowingCreateSerializer

        return BorrowingSerializer

