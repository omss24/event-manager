from rest_framework import viewsets
from rest_framework.permissions import (
    IsAuthenticated,
    IsAdminUser,
)
from rest_framework.exceptions import ValidationError

from django.contrib.auth.models import User
from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _

from room_manager.permissions import ReadOnly

from room.models import (
    Room,
    Event,
    Reservation,
)
from room.serializers import (
    RoomSerializer,
    EventSerializer,
    UserSerializer,
    ReservationSerializer
)


class UserModelViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class RoomModelViewSet(viewsets.ModelViewSet):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    permission_classes = [IsAdminUser | ReadOnly]

    def destroy(self, request, *args, **kwargs):
        instance: Room = self.get_object()
        if instance.events.all().exists():
            raise ValidationError(_("Room has events."))

        return super().destroy(request, *args, **kwargs)


class EventModelViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [IsAdminUser | ReadOnly]

    def get_queryset(self) -> QuerySet:
        qs: QuerySet = super().get_queryset()
        user: User = self.request.user

        if not user.is_authenticated or not user.is_staff:
            qs = qs.filter(is_public=True)

        return qs


class ReservationSerializerModelViewSet(viewsets.ModelViewSet):
    permission_classes = [
        IsAuthenticated,
    ]
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer

    def get_queryset(self):
        qs: QuerySet = super().get_queryset()

        if self.request.user.is_staff:
            return qs

        return qs.filter(user=self.request.user)
