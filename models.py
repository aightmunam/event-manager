import os
from time import time

from marshmallow import ValidationError
from pynamodb.attributes import UnicodeAttribute, UTCDateTimeAttribute
from pynamodb.connection import Connection
from pynamodb.exceptions import TransactWriteError
from pynamodb.indexes import AllProjection, GlobalSecondaryIndex
from pynamodb.models import Model
from pynamodb.transactions import TransactWrite


class GSI1(GlobalSecondaryIndex):
    class Meta:

        read_capacity_units = 2
        write_capacity_units = 1
        # All attributes are projected
        projection = AllProjection()

    gsi1PK = UnicodeAttribute(hash_key=True)
    gsi1SK = UnicodeAttribute(range_key=True)


class GSI2(GlobalSecondaryIndex):
    class Meta:

        read_capacity_units = 2
        write_capacity_units = 1
        # All attributes are projected
        projection = AllProjection()

    gsi2PK = UnicodeAttribute(hash_key=True)
    gsi2SK = UnicodeAttribute(range_key=True)


class BaseEventManagerModel(Model):
    class Meta:
        table_name = os.getenv("APP_TABLE_NAME", "undefined")
        host = os.getenv("DYNAMODB_HOST", "undefined")

    PK = UnicodeAttribute(hash_key=True)
    SK = UnicodeAttribute(range_key=True)
    entity_type = UnicodeAttribute()
    ID = UnicodeAttribute(null=True)

    def to_dict(self):
        rval = {}
        for key in self.attribute_values:
            rval[key] = self.__getattribute__(key)
        return rval

    @classmethod
    def prepare_key(cls, key):
        raise NotImplementedError()


class Event(BaseEventManagerModel):
    title = UnicodeAttribute()
    description = UnicodeAttribute()
    date = UTCDateTimeAttribute()
    city = UnicodeAttribute()
    zip_code = UnicodeAttribute()
    created_by = UnicodeAttribute()

    gsi1 = GSI1()
    gsi1PK = UnicodeAttribute()
    gsi1SK = UnicodeAttribute()

    gsi2 = GSI2()
    gsi2PK = UnicodeAttribute()
    gsi2SK = UnicodeAttribute()

    @classmethod
    def prepare_key(cls, key):
        return f"EVENT#{key}"


class User(BaseEventManagerModel):
    email = UnicodeAttribute()
    password = UnicodeAttribute()
    first_name = UnicodeAttribute(null=True)
    last_name = UnicodeAttribute(null=True)

    @classmethod
    def prepare_key(cls, key):
        return f"USER#{key}"

    @classmethod
    def put_user(cls, user, old_user):
        new_email_key: str = Email.prepare_key(user.email)
        new_email: Email = Email(
            PK=new_email_key,
            SK=new_email_key,
            entity_type="Email",
            user=user.ID
        )

        connection: Connection = Connection(
            host=os.getenv("DYNAMODB_HOST", "undefined")
        )
        try:
            with TransactWrite(
                connection=connection,
                client_request_token=str(time())
            ) as transaction:
                transaction.save(user)
                if old_user:
                    if old_user.email != user.email:
                        old_email_key: str = Email.prepare_key(old_user.email)
                        transaction.delete(
                            Email.get(old_email_key, old_email_key)
                        )
                        transaction.save(
                            new_email, condition=Email.PK.does_not_exist()
                        )
                else:
                    transaction.save(
                        new_email, condition=Email.PK.does_not_exist()
                    )
        except TransactWriteError as err:
            if (
                err.cancellation_reasons and (
                    err.cancellation_reasons[1]
                    or err.cancellation_reasons[2]
                )
            ):
                raise ValidationError(
                    {"email": "Email already belongs to another user."}
                )
            else:
                raise ValidationError(
                    "Something went wrong. Please try again."
                )

    @classmethod
    def delete_user(cls, user):
        connection: Connection = Connection(
            host=os.getenv("DYNAMODB_HOST", "undefined")
        )
        try:
            with TransactWrite(
                connection=connection,
                client_request_token=str(time())
            ) as transaction:
                email_key = Email.prepare_key(user.email)
                transaction.delete(Email.get(email_key, email_key))
                transaction.delete(user)
        except TransactWriteError:
            raise ValidationError("Something went wrong. Please try again.")


class Email(BaseEventManagerModel):
    user = UnicodeAttribute()

    @classmethod
    def prepare_key(cls, key):
        return f"EMAIL#{key}"


class Registration(BaseEventManagerModel):
    user = UnicodeAttribute()
    event = UnicodeAttribute()
    registration_time = UTCDateTimeAttribute()

    gsi1 = GSI1()
    gsi1PK = UnicodeAttribute()
    gsi1SK = UnicodeAttribute()

    @classmethod
    def prepare_key(cls, key):
        return f"REGISTRATION#{key}"
