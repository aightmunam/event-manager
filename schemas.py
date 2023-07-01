from datetime import datetime, timezone

from marshmallow import Schema, ValidationError, fields, post_load
from pynamodb.exceptions import PutError
from ulid import ULID

from models import Event, Registration, User


class BaseSchema(Schema):
    ID = fields.Str(dump_only=True)


class UserSchema(BaseSchema):
    entity_type = fields.Str(load_default="User", load_only=True)
    email = fields.Email(required=True)
    first_name = fields.Str(dump_default="")
    last_name = fields.Str(dump_default="")
    password = fields.Str(required=True, load_only=True)

    @post_load
    def make_user(self, data, **kwargs) -> User:
        instance: User | None = self.context.get("instance", None)
        if instance:
            PK: str = instance.PK
            SK: str = instance.SK
        else:
            identifier: str = str(ULID())
            data["ID"] = identifier
            prepared_key: str = User.prepare_key(identifier)
            PK: str = prepared_key
            SK: str = prepared_key

        user: User = User(PK, SK, **data)
        User.put_user(user, old_user=instance)
        return user


class EventSchema(BaseSchema):
    entity_type = fields.Str(load_default="Event", load_only=True)

    title = fields.Str(required=True)
    description = fields.Str(required=True)
    date = fields.AwareDateTime(required=True)
    city = fields.Str(required=True)
    zip_code = fields.Str(required=True)

    created_by = fields.Str(required=True)

    gsi1PK = fields.Str(load_only=True)
    gsi1SK = fields.Str(load_only=True)

    gsi2PK = fields.Str(load_only=True)
    gsi2SK = fields.Str(load_only=True)

    @post_load
    def make_event(self, data, **kwargs) -> Event:
        if instance := self.context.get("instance", None):
            identifier: str = instance.ID
            event_id: str = instance.PK
        else:
            identifier: str = str(ULID())
            event_id: str = Event.prepare_key(identifier)
            data["ID"] = identifier

        index_data: dict = {
            "gsi1PK": User.prepare_key(data["created_by"]),
            "gsi1SK": event_id,
            "gsi2PK": data["city"],
            "gsi2SK": data["zip_code"]
        }
        event: Event = Event(event_id, event_id, **data, **index_data)
        event.save()
        return event


class EventRegistrationSchema(BaseSchema):
    entity_type = fields.Str(load_default="Registration", load_only=True)

    user = fields.Str(required=True)
    event = fields.Str(required=True)
    registration_time = fields.AwareDateTime()

    @post_load
    def make_registration(self, data, **kwargs) -> Registration:
        if not data.get("registration_time"):
            data["registration_time"] = datetime.now(timezone.utc)

        data["ID"] = str(ULID())
        index_data: dict = {
            "gsi1PK": User.prepare_key(data["user"]),
            "gsi1SK": Registration.prepare_key(data["event"]),
        }
        try:
            registration: Registration = Registration(
                Event.prepare_key(data["event"]),
                User.prepare_key(data["user"]),
                **data,
                **index_data
            )
            registration.save(
                Registration.PK.does_not_exist()
                & Registration.SK.does_not_exist()
            )
        except PutError:
            raise ValidationError(
                {
                    "user": "Registration failed! User may already be"
                    " registered for this event"
                }
            )
        return registration
