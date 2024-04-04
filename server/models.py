from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import validates
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin

convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

metadata = MetaData(naming_convention=convention)

db = SQLAlchemy(metadata=metadata)

# db.Model = base class provided by SQLAlchemy

class Planet(db.Model, SerializerMixin):
    __tablename__ = "planets"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    distance_from_earth = db.Column(db.Integer)
    nearest_star = db.Column(db.String)

    # Add relationship
    # 1st arg = connecting class, back_populates = relationship on the related model
    missions = db.relationship("Mission", back_populates="planet", cascade="all, delete-orphan")

    #Association proxy
    # 1st arg = relationship property used as "connector", 2nd arg = name of model trying to connect to in lowercase
    scientists = association_proxy("missions", "scientist")
    
    # Add serialization rules
    # Tell SQLAlchemy-Serializer to not look back at the original record from within its related records
    serialize_rules = ("-missions.planet", "-scientists.planets")



class Scientist(db.Model, SerializerMixin):
    __tablename__ = "scientists"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    field_of_study = db.Column(db.String)

    # Add relationship
    # 1st arg = connecting class, back_populates = relationship on the related model
    missions = db.relationship("Mission", back_populates="scientist", cascade="all, delete-orphan")

    # Association proxy
    # 1st arg = relationship property used as "connector", 2nd arg = name of model trying to connect to in lowercase
    planets = association_proxy("missions", "planet")

    # Add serialization rules
    # ASK MATTEO - Need to exclude the association proxy relationship here?
    serialize_rules = ("-missions.scientist", "-planets.scientists")

    # Add validation
    @validates("name")
    def validate_name(self, _, name):
        if not name:
            raise ValueError("Name has to be present")
        return name

    @validates("field_of_study")
    def validate_field_of_study(self, _, field_of_study):
        if not field_of_study:
            raise ValueError("field_of_study has to be present")
        return field_of_study




class Mission(db.Model, SerializerMixin):
    __tablename__ = "missions"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    planet_id = db.Column(db.Integer, db.ForeignKey("planets.id"))
    scientist_id = db.Column(db.Integer, db.ForeignKey("scientists.id"))
    
    # Add relationships
    # 1st arg = connecting class, back_populates = relationship on the related model
    scientist = db.relationship("Scientist", back_populates="missions")
    planet = db.relationship("Planet", back_populates="missions")
    
    # Add serialization rules
    serialize_rules = ("-scientist.missions", "-planet.missions")
    
    # Add validation
    @validates("name")
    def validate_name(self, _, name):
        if not name:
            raise ValueError("Name has to be present")
        return name

    @validates("scientist_id")
    def validate_scientist_id(self, _, scientist_id):
        if not scientist_id:
            raise ValueError("scientist_id has to be present")
        return scientist_id

    @validates("planet_id")
    def validate_planet_id(self, _, planet_id):
        if not planet_id:
            raise ValueError("planet_id has to be present")
        return planet_id


# add any models you may need.