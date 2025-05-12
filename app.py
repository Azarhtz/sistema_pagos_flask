from flask import Flask, request, jsonify
from dotenv import load_dotenv
import psycopg2
import os
from datetime import datetime

load_dotenv()
app = Flask(__name__)
DATABASE_URL = os.getenv("DATABASE_URL")

def get_connection():
    return psycopg2.connect(DATABASE_URL, sslmode='require')

@app.route('/registrar_pedido', methods=['POST'])
def registrar_pedido():
    data = request.json
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO pedidos (fecha, nombre, producto, monto, metodo_pago, celular, tipo, token, estado, nombre_transferencia, nombre_yape)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        datetime.now(), data['nombre'], data['producto'], data['monto'], data['metodo_pago'],
        data['celular'], data['tipo'], data['token'], data['estado'],
        data['nombre_transferencia'], data['nombre_yape']
    ))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"status": "pedido registrado"})

@app.route('/registrar_mensaje', methods=['POST'])
def registrar_mensaje():
    data = request.json
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO mensajes (fecha, mensaje, nombre, monto, estado)
        VALUES (%s, %s, %s, %s, %s)
    """, (
        datetime.now(), data['mensaje'], data['nombre'], data['monto'], data['estado']
    ))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"status": "mensaje registrado"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
