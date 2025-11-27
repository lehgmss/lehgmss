from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import mysql.connector
from mysql.connector import Error

app = Flask(__name__, static_folder='.')
CORS(app)

DB_CONFIG = {
    'host': '127.0.0.1',
    'user': 'root',
    'password': "",
    'database': 'escola'
}

def get_db_connection():
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        if connection.is_connected():
            return connection
    except Error as e:
        print(f" [!] Erro de conexão MySQL: {e}")
        return None

@app.route('/')
def index():
    return send_file('index.html')

@app.route('/alunos', methods=['GET'])
def get_alunos():
    conn = get_db_connection()
    if not conn: 
        return jsonify({"erro": "Erro de conexão com o banco MySQL"}), 500

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM alunos")
        results_list = cursor.fetchall()
        cursor.close()

        for aluno in results_list:
            n1 = float(aluno['n1'] or 0)
            n2 = float(aluno['n2'] or 0)
            n3 = float(aluno['n3'] or 0)
            
            aluno['n1'], aluno['n2'], aluno['n3'] = n1, n2, n3
            aluno['average'] = round((n1 + n2 + n3) / 3, 1)
            
        conn.close()
        return jsonify(results_list)

    except Exception as e:
        if conn.is_connected(): conn.close()
        return jsonify({"erro": str(e)}), 500

@app.route('/alunos', methods=['POST'])
def add_aluno():
    data = request.json
    conn = get_db_connection()
    if not conn: 
        return jsonify({"erro": "Sem conexão com MySQL"}), 500
    
    try:
        id_aluno = data.get('matricula') or data.get('id')
        nome = data.get('nome')
        turma = data.get('turma')
        n1 = float(data.get('nota1') or 0)
        n2 = float(data.get('nota2') or 0)
        n3 = float(data.get('nota3') or 0)
        
        query = "INSERT INTO alunos (id, nome, turma, n1, n2, n3) VALUES (%s, %s, %s, %s, %s, %s)"
        
        cursor = conn.cursor()
        cursor.execute(query, (id_aluno, nome, turma, n1, n2, n3))
        conn.commit()
        cursor.close()
        
        return jsonify({"mensagem": "Sucesso"}), 201

    except Exception as e:
        return jsonify({"erro": f"Erro ao salvar: {str(e)}"}), 400
    finally:
        if conn.is_connected(): conn.close()

@app.route('/alunos/<int:id>', methods=['PUT'])
def update_aluno(id):
    data = request.json
    conn = get_db_connection()
    if not conn: 
        return jsonify({"erro": "Sem conexão com MySQL"}), 500
    
    try:
        nome = data.get('nome')
        turma = data.get('turma')
        n1 = float(data.get('nota1') or data.get('n1') or 0)
        n2 = float(data.get('nota2') or data.get('n2') or 0)
        n3 = float(data.get('nota3') or data.get('n3') or 0)

        query = "UPDATE alunos SET nome=%s, turma=%s, n1=%s, n2=%s, n3=%s WHERE id=%s"

        cursor = conn.cursor()
        cursor.execute(query, (nome, turma, n1, n2, n3, id))
        conn.commit()
        cursor.close()
        return jsonify({"mensagem": "Atualizado"})
    except Exception as e:
        return jsonify({"erro": str(e)}), 500
    finally:
        if conn.is_connected(): conn.close()

@app.route('/alunos/<int:id>', methods=['DELETE'])
def delete_aluno(id):
    conn = get_db_connection()
    if not conn: 
        return jsonify({"erro": "Sem conexão com MySQL"}), 500
    
    try:
        query = "DELETE FROM alunos WHERE id = %s"

        cursor = conn.cursor()
        cursor.execute(query, (id,))
        conn.commit()
        cursor.close()
        return jsonify({"mensagem": "Removido"})
    except Exception as e:
        return jsonify({"erro": str(e)}), 500
    finally:
        if conn.is_connected(): conn.close()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)