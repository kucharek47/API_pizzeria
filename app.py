from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime
import secrets
import json

app = Flask(__name__)

CORS(app, supports_credentials=True, origins=[
    "http://localhost:4200",
    "http://127.0.0.1:4200",
    "http://192.168.10.149:4200"
])

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pizzeria.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cookies = db.Column(db.String(120), unique=True, nullable=False)
    telefon = db.Column(db.String(12))
    miasto = db.Column(db.String(43)) #Wólka Sokołowska koło Wólki Niedźwiedzkiej
    kod_pocztowy = db.Column(db.String(6))
    ulica = db.Column(db.String(50))
    orders = db.relationship('Order', backref='customer', lazy=True)
    koszyk = db.Column(db.String(1200))


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pizza_json = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='oczekuje')
    date_created = db.Column(db.String(30), default=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class Menu(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nazwa = db.Column(db.String(40), nullable=False)
    skladniki = db.Column(db.String(400), nullable=False)
    obrazek_path = db.Column(db.String(200))

with app.app_context():
    db.create_all()
    if not db.session.get(User, 1):
        test_user = User(cookies='test')
        db.session.add(test_user)
        db.session.commit()

@app.route("/api/start", methods=["POST"])
def start_app_router():
    token = secrets.token_hex(16)
    while User.query.filter_by(cookies=token).first() is not None:
        token = secrets.token_hex(16)
    nowy = User(cookies=token)
    db.session.add(nowy)
    db.session.commit()
    return jsonify({"cookies":token})
@app.route("/api/check_cookiess", methods=["POST"])
def check_cookies_app_router():
    token = request.cookies.get('session_token')
    if token:
        if User.query.filter_by(cookies=token).first():
            return jsonify({"error_cookies": False})
        else:
            return jsonify({"error_cookies": True, "powod": "brak cookies w bazie"})
    else:
        return jsonify({"error_cookies": True, "powod": "brak cookies"})
@app.route("/api/menu", methods=["GET"])
def menu_app_router():
    wszystkie_dania = Menu.query.all()
    wynik = []
    for danie in wszystkie_dania:
        wynik.append({
            'id': danie.id,
            'nazwa': danie.nazwa,
            'skladniki': json.loads(danie.skladniki),
            'obrazek_path': danie.obrazek_path
        })
    return jsonify(wynik)
@app.route("/api/dodaj_do_koszyka", methods=["POST"])
def dodaj_do_koszyka_app_router():
    token = request.cookies.get('session_token')
    if token:
        uzytwkonik = User.query.filter_by(cookies=token).first()
        if uzytwkonik:
            dane = request.get_json()
            try:
                cena = (dane["rozmiar"] * 10 + 20) + ((dane["ciasto"] - 1) * 5) + (
                    len(dane["skladniki"]) * 3 if dane["rozmiar"] <= 1 else 4)
            except KeyError:
                return jsonify({"error_cookies": False, "powod": "blad skladni"}), 400
            print(uzytwkonik.koszyk)
            koszyk = json.loads(uzytwkonik.koszyk) if uzytwkonik.koszyk else {}
            koszyk[datetime.now().strftime("%Y-%m-%d-%H:%M:%S")] = {
                'status': 'w koszyku',
                'oplacone': False,
                'skladnikiD': dane["skladniki"],
                'rozmiar': dane["rozmiar"],
                'ciasto': dane["ciasto"],
                'sos': dane["sos"],
                'wartosc': cena
            }
            uzytwkonik.koszyk = json.dumps(koszyk)
            db.session.commit()
            wartosc = 0
            for x in koszyk:
                wartosc += koszyk[x]["wartosc"]
            return jsonify({"error_cookies": False,"wartosc_koszyka":wartosc})
        else:
            return jsonify({"error_cookies": True, "powod": "brak cookies w bazie"}),401
    else:
        return jsonify({"error_cookies": True, "powod": "brak cookies"}),401

if __name__ == '__main__':
    app.run(debug=True, port=5000, host="0.0.0.0",use_reloader=True)