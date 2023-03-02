import datetime
from typing import Optional
from rest_framework.test import APITestCase
from rest_framework import status

from django.db.models import QuerySet
from django.contrib.auth.models import User
from django.urls import reverse

from room.models import (
    Room,
    Event,
    Reservation
)


class BaseAPITestCase(APITestCase):
    staff_user: User
    user: User

    password: str = 'steve-pug-123'

    def setUp(self) -> None:
        self.staff_user = User.objects.create(
            username='staff',
            first_name='steve',
            last_name='pug',
            is_staff=True
        )
        self.user = User.objects.create(
            username='non-staff',
            first_name='steve',
            last_name='pug',
            is_staff=False
        )

        self.staff_user.set_password(self.password)
        self.staff_user.save()

        self.user.set_password(self.password)
        self.user.save()

        return super().setUp()

    def login(self, user: User) -> None:
        self.client.login(username=user, password=self.password)

    def logout(self) -> None:
        self.client.logout()


class RoomBaseAPITestCase(BaseAPITestCase):
    def _create_room(self, name: str = "steve's room") -> Room:
        return Room.objects.create(
            name=name,
            capacity=14
        )

    def _create_event(
        self,
        room: Optional[Room] = None,
        name: str = "steve's event",
        date: datetime.date = datetime.date.today(),
        is_public: bool = False
    ) -> Event:
        if not room:
            room = self._create_room()

        return Event.objects.create(
            room=room,
            name=name,
            date=date,
            is_public=is_public
        )

    def _create_reservation(
        self,
        user: User,
        event: Optional[Room] = None,
    ) -> Reservation:
        if not event:
            event = self._create_event()

        return Reservation.objects.create(
            event=event,
            user=user,
        )


