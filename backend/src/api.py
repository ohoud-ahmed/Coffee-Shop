import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

# db_drop_and_create_all()

# ROUTES


@app.route('/drinks')
def get_drinks():
    drinksList = Drink.query.all()
    drinks = {}
    for drink in drinksList:
        drinks[drink.id] = drink.type

    return jsonify({
        'success': True,
        'drinks': drinks,
    })


@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def drinks_detail(token):
    drinks = Drink.query.all()

    return jsonify({
        'drinks': [drink.long() for drink in drinks],
        'success': True
    })


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def create_drinks(token):
    body = request.get_json()

    title = body['title']
    ingredients = body['ingredients']

    try:
        drink = Drink(
            title=title,
            ingredients=ingredients)

        drink.insert()

        return jsonify({
            'drinks': drink.long(),
            'success': True
        })

    except BaseException:
        abort(422)


@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drinks(token, drink_id):

    body = request.get_json()

    try:
        drink = Drink.query.filter(Drink.id == drink_id).one_or_none()
        if drink is None:
            abort(404)

        if 'title' in body:
            drink.title = int(body.get('title'))

        drink.update()

        return jsonify({
            'success': True,
            'drinks': drink.long()
        })

    except:
        abort(400)


'''
@TODO implement endpoint
    DELETE /drink/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(drink_id, token):
    try:
        drink = Drink.query.filter(Drink.id == drink_id).one_or_none()

        if drink is None:
            abort(404)

        drink.delete()

        return jsonify({
            'success': True,
            'delete': drink_id
        })

    except:
        abort(422)


# Error Handling
'''
Example error handling for unprocessable entity
'''


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


@ app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404
