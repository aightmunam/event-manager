from chalice import Chalice, BadRequestError, NotFoundError, Response
from schemas import UserSchema, EventSchema
from marshmallow import ValidationError
from models import User, Event


app = Chalice(app_name='events-manager')


@app.route('/users', methods=['POST'])
def create_user():
    request = app.current_request
    try:
        result: dict = UserSchema().load(request.json_body)
        return Response(
            body=result,
            status_code=200,
            headers={'Content-Type': 'text/json'}
        )
    except ValidationError as err:
        raise BadRequestError(err.messages_dict)


@app.route('/users/{pk}', methods=['GET'])
def get_user(pk):
    full_key: str = User.prepare_key(pk)
    try:
        user: User = User.get(full_key, full_key)
        return Response(
            body=UserSchema().dump(user),
            status_code=200,
            headers={'Content-Type': 'text/json'}
        )
    except User.DoesNotExist:
        raise NotFoundError("User not found")


@app.route('/users/{pk}', methods=['PUT'])
def update_user(pk):
    request = app.current_request
    full_key: str = User.prepare_key(pk)
    try:
        user: User = User.get(full_key, full_key)
        user: dict = UserSchema(context={"instance": user}).load({**request.json_body})
        return Response(
            body=user,
            status_code=200,
            headers={'Content-Type': 'text/json'}
        )
    except User.DoesNotExist:
        raise NotFoundError("User not found")

    except ValidationError as err:
        raise BadRequestError(err.messages_dict)


@app.route('/users/{pk}', methods=['DELETE'])
def delete_user(pk):
    full_key: str = User.prepare_key(pk)
    try:
        user: User = User.get(full_key, full_key)
        User.delete_user(user)
        return Response(
            body=UserSchema().dump(user),
            status_code=200,
            headers={'Content-Type': 'text/json'}
        )
    except User.DoesNotExist:
        raise NotFoundError("User not found")


@app.route('/events', methods=['POST'])
def create_event():
    request = app.current_request
    try:
        result: dict = EventSchema().load(request.json_body)
        return Response(
            body=result,
            status_code=200,
            headers={'Content-Type': 'text/json'}
        )
    except ValidationError as err:
        raise BadRequestError(err.messages_dict)


@app.route('/users/{id}/events', methods=['GET'])
def get_events_by_user(id):
    full_key = User.prepare_key(id)
    events = Event.gsi1.query(full_key, Event.gsi1SK.startswith("EVENT#"))
    print(events)
    return Response(
        body=EventSchema().dump(events, many=True),
        status_code=200,
        headers={'Content-Type': 'text/json'}
    )
