from chalice import BadRequestError, Chalice, NotFoundError, Response
from marshmallow import ValidationError

from models import Event, Registration, User
from schemas import EventRegistrationSchema, EventSchema, UserSchema

app = Chalice(app_name="events-manager")


@app.route("/users", methods=["POST"])
def create_user():
    request = app.current_request
    try:
        user: User = UserSchema().load(request.json_body)
        return Response(
            body=UserSchema().dump(user),
            status_code=200,
            headers={"Content-Type": "text/json"}
        )
    except ValidationError as err:
        raise BadRequestError(err.messages_dict)


@app.route("/users/{pk}", methods=["GET", "DELETE", "PUT"])
def user_detail(pk):
    request = app.current_request
    full_key: str = User.prepare_key(pk)
    try:
        user: User = User.get(full_key, full_key)
        if request.method == "DELETE":
            User.delete_user(user)
        elif request.method == "PUT":
            user = UserSchema(
                context={"instance": user}
            ).load(request.json_body)

        return Response(
            body=UserSchema().dump(user),
            status_code=200,
            headers={"Content-Type": "text/json"}
        )
    except User.DoesNotExist:
        raise NotFoundError("User not found")

    except ValidationError as err:
        raise BadRequestError(err.messages_dict)


@app.route("/events", methods=["POST"])
def create_event():
    request = app.current_request
    try:
        event: Event = EventSchema().load(request.json_body)
        return Response(
            body=EventSchema().dump(event),
            status_code=200,
            headers={"Content-Type": "text/json"}
        )
    except ValidationError as err:
        raise BadRequestError(err.messages_dict)


@app.route("/events/{pk}", methods=["GET", "DELETE", "PUT"])
def event_detail(pk):
    request = app.current_request
    full_key: str = Event.prepare_key(pk)
    try:
        event: Event = Event.get(full_key, full_key)
        if request.method == "DELETE":
            event.delete()
        elif request.method == "PUT":
            event = EventSchema(
                context={"instance": event}
            ).load(request.json_body)

        return Response(
            body=EventSchema().dump(event),
            status_code=200,
            headers={"Content-Type": "text/json"}
        )
    except Event.DoesNotExist:
        raise NotFoundError("Event not found")

    except ValidationError as err:
        raise BadRequestError(err.messages_dict)


@app.route("/users/{id}/events", methods=["GET"])
def get_events_by_user(id):
    full_key = User.prepare_key(id)
    events = Event.gsi1.query(full_key, Event.gsi1SK.startswith("EVENT#"))
    return Response(
        body=EventSchema().dump(events, many=True),
        status_code=200,
        headers={"Content-Type": "text/json"}
    )


@app.route("/events/{id}/registrations", methods=["POST"])
def register_for_event(id):
    request = app.current_request
    full_key: str = Event.prepare_key(id)
    try:
        event: Event = Event.get(full_key, full_key)
        registration: Registration = EventRegistrationSchema().load(
            {**request.json_body, "event": event.ID}
        )
        return Response(
            body=EventRegistrationSchema().dump(registration),
            status_code=200,
            headers={"Content-Type": "text/json"}
        )
    except Event.DoesNotExist:
        raise NotFoundError("Event not found")

    except ValidationError as err:
        raise BadRequestError(err.messages_dict)


@app.route("/events/{id}/registrations/{user_id}", methods=["GET", "DELETE"])
def change_registration(id, user_id):
    request = app.current_request
    try:
        registration: Registration = Registration.get(
            Event.prepare_key(id), User.prepare_key(user_id)
        )
        if request.method == "DELETE":
            registration.delete()
        return Response(
            body=EventRegistrationSchema().dump(registration),
            status_code=200,
            headers={"Content-Type": "text/json"}
        )

    except Registration.DoesNotExist:
        raise NotFoundError("Registration not found")

    except ValidationError as err:
        raise BadRequestError(err.messages_dict)


@app.route("/events/{id}/registrations", methods=["GET"])
def get_event_registrations(id):
    registrations = Registration.query(
        Event.prepare_key(id), Registration.SK.startswith("USER#")
    )
    return Response(
        body=EventRegistrationSchema().dump(registrations, many=True),
        status_code=200,
        headers={"Content-Type": "text/json"}
    )


@app.route("/users/{id}/registrations", methods=["GET"])
def get_user_registrations(id):
    registrations = Registration.gsi1.query(
        User.prepare_key(id), Registration.gsi1SK.startswith("REGISTRATION#")
    )
    return Response(
        body=EventRegistrationSchema().dump(registrations, many=True),
        status_code=200,
        headers={"Content-Type": "text/json"}
    )


@app.route("/events", methods=["GET"])
def get_events_for_city():
    query_params = app.current_request.query_params

    if not query_params or "city" not in query_params:
        raise BadRequestError({"city": "`city` query param must be provided"})

    city: str = query_params.get("city")
    zip_code: str = query_params.get("zip_code")
    if zip_code:
        events = Event.gsi2.query(city, Event.gsi2SK == zip_code)
    else:
        events = Event.gsi2.query(city)
    return Response(
        body=EventSchema().dump(events, many=True),
        status_code=200,
        headers={"Content-Type": "text/json"}
    )
