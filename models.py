from pynamodb.models import Model
from pynamodb.attributes import UnicodeAttribute, UTCDateTimeAttribute, NumberAttribute
from pynamodb.indexes import GlobalSecondaryIndex, AllProjection


class GSI1(GlobalSecondaryIndex):
    class Meta:

        read_capacity_units = 2
        write_capacity_units = 1
        # All attributes are projected
        projection = AllProjection()

    GSI1PK = UnicodeAttribute(hash_key=True)
    GSI1SK = UnicodeAttribute(range_key=True)


class GSI2(GlobalSecondaryIndex):
    class Meta:

        read_capacity_units = 2
        write_capacity_units = 1
        # All attributes are projected
        projection = AllProjection()

    GSI2PK = UnicodeAttribute(hash_key=True)
    GSI2SK = UnicodeAttribute(range_key=True)


class BaseEventManagerModel(Model):
    class Meta:
        table_name = 'EventsManager'
        host = 'http://localhost:8000'

    PK = UnicodeAttribute(hash_key=True)
    SK = UnicodeAttribute(range_key=True)
    entity_type = UnicodeAttribute()

    def to_dict(self):
        rval = {}
        for key in self.attribute_values:
            rval[key] = self.__getattribute__(key)
        return rval

    @classmethod
    def prepare_key(cls, key):
        raise NotImplementedError()

    # GSI1 = GSI1()
    # GSI1PK = UnicodeAttribute()
    # GSI1SK = UnicodeAttribute()

    # GSI2 = GSI2()
    # GSI2PK = UnicodeAttribute()
    # GSI2SK = UnicodeAttribute()


class Event(BaseEventManagerModel):
    title = UnicodeAttribute()
    description = UnicodeAttribute()
    date = UTCDateTimeAttribute()
    city = UnicodeAttribute()
    zip_code = NumberAttribute()
    created_by = UnicodeAttribute()


class User(BaseEventManagerModel):
    email = UnicodeAttribute()
    password = UnicodeAttribute()
    first_name = UnicodeAttribute(null=True)
    last_name = UnicodeAttribute(null=True)

    @classmethod
    def prepare_key(cls, key):
        return f"USER#{key}"


class Registration(BaseEventManagerModel):
    created_by = UnicodeAttribute()