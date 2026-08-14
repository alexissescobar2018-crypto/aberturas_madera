from flask import Flask, render_template, request, redirect
from database import db
from config import Config
from models import db, Abertura
from cotizador import calcular_presupuesto # <- desde "cotizador" solo importas la función
from models import Abertura, Cliente, Presupuesto
from sqlalchemy import func # Asegurate de importar func si no esta arriba
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///aberturas.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False          
app.config.from_object(Config)

# Inicializar la base de datos
db.init_app(app)

# Crear las tablas en la base de datos si no existen
with app.app_context():
    db.create_all()

from sqlalchemy import func  # Asegúrate de importar func si no está arriba

@app.route('/')
def inicio():
    # Métricas para el Dashboard
    total_presupuestado = db.session.query(func.sum(Presupuesto.total)).scalar() or 0.0
    cant_presupuestos = Presupuesto.query.count()
    cant_clientes = Cliente.query.count()
    cant_aberturas = Abertura.query.count()
    
    # Obtener los últimos 5 presupuestos creados
    ultimos_presupuestos = Presupuesto.query.order_by(Presupuesto.id.desc()).limit(5).all()
    
    return render_template(
        'index.html',
        total_presupuestado=total_presupuestado,
        cant_presupuestos=cant_presupuestos,
        cant_clientes=cant_clientes,
        cant_aberturas=cant_aberturas,
        presupuestos=ultimos_presupuestos
    )

    db.session.commit()

@app.route('/catalogo', methods=['GET', 'POST'])
def catalogo():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        precio_m2 = float(request.form.get('precio_m2', 0))
        imagen = request.form.get('imagen', 'default.jpg')
        
        # Agregamos valores por defecto a los campos obligatorios para evitar el error
        nueva_abertura = Abertura(
            nombre=nombre,
            tipo=request.form.get('tipo', 'Estándar'),
            material=request.form.get('material', 'Algarrobo'),
            ancho_cm=float(request.form.get('ancho_cm', 100)),
            alto_cm=float(request.form.get('alto_cm', 100)),
            precio_m2=precio_m2,
            imagen=imagen
        )
        
        db.session.add(nueva_abertura)
        db.session.commit()

    aberturas = Abertura.query.all()
    return render_template('catalogo.html', aberturas=aberturas)

@app.route('/cotizador', methods=['GET', 'POST'])
def cotizador():
    cotizacion = None
    if request.method == 'POST':
        try:
            ancho = float(request.form.get('ancho', 0))
            alto = float(request.form.get('alto', 0))
            precio_m2 = float(request.form.get('precio_m2', 0))
            
            # Llamamos a la función de cálculo
            cotizacion = calcular_presupuesto(ancho, alto, precio_m2)
        except (ValueError, TypeError):
            cotizacion = 0

    return render_template('cotizador.html', cotizacion=cotizacion)

@app.route('/nuevo_presupuesto', methods=['GET', 'POST'])
def nuevo_presupuesto():
    if request.method == 'POST':
        cliente_id = int(request.form['cliente_id'])
        ancho = float(request.form['ancho'])
        alto = float(request.form['alto'])
        precio_m2 = float(request.form['precio_m2'])
        
        # Área en m²: (Ancho cm / 100) * (Alto cm / 100)
        area_m2 = (ancho / 100.0) * (alto / 100.0)
        total = area_m2 * precio_m2
        
        presupuesto = Presupuesto(
            cliente_id=cliente_id,
            ancho=ancho,
            alto=alto,
            precio_m2=precio_m2,
            total=total
        )
        
        db.session.add(presupuesto)
        db.session.commit()
        
        return redirect('/presupuestos')

    # Enviamos tanto los clientes como las aberturas del catálogo
    clientes = Cliente.query.all()
    aberturas = Abertura.query.all()
    return render_template('nuevo_presupuesto.html', clientes=clientes, aberturas=aberturas)


# --- HISTORIAL Y BÚSQUEDA DE PRESUPUESTOS ---

