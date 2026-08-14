from flask import Flask, render_template, request
from config import Config
from models import db, Abertura
from cotizador import calcular_presupuesto # <- desde "cotizador" solo importas la función
app = Flask(__name__)
app.config.from_object(Config)

# Inicializar la base de datos
db.init_app(app)

# Crear las tablas en la base de datos si no existen
with app.app_context():
    db.create_all()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/catalogo')
def catalogo():
    aberturas = Abertura.query.all()
    return render_template('catalogo.html', aberturas=aberturas)

@app.route('/cotizador', methods=['GET', 'POST'])
def cotizador():
    cotizacion = None
    if request.method == 'POST':
        ancho = float(request.form.get('ancho', 0))
        alto = float(request.form.get('alto', 0))
        precio_m2 = float(request.form.get('precio_m2', 0))
        
        # Cálculo simple por área en m²
    if request.method == "POST":
        ancho = float(request.form.get("ancho" , 0))
        alto = float(request.form.get("alto" , 0))
        precio_m2 = float(request.form.get("precio_m2" , 0))
        cotización = calcular_presupuesto(ancho, alto, precio_m2)

    return render_template('cotizador.html', cotizacion=cotizacion)


@app.route('/catalogo', methods=['GET', 'POST'])
def catalogo():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        precio_m2 = float(request.form.get('precio_m2', 0))
        
        # Crear un nuevo registro de abertura en la base de datos
        nueva_abertura = Abertura(nombre=nombre, precio_m2=precio_m2)
        db.session.add(nueva_abertura)
        db.session.commit()

    # Obtener todas las aberturas guardadas
    aberturas = Abertura.query.all()
    return render_template('catalogo.html', aberturas=aberturas)

if __name__ == '__main__':
    
    app.run(debug=True)