from chalice import Chalice, BadRequestError, NotFoundError, Response
from schemas import UserSchema, EventSchema, EventRegistrationSchema
from marshmallow import ValidationError
from models import User, Event, Registration


app = Chalice(app_name='events-manager')


@app.route('/users', methods=['POST'])
def create_user():
    request = app.current_request
    try:
        user: User = UserSchema().load(request.json_body)
        return Response(
            body=UserSchema().dump(user),
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
        updated_user: User = UserSchema(context={"instance": user}).load(request.json_body)
        return Response(
            body=UserSchema().dump(updated_user),
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

    except ValidationError as err:
        raise BadRequestError(err.messages_dict)


@app.route('/events', methods=['POST'])
def create_event():
    request = app.current_request
    try:
        event: Event = EventSchema().load(request.json_body)
        return Response(
            body=EventSchema().dump(event),
            status_code=200,
            headers={'Content-Type': 'text/json'}
        )
    except ValidationError as err:
        raise BadRequestError(err.messages_dict)


@app.route('/users/{id}/events', methods=['GET'])
def get_events_by_user(id):
    full_key = User.prepare_key(id)
    events = Event.gsi1.query(full_key, Event.gsi1SK.startswith("EVENT#"), filter_condition=Event.entity_type == "Event")
    return Response(
        body=EventSchema().dump(events, many=True),
        status_code=200,
        headers={'Content-Type': 'text/json'}
    )


@app.route('/events/{id}/registrations', methods=['POST'])
def register_for_event(id):
    request = app.current_request
    full_key: str = Event.prepare_key(id)
    try:
        event: Event = Event.get(full_key, full_key)
        registration: Registration = EventRegistrationSchema().load({**request.json_body, "event": event.PK})
        return Response(
            body=EventRegistrationSchema().dump(registration),
            status_code=200,
            headers={'Content-Type': 'text/json'}
        )
    except Event.DoesNotExist:
        raise NotFoundError("Event not found")

    except ValidationError as err:
        raise BadRequestError(err.messages_dict)


@app.route('/events/{id}/registrations/{user_id}', methods=['GET', 'DELETE'])
def change_registration(id, user_id):
    request = app.current_request
    try:
        registration: Registration = Registration.get(Event.prepare_key(id), User.prepare_key(user_id))
        if request.method == 'DELETE':
            registration.delete()
        return Response(
            body=EventRegistrationSchema().dump(registration),
            status_code=200,
            headers={'Content-Type': 'text/json'}
        )

    except Registration.DoesNotExist:
        raise NotFoundError("Registration not found")

    except ValidationError as err:
        raise BadRequestError(err.messages_dict)


@app.route('/users/{id}/registrations', methods=['GET'])
def get_user_registrations(id):
    registrations = Registration.gsi1.query(User.prepare_key(id), filter_condition=Registration.entity_type == "Registration")
    return Response(
        body=EventRegistrationSchema().dump(registrations, many=True),
        status_code=200,
        headers={'Content-Type': 'text/json'}
    )
