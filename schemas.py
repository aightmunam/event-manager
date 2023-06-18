from marshmallow import Schema, fields, post_load
from ulid import ULID
from models import User


class UserSchema(Schema):
    PK = fields.Str()
    SK = fields.Str()
    email = fields.Email(required=True)
    first_name = fields.Str(dump_default="")
    last_name = fields.Str(dump_default="")
    password = fields.Str(required=True, load_only=True)
    entity_type = fields.Str(load_default="User", load_only=True)

    @post_load
    def make_user(self, data, **kwargs):
        prepared_key: str = User.prepare_key(str(ULID()))
        PK: str = data.get("PK") or prepared_key
        SK: str = data.get("SK") or prepared_key
        user: User = User(PK, SK, **data)
        user.save(condition=User.email.does_not_exist())
        return self.dump(user.to_dict())
