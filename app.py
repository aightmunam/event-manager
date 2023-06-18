from chalice import Chalice, BadRequestError, NotFoundError, Response
from schemas import UserSchema
from marshmallow import ValidationError
from models import User


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
        user: dict = UserSchema().load({**request.json_body, "PK": user.PK, "SK": user.SK})
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
        user.delete()
        return Response(
            body=UserSchema().dump(user),
            status_code=200,
            headers={'Content-Type': 'text/json'}
        )
    except User.DoesNotExist:
        raise NotFoundError("User not found")


@app.route('/events/', methods=['POST'])
def create_event():
    pass


# @app.route('/events/{id}/', methods=['PUT'])
# def update_event():
#     pass


# @app.route('/events/{id}/', methods=['GET'])
# def get_event():
#     pass


# @app.route('/events/{id}/', methods=['DELETE'])
# def delete_event():
#     pass