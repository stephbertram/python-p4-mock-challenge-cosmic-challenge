#!/usr/bin/env python3

from models import db, Scientist, Mission, Planet
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)
api = Api(app)

class Scientists(Resource):
    def get(self):
        all_scientists = [scientist.to_dict(rules=("-missions",)) for scientist in Scientist.query]
        resp = make_response(all_scientists, 200)
        return resp

    def post(self):
        try:
            data = request.json
            new_scientist = Scientist(**data)
            db.session.add(new_scientist)
            db.session.commit()
            return new_scientist.to_dict(rules=("-missions",)), 201
        except Exception as e:
            db.session.rollback()
            return {"errors": [str(e)]}, 422

api.add_resource(Scientists, "/scientists")

class ScientistById(Resource):
    def get(self, id):
        if scientist := db.session.get(Scientist, id):
            return scientist.to_dict(), 200
        else:
            return {"error": "Scientist not found"}, 404

    def patch(self, id):
        if scientist := db.session.get(Scientist, id):
            try:
                data = request.json
                for attr, value in data.items():
                    setattr(scientist, attr, value) #! model validations kick in for any attr provided!
                db.session.commit()
                return scientist.to_dict(rules=("-missions",)), 202
            except Exception as e:
                return {"errors": [str(e)]}
        else:
            return {"error": "Scientist not found"}, 404

    def delete(self, id):
        if scientist := db.session.get(Scientist, id):
            db.session.delete(scientist)
            db.session.commit()
            return "", 204
        else:
            return {"error": "Scientist not found"}, 404

api.add_resource(ScientistById, "/scientists/<int:id>")

if __name__ == "__main__":
    app.run(port=5555, debug=True)