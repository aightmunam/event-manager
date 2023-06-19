from marshmallow import Schema, fields, post_load, ValidationError
from ulid import ULID
from models import User, Event


class BaseSchema(Schema):
    PK = fields.Str()
    SK = fields.Str()


class UserSchema(BaseSchema):
    entity_type = fields.Str(load_default="User", load_only=True)
    email = fields.Email(required=True)
    first_name = fields.Str(dump_default="")
    last_name = fields.Str(dump_default="")
    password = fields.Str(required=True, load_only=True)

    @post_load
    def make_user(self, data, **kwargs):
        instance: User | None = self.context.get("instance", None)
        prepared_key: str = User.prepare_key(str(ULID()))
        PK = SK = None
        if instance:
            PK: str = instance.PK
            SK: str = instance.SK

        put_data: dict = {"PK": PK or prepared_key, "SK": SK or prepared_key, **data}
        user: User = User(**put_data)
        User.put_user(user, old_user=instance)
        return self.dump(user.to_dict())



class EventSchema(BaseSchema):
    entity_type = fields.Str(load_default="Event", load_only=True)

    title = fields.Str(required=True)
    description = fields.Str(required=True)
    date = fields.AwareDateTime(required=True)
    city = fields.Str(required=True)
    zip_code = fields.Number(required=True)

    created_by = fields.Str(required=True)

    gsi1PK = fields.Str(load_only=True)
    gsi1SK = fields.Str(load_only=True)

    gsi2PK = fields.Str(load_only=True)
    gsi2SK = fields.Str(load_only=True)

    @post_load
    def make_event(self, data, **kwargs):
        prepared_key: str = Event.prepare_key(str(ULID()))
        data["created_by"] = User.prepare_key(data["created_by"])
        PK: str = data.get("PK") or prepared_key
        SK: str = data.get("SK") or prepared_key
        index_data = {
            "gsi1PK": data["created_by"],
            "gsi1SK": PK,
            "gsi2PK": data["city"],
            "gsi2SK": data["zip_code"]
        }
        event: Event = Event(PK, SK, **data, **index_data)
        event.save()
        return self.dump(event.to_dict())
