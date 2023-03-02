from rest_framework import serializers

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from room.models import (
    Room,
    Event,
    Reservation,
)


class ValidateWithCleanSerializerMixin:
    def validate(self, data):
        instance = self.Meta.model(**data)

        try:
            instance.clean()
        except ValidationError as e:
            raise serializers.ValidationError(e.args[0])

        return super().validate(data)


class UserSerializer(
    ValidateWithCleanSerializerMixin,
    serializers.ModelSerializer
):
    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'first_name',
            'last_name',
        )


class RoomSerializer(
    ValidateWithCleanSerializerMixin,
    serializers.HyperlinkedModelSerializer
):
    class Meta:
        model = Room
        fields = (
            'id',
            'name',
            'capacity'
        )


class ReservationSerializer(
    ValidateWithCleanSerializerMixin,
    serializers.HyperlinkedModelSerializer
):
    class Meta:
        model = Reservation
        fields = (
            'id',
            'event',
            'user'
        )


class EventSerializer(
    ValidateWithCleanSerializerMixin,
    serializers.HyperlinkedModelSerializer
):
    room = serializers.HyperlinkedRelatedField(
        many=False,
        view_name='room-detail',
        queryset=Room.objects.all()
    )

    class Meta:
        model = Event
        fields = (
            'id',
            'name',
            'room',
            'date',
            'is_public'
        )
