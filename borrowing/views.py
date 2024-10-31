from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from borrowing.models import Borrowing
from borrowing.serializers import (
    BorrowingSerializer,
    BorrowingListSerializer,
    BorrowingCreateSerializer,
    BorrowingReturnSerializer
)


class BorrowingViewSet(viewsets.ModelViewSet):
    queryset = Borrowing.objects.all()
    serializer_class = BorrowingSerializer
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="user_id",
                description="Filter borrowings by specific user (admin only)",
                required=False,
                type=int
            ),
            OpenApiParameter(
                name="is_active",
                description="Filter by active borrowings (still not returned): true or false",
                required=False,
                type=bool
            ),
        ],
        responses={200: BorrowingListSerializer},
    )
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

    @extend_schema(
        description="Mark a borrowing instance as returned and increase the book's inventory.",
        responses={201: BorrowingReturnSerializer},
    )
    @action(
        methods=["GET"],
        detail=True,
        serializer_class=BorrowingReturnSerializer
    )
    def return_borrowing(self, request, pk=None):
        borrowing = self.get_object()
        serializer = BorrowingReturnSerializer(borrowing, data=request.data)

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)

