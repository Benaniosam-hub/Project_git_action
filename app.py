import os
from flask import Flask, request, jsonify
import psycopg2
from psycopg2.extras import RealDictCursor

app = Flask(__name__)

def get_db_connection():
    return psycopg2.connect(
        host=os.environ.get("DB_HOST", "database-1.c7wqac8my5ba.ap-south-2.rds.amazonaws.com"),
        database=os.environ.get("DB_NAME", "postgres"),
        user=os.environ.get("DB_USER", "postgres"),
        password=os.environ.get("DB_PASSWORD", "benaniosam")
    )

def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            age INTEGER NOT NULL
        );
    ''')
    conn.commit()
    cur.close()
    conn.close()

# This runs once automatically right when the container turns on
init_db()

@app.route('/hello', methods=['GET'])
def user_check():
    return jsonify({"sharlin": "Hello benanio"}), 200

@app.route('/students', methods=['GET'])
def get_students():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute('SELECT * FROM students;')
    students = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify(students), 200

@app.route('/students', methods=['POST'])
def add_student():
    data = request.get_json()
    name = data.get('name')
    age = data.get('age')
    
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        'INSERT INTO students (name, age) VALUES (%s, %s) RETURNING id;',
        (name, age)
    )
    student_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    
    return jsonify({"message": "Student added successfully!", "student_id": student_id}), 201

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)