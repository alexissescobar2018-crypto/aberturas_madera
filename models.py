from database import db
from datetime import datetime

class Abertura(db.Model):
    __tablename__ = 'aberturas'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    precio_m2 = db.Column(db.Float, nullable=False)

class Cliente(db.Model):
    __tablename__ = 'clientes'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    telefono = db.Column(db.String(50), nullable=True)
    email = db.Column(db.String(100), nullable=True)
    presupuestos = db.relationship('Presupuesto', backref='cliente', lazy=True)

class Presupuesto(db.Model):
    __tablename__ = 'presupuestos'
    id = db.Column(db.Integer, primary_key=True)
    ancho = db.Column(db.Float, nullable=False)
    alto = db.Column(db.Float, nullable=False)
    precio_m2 = db.Column(db.Float, nullable=False)
    total = db.Column(db.Float, nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=False)
    abertura_id = db.Column(db.Integer, db.ForeignKey('aberturas.id'), nullable=True)

class Abertura(db.Model):
    __tablename__ = 'aberturas'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    precio_m2 = db.Column(db.Float, nullable=False)
    imagen_url = db.Column(db.String(500), nullable=True)
