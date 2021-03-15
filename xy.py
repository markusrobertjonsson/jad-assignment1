import threading
import sys
import json
# from json import JSONEncoder
from flask import Flask, jsonify, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
# app.debug = True

# mysql+mysqlconnector://<user>:<password>@<host>[:<port>]/<dbname>
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:hejsan123@localhost/testdatabasen'

# To avoid warning. We do not use the Flask-SQLAlchemy event system, anyway.
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class XYData(db.Model):
    id_number = db.Column(db.Integer, primary_key=True)  # Since "id" is builtin
    description = db.Column(db.String(256), unique=False, nullable=True)
    owner = db.Column(db.String(80), unique=False, nullable=False)
    x = db.Column(db.String(500))
    y = db.Column(db.String(500))

    def get(self, attribute_name):
        d = self.serialize()
        return d[attribute_name]

    def update(self, new_data):
        for key, value in new_data.items():
            setattr(self, key, value)

    def serialize(self):
        return {'id_number': self.id_number,
                'x': self.x,
                'y': self.y,
                'description': self.description,
                'owner': self.owner}

    def to_string(self):
        d = self.serialize()
        out_str = f"{d['id_number']}: "
        for key, val in d.items():
            if key != 'id_number':
                out_str += f"{key}: {val}    "
        return out_str

    def print_attributes(self):
        d = self.serialize()
        for key in d.keys():
            if key != "id_number":
                print(key)


db.create_all()


@app.route('/xydata', methods=['POST'])
def create_xydata():
    dc = json.loads(request.data)
    xydata = XYData(**dc)
    create_xydata_from_obj(xydata)
    url = url_for('get_xydata', id_number=xydata.id_number)
    return redirect(url)


def create_xydata_from_obj(xydata):
    db.session.add(xydata)
    db.session.commit()


@app.route('/xydata', methods=['GET'])
def get_all_xydata():
    all_xydata = XYData.query.all()
    all_xydata_serialized = [xydata.serialize() for xydata in all_xydata]
    return jsonify(all_xydata_serialized)


def get_all_xydata_str():
    all_xydata = XYData.query.all()
    out_str = ""
    for xydata in all_xydata:
        out_str += xydata.to_string() + "\n"
    return out_str


@app.route('/xydata/<int:id_number>', methods=['GET'])
def get_xydata(id_number):
    xydata = XYData.query.filter_by(id_number=id_number).one()
    return jsonify(xydata.serialize())


def get_xydata_obj(id_number):
    xydata = XYData.query.filter_by(id_number=id_number).one()
    return xydata


@app.route('/xydata/<int:id_number>', methods=['PUT'])
def update_xydata(id_number):
    xydata = XYData.query.filter_by(id_number=id_number).one()
    dc = json.loads(request.data)
    xydata.update(dc)
    db.session.commit()
    return jsonify(xydata.serialize())


@app.route('/xydata/<int:id_number>', methods=['DELETE'])
def delete_xydata(id_number):
    xydata = XYData.query.filter_by(id_number=id_number).one()
    db.session.delete(xydata)
    db.session.commit()
    return ""


def command_line():
    print("".join(["\n"] * 50))
    print("********** Welcome to this ugly command line interface! **********")
    while (True):
        print("\nMAIN MENU:\n   Ctrl-C: Exit this CLI\n   1: Create new xydata\n   2: Update xydata\n   3: List all xydata\n   4: Delete xydata")
        choice = input("What do you want to do? ")
        if (choice == "0"):
            sys.exit(0)
        elif (choice == "1"):
            new_xydata = XYData()
            new_xydata.x = input("X-values: ")
            new_xydata.y = input("Y-values: ")
            new_xydata.description = input("Description: ")
            new_xydata.owner = input("Owner: ")
            create_xydata_from_obj(new_xydata)
            print("Successfully created new xydata.")
        elif (choice == "2"):
            print("Which data do you want to update?")
            print(get_all_xydata_str())

            id_ok = False
            while (not id_ok):
                try:
                    update_id = int(input("> "))
                    xydata = get_xydata_obj(update_id)
                    id_ok = True
                except Exception:
                    print("Invalid id. Try again.")

            print("Which attribute would you like to update?")
            xydata.print_attributes()
            attribute_ok = False
            while (not attribute_ok):
                try:
                    attribute_name = input("> ")
                    new_value = input(f"Enter new value of {attribute_name} (old value: {xydata.get(attribute_name)}): ")
                    attribute_ok = True
                except Exception:
                    print("Invalid attribute. Try again.")

            xydata.update({attribute_name: new_value})
            db.session.commit()
        elif (choice == "3"):
            print(get_all_xydata_str())
        elif (choice == "4"):
            print("Which data do you want to delete?")
            print(get_all_xydata_str())

            id_ok = False
            while (not id_ok):
                try:
                    delete_id = int(input("> "))
                    get_xydata_obj(delete_id)  # Just for error handling
                    id_ok = True
                except Exception:
                    print("Invalid id. Try again.")
            delete_xydata(delete_id)
        else:
            print("Invalid input")


cli_thread = threading.Thread(target=command_line)

# Start command line loop
cli_thread.start()

# Start Flask app
app.run()
