import datetime

from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from room_manager.models import BaseModel


class Room(BaseModel):
    name: str = models.CharField(max_length=225)
    capacity: int = models.PositiveIntegerField()


class Event(BaseModel):
    reservations: models.QuerySet  # room.models.Reservation.

    name: str = models.CharField(max_length=225)
    room: Room = models.ForeignKey(
        Room,
        on_delete=models.PROTECT,
        related_name='events'
    )
    is_public: bool = models.BooleanField(default=False)
    date: datetime.date = models.DateField()

    def clean(self) -> None:
        qs: models.QuerySet = self.__class__.objects.filter(
            date=self.date,
            room=self.room
        )
        if qs.exists():
            raise ValidationError(_("Room has event on that day."))

        return super().clean()


class Reservation(BaseModel):
    user: User = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
    )
    event: Event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='reservations'
    )

    class Meta:
        unique_together = (('user', 'event'), )

    def clean(self) -> None:
        room: Room = self.event.room
        n_reservations: int = self.event.reservations.all().count()

        if n_reservations >= room.capacity:
            raise ValidationError(_("Room has no more capacity."))

        return super().clean()