class RoomAPITest(RoomBaseAPITestCase):
    name: str = "steve's room"

    def test_create_room(self) -> None:
        response = self.client.post(
            reverse('room-list'),
            {
                "name": self.name,
                "capacity": 14
            },
            format='json'
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )

        self.login(self.staff_user)

        response = self.client.post(
            reverse('room-list'),
            {
                "name": self.name,
                "capacity": 14
            },
            format='json'
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

        qs: QuerySet = Room.objects.filter(name=self.name, capacity=14)

        self.assertTrue(qs.count(), 1)

    def test_delete_room(self) -> None:
        room: Room = self._create_room(name=self.name)

        response = self.client.delete(
            reverse('room-detail', kwargs={'pk': room.id}),
            format='json'
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )

        self.login(self.staff_user)
        response = self.client.delete(
            reverse('room-detail', kwargs={'pk': room.id}),
            format='json'
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT
        )

        self.assertFalse(
            Room.objects.filter(pk=room.id).exists()
        )

    def test_delete_room_with_event(self) -> None:
        room: Room = self._create_room(name=self.name)
        self._create_event(room=room)

        self.login(self.staff_user)

        response = self.client.delete(
            reverse('room-detail', kwargs={'pk': room.id}),
            format='json'
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

        self.assertTrue(
            Room.objects.filter(pk=room.id).exists()
        )

    def test_retrive_room(self) -> None:
        room: Room = self._create_room(name=self.name)

        response = self.client.get(
            reverse('room-detail', kwargs={'pk': room.id}),
            format='json'
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.login(self.staff_user)
        response = self.client.get(
            reverse('room-detail', kwargs={'pk': room.id}),
            format='json'
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

    def test_list_room(self) -> None:
        self._create_room(name=self.name)

        response = self.client.get(
            reverse('room-list'),
            format='json'
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.login(self.staff_user)
        response = self.client.get(
            reverse('room-list'),
            format='json'
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(
            len(response.json()),
            1
        )


class EventAPITest(RoomBaseAPITestCase):
    name: str = "steve's event"

    def test_create_event(self) -> None:
        room: Room = self._create_room(name=self.name)
        date_str: str = datetime.date.today().isoformat()

        # Test with non-auth.

        response = self.client.post(
            reverse('event-list'),
            {
                "name": self.name,
                "room": room.pk
            },
            format='json',
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

        # Test with staff user.

        self.login(self.staff_user)

        response = self.client.post(
            reverse('event-list'),
            {
                "name": self.name,
                "room": reverse('room-detail', kwargs={'pk': room.pk}),
                "date": date_str
            },
            format='json'
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
            msg=response.content
        )

        qs: QuerySet = Event.objects.filter(name=self.name, date=date_str)

        self.assertTrue(qs.count(), 1)

    def test_list_events(self) -> None:
        # Test with staff user.

        self.login(self.staff_user)
        self._create_event()


        response = self.client.get(
            reverse('event-list'),
            format='json'
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(
            len(response.json()),
            1
        )

    def test_list_public_events(self) -> None:
        private_event: Event = self._create_event(
            is_public=False,
            date=datetime.date.today()
        )
        public_event: Event = self._create_event(
            is_public=True,
            date=datetime.date.today()
        )

        # Test with non-auth.

        response = self.client.get(
            reverse('event-list'),
            format='json'
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        data: dict = response.json()
        self.assertEqual(
            len(data),
            1
        )

        self.assertEqual(data[0]['id'], public_event.pk)

        # Test with staff user.

        self.login(self.staff_user)

        response = self.client.get(
            reverse('event-list'),
            format='json'
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        data: dict = response.json()
        self.assertEqual(
            len(data),
            2
        )

        self.assertEqual(data[0]['id'], private_event.pk)
        self.assertEqual(data[1]['id'], public_event.pk)


class ReservationAPITest(RoomBaseAPITestCase):
    def test_reservation_list(self) -> None:
        user_reservation: Reservation = self._create_reservation(
            user=self.user
        )
        self._create_reservation(user=self.staff_user)

        # Test with non-auth.

        response = self.client.get(
            reverse('reservation-list'),
            {},
            format='json',
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

        self.login(self.staff_user)

        response = self.client.get(
            reverse('reservation-list'),
            {},
            format='json',
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            msg=response.content
        )

        data: dict = response.json()
        self.assertEqual(
            len(data),
            2
        )

        self.logout()

        # Test with non-staff user.

        self.login(self.user)

        response = self.client.get(
            reverse('reservation-list'),
            {},
            format='json',
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            msg=response.content
        )

        data: dict = response.json()
        self.assertEqual(
            len(data),
            1
        )
        self.assertEqual(
            user_reservation.pk,
            data[0]['id']
        )

    def test_book_event(self) -> None:
        event: Event = self._create_event()

        # Test with non-auth.

        response = self.client.post(
            reverse('reservation-list'),
            {},
            format='json',
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

        # Test with staff user.

        self.login(self.staff_user)

        response = self.client.post(
            reverse('reservation-list'),
            {
                "user": reverse('user-detail', kwargs={'pk': self.staff_user.pk}),
                "event": reverse('event-detail', kwargs={'pk': event.pk}),
            },
            format='json'
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
            msg=response.content
        )

        qs: QuerySet = Reservation.objects.filter(
            user=self.staff_user,
            event=event
        )

        self.assertTrue(qs.count(), 1)

        response = self.client.post(
            reverse('reservation-list'),
            {
                "user": reverse('user-detail', kwargs={'pk': self.staff_user.pk}),
                "event": reverse('event-detail', kwargs={'pk': event.pk}),
            },
            format='json'
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
            msg=response.content
        )

    def test_book_event_non_staff(self) -> None:
        event: Event = self._create_event()

        # Test with non-staff user.

        self.login(self.user)

        response = self.client.post(
            reverse('reservation-list'),
            {
                "user": reverse('user-detail', kwargs={'pk': self.user.pk}),
                "event": reverse('event-detail', kwargs={'pk': event.pk}),
            },
            format='json'
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
            msg=response.content
        )

        qs: QuerySet = Reservation.objects.filter(
            user=self.user,
            event=event
        )

        self.assertTrue(qs.count(), 1)

        response = self.client.post(
            reverse('reservation-list'),
            {
                "user": reverse('user-detail', kwargs={'pk': self.user.pk}),
                "event": reverse('event-detail', kwargs={'pk': event.pk}),
            },
            format='json'
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
            msg=response.content
        )

    def test_book_delete(self) -> None:
        user_reservation: Reservation = self._create_reservation(
            user=self.user
        )
        staff_reservation: Reservation = self._create_reservation(
            user=self.staff_user
        )

        # Test with non-auth.
        response = self.client.delete(
            reverse('reservation-detail', kwargs={'pk': user_reservation.pk}),
            format='json',
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

        # Test with user non-staff.
        self.login(self.user)
        response = self.client.delete(
            reverse('reservation-detail', kwargs={'pk': user_reservation.pk}),
            format='json',
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
        )
        self.assertFalse(
            Reservation.objects.filter(pk=user_reservation.pk).exists()
        )

        response = self.client.delete(
            reverse('reservation-detail', kwargs={'pk': staff_reservation.pk}),
            format='json',
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

        self.logout()

        # Test with user staff.

        self.login(self.staff_user)

        response = self.client.delete(
            reverse('reservation-detail', kwargs={'pk': staff_reservation.pk}),
            format='json',
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
        )
        self.assertFalse(
            Reservation.objects.filter(pk=staff_reservation.pk).exists()
        )
