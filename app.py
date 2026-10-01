from flask import Flask, render_template, request, redirect
from database import conectar

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

app = Flask(__name__)

GMAIL_USER = "viguri@escuelasproa.edu.ar"
GMAIL_PASS = "ihjxgeibjzusijfz" 


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

    try:

        conexion = conectar()
        cursor = conexion.cursor()

        sql = """
        INSERT INTO tickets
        (nombre, legajo, email, prioridad, categoria, descripcion)
        VALUES (%s, %s, %s, %s, %s, %s)
        """

        valores = (
            nombre_usuario,
            legajo_usuario,
            email_usuario,
            prioridad,
            categoria,
            mensaje
        )

        cursor.execute(sql, valores)
        conexion.commit()

        ticket_id = cursor.lastrowid

        cursor.close()
        conexion.close()

    except Exception as error:

        print("Error al guardar el ticket:", error)

        return f"""
        <div style="font-family:Arial; text-align:center; margin-top:50px;">
            <h2 style="color:red;">Error al guardar el ticket</h2>
            <p>{error}</p>
            <a href="/">Volver al formulario</a>
        </div>
        """

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
                f'attachment; filename={file.filename}'
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

            <h2 style="color:green;">
                Hola, recibimos tu ticket #{ticket_id}.
            </h2>

            <p>
                Nuestro equipo lo revisará a la brevedad.
            </p>

            <p>
                Guardá el número de ticket: <strong>#{ticket_id}</strong>
            </p>

            <a href="/">
                Volver al formulario
            </a>

        </div>
        """


    except Exception as error:

        print("Error al enviar el correo:", error)

        return f"""
        <div style="font-family:Arial; text-align:center; margin-top:50px;">

            <h2 style="color:red;">
                El ticket fue guardado, pero hubo un error al enviar el correo.
            </h2>

            <p>
                Número de ticket: <strong>#{ticket_id}</strong>
            </p>

            <p>
                Error: {error}
            </p>

            <a href="/">
                Volver
            </a>

        </div>
        """
@app.route('/panel')
def panel():

    conexion = conectar()
    cursor = conexion.cursor(dictionary=True)

    cursor.execute("SELECT * FROM tickets ORDER BY id DESC")

    tickets = cursor.fetchall()

    cursor.close()
    conexion.close()

    return render_template('panel.html', tickets=tickets)

@app.route('/solucionar/<int:ticket_id>', methods=['POST'])
def solucionar(ticket_id):


    conexion = conectar()
    cursor = conexion.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM tickets WHERE id = %s",
        (ticket_id,)
    )

    ticket = cursor.fetchone()

    cursor.close()
    conexion.close()

    if not ticket:
        return "Ticket no encontrado"

    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute(
        """
        UPDATE tickets
        SET estado = 'solucionado'
        WHERE id = %s
        """,
        (ticket_id,)
    )

    conexion.commit()

    cursor.close()
    conexion.close()


    msg = MIMEMultipart()

    msg['From'] = GMAIL_USER
    msg['To'] = ticket['email']

    msg['Subject'] = f"Ticket #{ticket_id} solucionado"


    cuerpo_correo = f"""
Hola {ticket['nombre']},

Te informamos que tu ticket de soporte #{ticket_id} ha sido solucionado.

Categoría: {ticket['categoria']}

Descripción del problema:

{ticket['descripcion']}

Si el problema continúa, podés generar un nuevo ticket.

Saludos,

Equipo de Soporte
UTN Facultad Regional San Francisco
"""

    msg.attach(MIMEText(cuerpo_correo, 'plain'))

    try:

        server = smtplib.SMTP('smtp.gmail.com', 587)

        server.starttls()

        server.login(GMAIL_USER, GMAIL_PASS)

        server.send_message(msg)

        server.quit()

        print("Correo de solución enviado correctamente.")

    except Exception as error:

        print("Error al enviar correo:", error)


    return redirect('/panel')

if __name__ == '__main__':
    app.run(debug=True, port=5000)