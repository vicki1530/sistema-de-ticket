from flask import Flask, render_template, request
import webbrowser
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)

GMAIL_USER = "gestioneventocontrasena12@gmail.com"
GMAIL_PASS = "jlrwsofpaxaksxoq" 

@app.route('/')
def home():
    return render_template('soporte.html')

@app.route('/enviar-ticket', methods=['POST'])
def enviar_ticket():

    nombre_usuario = request.form.get('nombre')
    email_usuario = request.form.get('email')
    categoria = request.form.get('categoria')
    mensaje = request.form.get('descripcion')

    msg = MIMEMultipart()
    msg['From'] = GMAIL_USER
    msg['To'] = GMAIL_USER
    msg['Subject'] = f"TICKET [{categoria}] - De: {nombre_usuario}"

    cuerpo_correo = f"""
NUEVO TICKET DE SOPORTE

Nombre: {nombre_usuario}
Correo: {email_usuario}
Categoría: {categoria}

Descripción del problema:

{mensaje}

----------------------------------------
Sistema de Gestión de Eventos
UTN Facultad Regional San Francisco
"""

    msg.attach(MIMEText(cuerpo_correo, 'plain'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(GMAIL_USER, GMAIL_PASS)
        server.send_message(msg)
        server.quit()

        return """
        <div style="font-family:Arial; text-align:center; margin-top:50px;">
            <h2 style="color:green;">¡Ticket enviado correctamente!</h2>
            <p>El equipo de soporte fue notificado.</p>
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
