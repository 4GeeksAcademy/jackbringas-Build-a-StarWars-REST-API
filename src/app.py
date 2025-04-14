"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Character, Planet, favorite_characters, favorite_planets
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

#GET
@app.route('/user', methods=['GET'])
def get_user():
    users = User.query.all()
    users_list = [userData.serialize() for userData in users]
    return jsonify(users_list), 200

@app.route('/user/<int:user_id>/favorites', methods=['GET'])
def get_user_favorites(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"msg": "User not found"}), 404

    favorite_characters = [character.serialize() for character in user.favorite_characters]
    favorite_planets = [planet.serialize() for planet in user.favorite_planets]

    return jsonify({
        "favorite_characters": favorite_characters,
        "favorite_planets": favorite_planets
    }), 200


@app.route('/characters', methods=['GET'])
def get_characters():
    characters = Character.query.all()
    characters_list = [characterData.serialize() for characterData in characters]
    return jsonify(characters_list), 200

@app.route('/characters/<int:character_id>', methods=['GET'])
def get_character(character_id):
    character = Character.query.filter_by(id= character_id).first()
    if character is None:
        return jsonify({"msg":"character not found"}), 404
    
    return jsonify(character.serialize()), 200


@app.route('/planets', methods=['GET'])
def get_planets():
    planets = Planet.query.all()
    planets_list = [planetData.serialize() for planetData in planets]
    return jsonify(planets_list), 200

@app.route('/planets/<int:planet_id>', methods=['GET'])
def get_planet(planet_id):
    planet = Planet.query.filter_by(id= planet_id).first()
    if planet is None:
        return jsonify({"msg":"planet not found"}), 404
    
    return jsonify(planet.serialize()), 200


#POST
@app.route('/user', methods=['POST'])
def create_user():
    data = request.json
    new_user = User(
        email=data['email'],
        password=data['password'],
        is_active= data.get("is_active")
    )
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "User created"}), 200

@app.route('/character', methods=['POST'])
def create_character():
    
    data = request.json
    new_character = Character(
        
        name =data["name"],
        age = data["age"],
        is_active = data["is_active"],
    )
    db.session.add(new_character)
    db.session.commit()
    
    return jsonify(new_character.serialize()),200


@app.route('/planet', methods=['POST'])
def create_planet():
    
    data = request.json
    new_planet = Planet(
        
        name =data["name"],
        population = data["population"],
        is_habitable = data["is_habitable"],
    )
    db.session.add(new_planet)
    db.session.commit()
    
    return jsonify(new_planet.serialize()),200



# @app.route('/favorite/character/<int:character_id>', methods=['POST'])
# def create_favorite_character():

#     data= request.json
#     new_favorite = Favorite_character (
    
#      name = data["name"],
#      age = data["age"],
#      is_active = data["is_active"]
#  )
#     db.session.add(new_favorite)
#     db.session.commit()
#     return jsonify(new_favorite.serialize()), 200




 
# @app.route('/favorite/planet/<int:planet_id>', methods=['POST'])
# def create_favorite_planet():
#     data = request.json
    
#     new_favorite_planet = Favorite_planet(
#         name = data["name"],
#         population = data["population"],
#         is_habitable = data["is_habitable"]
#     )
    
    
#     db.session.add(new_favorite_planet)
#     db.session.commit()

    
#     return jsonify(new_favorite_planet.serialize()), 200



@app.route('/favorite/character/<int:character_id>', methods=['POST'])
def create_favorite_character(character_id):
    data = request.json
    user_id = data.get("user_id")  

    user = User.query.get(user_id)  
    character = Character.query.get(character_id)  

    if not user or not character:
        return jsonify({"msg": "User or character not found"}), 404
    
    if character in user.favorite_characters:
        return jsonify({"msg": "character is already added"}), 409

    
    user.favorite_characters.append(character)
    db.session.commit()

    return jsonify({"msg": f"{character.name} added to favorites"}), 200


@app.route('/favorite/planet/<int:planet_id>', methods=['POST'])
def create_favorite_planet(planet_id):
    data = request.json
    user_id = data.get("user_id")  

    user = User.query.get(user_id)  
    planet = Planet.query.get(planet_id)  

    if not user or not planet:
        return jsonify({"msg": "User or planet not found"}), 404

    
    user.favorite_planets.append(planet)
    db.session.commit()

    return jsonify({"msg": f"{planet.name} added to favorites"}), 200

#DELETE 
@app.route('/favorite/planet/<int:user_id>/<int:planet_id>', methods=['DELETE'])
def delete_favorite_planet(user_id, planet_id):
    user = User.query.get(user_id)
    planet = Planet.query.get(planet_id)

    if not user or not planet:
        return jsonify({"msg": "User or Planet not found"}), 404

    if planet not in user.favorite_planets:
        return jsonify({"msg": "Planet is not in the user's favorites"}), 400

    user.favorite_planets.remove(planet)
    db.session.commit()

    return jsonify({"msg": "Planet removed from favorites"}), 200


@app.route('/favorite/character/<int:user_id>/<int:character_id>', methods=['DELETE'])
def delete_favorite_character(user_id, character_id):
    user = User.query.get(user_id)
    character = Character.query.get(character_id)

    if not user or not character:
        return jsonify({"msg": "User or Character not found"}), 404

    if character not in user.favorite_characters:
        return jsonify({"msg": "Character is not in the user's favorites"}), 400

    user.favorite_characters.remove(character)
    db.session.commit()

    return jsonify({"msg": "Character removed from favorites"}), 200


# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
