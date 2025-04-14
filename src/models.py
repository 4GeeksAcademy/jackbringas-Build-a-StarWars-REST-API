from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

db = SQLAlchemy()

favorite_planets = db.Table(
    "favorite_planets",

    db.Column("user_id", ForeignKey("user.id")),
    db.Column("planet_id", ForeignKey("planet.id")),
)

favorite_characters = db.Table(
    "favorite_characters",

    db.Column("user_id", ForeignKey("user.id")),
    db.Column("character_id", ForeignKey("character.id")),
)

class User(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean(), nullable=False)

    favorite_planets: Mapped[list["Planet"]] = relationship(
        "Planet", secondary=favorite_planets, backref="fans"
    )

    favorite_characters: Mapped[list["Character"]] = relationship(
        "Character", secondary=favorite_characters, backref="fans"
    )

    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            "favorite_planets": [planet.name for planet in self.favorite_planets],
            "favorite_characters": [char.name for char in self.favorite_characters],
        }


class Character(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(40), unique=True, nullable=False)
    age: Mapped[int] = mapped_column(String(5), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean(), nullable=False)
    

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "age": self.age,
            "is_active": self.is_active,
            
        }


# class Favorite_character(db.Model):
#     id: Mapped[int] = mapped_column(primary_key=True)
    
#     user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
#     character_id: Mapped[int] = mapped_column(ForeignKey("character.id"), nullable=False)

#     user: Mapped["User"] = relationship("User", backref="favorite_characters")
#     character: Mapped["Character"] = relationship("Character", backref="favorited_by")

#     def serialize(self):
#         return {
#             "id": self.id,
#             "user_id": self.user_id,
#             "character_id": self.character_id,
#             "character_name": self.character.name
#         }


class Planet(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(40), unique=True, nullable=False)
    population: Mapped[int] = mapped_column(nullable=True)
    is_habitable: Mapped[bool] = mapped_column(Boolean(), nullable=False)

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "population": self.population,
            "is_habitable": self.is_habitable
        }
    

# class Favorite_planet(db.Model):
#     id: Mapped[int] = mapped_column(primary_key=True)
#     planet_id: Mapped[int] = mapped_column(ForeignKey("planet.id"), nullable=False)
#     user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
#     planet: Mapped["Planet"] = relationship("Planet", backref="favorited_by")
#     user: Mapped["User"] = relationship("User", backref="favorite_planets")

#     def serialize(self):
#         return {
#             "id": self.id,
#             "planet_id": self.planet_id,
#             "user_id": self.user_id,
#         }
