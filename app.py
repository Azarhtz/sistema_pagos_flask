from flask import Flask, request, jsonify
from dotenv import load_dotenv
import psycopg2
import os
from datetime import datetime

from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "✅ El backend Flask está funcionando correctamente"

# (Aquí van tus otras rutas, como /registrar_pedido)


load_dotenv()
app = Flask(__name__)
DATABASE_URL = os.getenv("DATABASE_URL")

def get_connection():
    return psycopg2.connect(DATABASE_URL, sslmode='require')

@app.route('/registrar_pedido', methods=['POST'])

@app.route('/registrar_pedido', methods=['POST'])
def registrar_pedido():
    data = request.json
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO pedidos (
            fecha, nombre, producto, monto, metodo_pago, celular, tipo, token,
            estado, nombre_transferencia, nombre_yape
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        datetime.now(),
        data['nombre'],
        data['producto'],
        data['monto'],
        data['metodo_pago'],
        data['celular'],
        data['tipo'],
        data.get('token', ''),  # token puede estar vacío
        data['estado'],
        data['nombre_transferencia'],
        data['nombre_yape']
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

@app.route('/confirmar', methods=['POST'])
def confirmar():
    try:
        data = request.get_json()
        nombre_yape = data.get('nombre_yape')
        producto = data.get('producto')

        if not nombre_yape or not producto:
            return jsonify({"status": "faltan datos"}), 400

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT m.id, p.id 
            FROM mensajes m 
            JOIN pedidos p ON m.nombre = p.nombre_yape 
            WHERE m.estado = 'pendiente' AND p.estado != 'confirmado' 
            AND p.producto = %s AND p.nombre_yape = %s
            LIMIT 1
        """, (producto, nombre_yape))
        resultado = cur.fetchone()

        if resultado:
            mensaje_id, pedido_id = resultado

            cur.execute("UPDATE mensajes SET estado = 'usado' WHERE id = %s", (mensaje_id,))
            cur.execute("UPDATE pedidos SET estado = 'confirmado' WHERE id = %s", (pedido_id,))
            cur.execute("""
                INSERT INTO confirmaciones (pedido_id, mensaje_id, producto, estado)
                VALUES (%s, %s, %s, %s)
            """, (pedido_id, mensaje_id, producto, "confirmado"))

            conn.commit()
            cur.close()
            conn.close()

            return jsonify({"status": "confirmado"}), 200
        else:
            return jsonify({"status": "no encontrado o ya confirmado"}), 404

    except Exception as e:
        print("❌ Error en confirmación:", e)
        return jsonify({"status": "error", "detalle": str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
