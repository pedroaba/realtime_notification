import datetime
from datetime import timedelta
from flask_socketio import SocketIO

from flask import Flask, jsonify, request, send_file, render_template

from payments.pix import Pix
from repository.database import db
from models.payment import Payment

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = '<KEY>'

db.init_app(app)
socketio = SocketIO()


@app.route('/payments/pix', methods=['POST'])
def create_payment_pix():
    body = request.get_json()

    if 'value' not in body:
        return jsonify({
            "message": "Invalid value"
        }), 400

    expiration_date = datetime.datetime.now() + timedelta(minutes=30)
    new_payment = Payment(
        value=body['value'],
        expiration_date=expiration_date
    )

    data_payment_pix = Pix.create_payment()
    new_payment.bank_payment_id = data_payment_pix['bank_payment_id']
    new_payment.qr_code = data_payment_pix['qr_code_path']

    db.session.add(new_payment)
    db.session.commit()

    return jsonify({
        "message": "The payment has been created",
        "payment": new_payment.to_dict()
    })


@app.route('/payments/pix/qr_code/<filename>', methods=['GET'])
def get_qr_code(filename):
    return send_file(f'static/img/{filename}.png', mimetype='image/png')


@app.route('/payments/pix/confirmation', methods=['POST'])
def pix_confirmation():
    body = request.get_json()

    if "bank_payment_id" not in body:
        return jsonify({
            "message": "Invalid payment data"
        }), 400

    payment = Payment.query.filter_by(bank_payment_id=body['bank_payment_id']).first()

    return jsonify({
        "message": "The payment has been confirmed"
    })


@app.route('/payments/pix/<int:payment_id>', methods=['GET'])
def payment_pix_page(payment_id: int):
    payment = Payment.query.get(payment_id)

    return render_template(
        'payment.html',
        payment_id=payment.id,
        value=payment.value,
        host="http://127.0.0.1:5000",
        qr_code=payment.qr_code
    )


@socketio.on('connect')
def handle_connect():
    print("Client connected to the server.")


if __name__ == '__main__':
    socketio.run(app, debug=True)
