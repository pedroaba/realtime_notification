from repository.database import db


class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.Float)
    paid = db.Column(db.Boolean, default=False)
    bank_payment_id = db.Column(db.String(100), nullable=True)

    qr_code = db.Column(db.String(100), nullable=True)
    expiration_date = db.Column(db.DateTime, nullable=True)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "value": self.value,
            "paid": self.paid,
            "bank_payment_id": self.bank_payment_id,
            "expiration_date": self.expiration_date,
            "qr_code": self.qr_code
        }
