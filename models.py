from pynamodb.models import Model
from pynamodb.attributes import UnicodeAttribute, UTCDateTimeAttribute, NumberAttribute
from pynamodb.indexes import GlobalSecondaryIndex, AllProjection


class EventsManager(Model):
    class Meta:
        table_name = 'EventsManager'

    # common attributes
    PK = UnicodeAttribute(hash_key=True)
    SK = UnicodeAttribute(range_key=True)
    Type = UnicodeAttribute()

    created_by = UnicodeAttribute()

    # event attributes below
    title = UnicodeAttribute()
    description = UnicodeAttribute()
    date = UTCDateTimeAttribute()
    city = UnicodeAttribute()
    zip_code = NumberAttribute()

    # user attributes below
    email = UnicodeAttribute()
    profile_picture = UnicodeAttribute()

    # index attributes below
    GSI1 = GSI1()
    GSI1PK = UnicodeAttribute()
    GSI1SK = UnicodeAttribute()

    GSI2 = GSI2()
    GSI2PK = UnicodeAttribute()
    GSI2SK = UnicodeAttribute()


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
