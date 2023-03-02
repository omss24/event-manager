from typing import Tuple
from django.contrib import admin

from room.models import (
    Room,
    Event,
    Reservation
)


class BaseModelAdmin(admin.ModelAdmin):
    list_filter: Tuple[str] = (
        'created_at',
        'updated_at'
    )
    list_display: Tuple[str] = (
        'id',
        '__str__'
    )
    search_fields: Tuple[str] = (
        'id',
    )


@admin.register(Room)
class RoomAdmin(BaseModelAdmin):
    pass


@admin.register(Event)
class EventAdmin(BaseModelAdmin):
    pass


@admin.register(Reservation)
class ReservationAdmin(BaseModelAdmin):
    pass