@app.route('/presupuestos')
def presupuestos():
    # Obtenemos el término de búsqueda de la URL (si existe)
    buscar = request.args.get('buscar', '').strip()
    
    if buscar:
        # Filtramos por nombre de cliente que contenga el término ingresado
        lista_presupuestos = Presupuesto.query.join(Cliente).filter(
            Cliente.nombre.ilike(f'%{buscar}%')
        ).all()
    else:
        # Si no hay búsqueda, mostramos todos
        lista_presupuestos = Presupuesto.query.all()
        
    return render_template('presupuestos.html', presupuestos=lista_presupuestos, buscar=buscar)


# --- ELIMINAR PRESUPUESTO ---

@app.route('/presupuesto/eliminar/<int:id>')
def eliminar_presupuesto(id):
    presupuesto = Presupuesto.query.get_or_404(id)
    db.session.delete(presupuesto)
    db.session.commit()
    return redirect('/presupuestos')

@app.route('/nuevo_cliente', methods=['GET', 'POST'])
def nuevo_cliente():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        telefono = request.form.get('telefono')
        email = request.form.get('email')

        cliente = Cliente(nombre=nombre, telefono=telefono, email=email)
        db.session.add(cliente)
        db.session.commit()
        return redirect('/nuevo_presupuesto')

    return render_template('nuevo_cliente.html')

    
    app.run(debug=True)

import io
from flask import send_file
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

@app.route('/presupuesto/<int:id>/pdf')
def descargar_pdf(id):
    presupuesto = Presupuesto.query.get_or_404(id)
    
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    
    # Encabezado
    p.setFont("Helvetica-Bold", 18)
    p.drawString(100, 750, "Aberturas Madera - Presupuesto")
    
    p.setFont("Helvetica", 10)
    p.drawString(100, 735, f"Fecha: {presupuesto.fecha.strftime('%d/%m/%Y')}")
    p.drawString(100, 720, f"Presupuesto N: #{presupuesto.id}")
    p.line(100, 710, 500, 710)
    
    # Datos del Cliente
    p.setFont("Helvetica-Bold", 12)
    p.drawString(100, 680, "Datos del Cliente:")
    p.setFont("Helvetica", 11)
    p.drawString(120, 660, f"Nombre: {presupuesto.cliente.nombre}")
    p.drawString(120, 645, f"Telefono: {presupuesto.cliente.telefono or 'N/A'}")
    p.drawString(120, 630, f"Email: {presupuesto.cliente.email or 'N/A'}")
    
    # Detalle del Trabajo
    p.setFont("Helvetica-Bold", 12)
    p.drawString(100, 590, "Detalle del Trabajo:")
    p.setFont("Helvetica", 11)
    p.drawString(120, 570, f"Medidas: {presupuesto.ancho} cm (Ancho) x {presupuesto.alto} cm (Alto)")
    p.drawString(120, 550, f"Precio por m2: ${presupuesto.precio_m2:,.2f}")
    
    # Total
    p.line(100, 520, 500, 520)
    p.setFont("Helvetica-Bold", 14)
    p.drawString(100, 490, f"TOTAL: ${presupuesto.total:,.2f}")
    
    p.showPage()
    p.save()
    
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name=f"Presupuesto_{presupuesto.id}_{presupuesto.cliente.nombre}.pdf", mimetype='application/pdf')

# --- RUTAS DE CATÁLOGO DE ABERTURAS ---

@app.route('/aberturas', methods=['GET', 'POST'])
def aberturas():
    if request.method == 'POST':
        nombre = request.form['nombre']
        precio_m2 = float(request.form['precio_m2'])
        imagen_url = request.form.get('imagen_url')

        nueva_abertura = Abertura(
            nombre=nombre, 
            precio_m2=precio_m2, 
            imagen_url=imagen_url
        )
        db.session.add(nueva_abertura)
        db.session.commit()
        return redirect('/aberturas')

    lista_aberturas = Abertura.query.all()
    return render_template('aberturas.html', aberturas=lista_aberturas)
        

@app.route('/abertura/eliminar/<int:id>')
def eliminar_abertura(id):
    abertura = Abertura.query.get_or_404(id)
    db.session.delete(abertura)
    db.session.commit()
    return redirect('/aberturas')
if __name__ == '__main__':
    app.run(debug=True)
