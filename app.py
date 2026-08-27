from flask import Flask, render_template, request
import smtplib
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

app = Flask(__name__)

GMAIL_USER = "gestioneventocontrasena12@gmail.com"
GMAIL_PASS = "lxbvaaiwjwnhtjni" 

@app.route('/')
def home():
    return render_template('soporte.html')

@app.route('/enviar-ticket', methods=['POST'])
def enviar_ticket():
    nombre_usuario = request.form.get('nombre')
    legajo_usuario = request.form.get('legajo')  
    email_usuario = request.form.get('email')
    prioridad = request.form.get('prioridad')
    categoria = request.form.get('categoria')
    mensaje = request.form.get('descripcion')
    
    ticket_id = int(time.time())

    msg = MIMEMultipart()
    msg['From'] = GMAIL_USER
    msg['To'] = GMAIL_USER
    
    msg['Subject'] = f"TICKET #{ticket_id} [{categoria}] - De: {nombre_usuario}"

    cuerpo_correo = f"""
NUEVO TICKET DE SOPORTE: #{ticket_id}

Nombre: {nombre_usuario}
Legajo/DNI: {legajo_usuario}
Correo: {email_usuario}
Categoría: {categoria}
Prioridad: {prioridad}

Descripción del problema:
{mensaje}

__________________________________________
Sistema de Gestión de Eventos
UTN Facultad Regional San Francisco
"""

    msg.attach(MIMEText(cuerpo_correo, 'plain'))

    file = request.files.get('adjunto')
    if file and file.filename != '':
        try:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(file.read())
            encoders.encode_base64(part)
            part.add_header(
                'Content-Disposition',
                f'attachment; filename={file.filename}',
            )
            msg.attach(part)
        except Exception as file_error:
            print("Error al adjuntar archivo:", file_error)

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(GMAIL_USER, GMAIL_PASS)
        server.send_message(msg)
        server.quit()

        return f"""
        <div style="font-family:Arial; text-align:center; margin-top:50px;">
            <h2 style="color:green;"> Hola, recibimos tu ticket  #{ticket_id}. Nuestro equipo lo revisará a la brevedad</h2>
            <p>Guardar el número de ticket por favor.</p>
            <a href="/">Volver al formulario</a>
        </div>
        """

    except Exception as e:
        print("Error:", e)
        return f"""
        <div style="font-family:Arial; text-align:center; margin-top:50px;">
            <h2 style="color:red;">Error al enviar el ticket</h2>
            <p>{e}</p>
            <a href="/">Volver</a>
        </div>
        """

if __name__ == '__main__':
    app.run(debug=True, port=5000)
