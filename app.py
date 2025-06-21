from flask import Flask, render_template, request, redirect, url_for, Response
import sqlite3
import csv

app = Flask(__name__)

DATABASE = 'students.db'


def init_db():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                roll_number TEXT NOT NULL UNIQUE,
                subject1_marks INTEGER,
                subject2_marks INTEGER,
                total_marks INTEGER,
                percentage REAL
            )
        ''')
        conn.commit()


@app.route('/')
def index():
    search_query = request.args.get('search', '')
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        if search_query:
            cursor.execute("SELECT * FROM students WHERE name LIKE ? OR roll_number LIKE ?",
                           ('%' + search_query + '%', '%' + search_query + '%'))
        else:
            cursor.execute("SELECT * FROM students")
        students = cursor.fetchall()
    return render_template('index.html', students=students, search_query=search_query)


@app.route('/add', methods=['GET', 'POST'])
def add_student():
    if request.method == 'POST':
        name = request.form['name']
        roll_number = request.form['roll_number']
        subject1_marks = int(request.form['subject1_marks'])
        subject2_marks = int(request.form['subject2_marks'])

        # Validation for marks
        if subject1_marks > 100 or subject2_marks > 100:
            return "Marks cannot be more than 100!", 400

        total_marks = subject1_marks + subject2_marks
        percentage = (total_marks / 200) * 100

        with sqlite3.connect(DATABASE) as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(
                    "INSERT INTO students (name, roll_number, subject1_marks, subject2_marks, total_marks, percentage) VALUES (?, ?, ?, ?, ?, ?)",
                    (name, roll_number, subject1_marks, subject2_marks, total_marks, percentage))
                conn.commit()
            except sqlite3.IntegrityError:
                return "Roll number already exists!", 400
        return redirect(url_for('index'))
    return render_template('add_student.html')


@app.route('/update/<int:student_id>', methods=['GET', 'POST'])
def update_student(student_id):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        if request.method == 'POST':
            name = request.form['name']
            roll_number = request.form['roll_number']
            subject1_marks = int(request.form['subject1_marks'])
            subject2_marks = int(request.form['subject2_marks'])

            if subject1_marks > 100 or subject2_marks > 100:
                return "Marks cannot be more than 100!", 400

            total_marks = subject1_marks + subject2_marks
            percentage = (total_marks / 200) * 100

            cursor.execute(
                "UPDATE students SET name=?, roll_number=?, subject1_marks=?, subject2_marks=?, total_marks=?, percentage=? WHERE id=?",
                (name, roll_number, subject1_marks, subject2_marks, total_marks, percentage, student_id))
            conn.commit()
            return redirect(url_for('index'))

        cursor.execute("SELECT * FROM students WHERE id=?", (student_id,))
        student = cursor.fetchone()
    return render_template('update_student.html', student=student)


@app.route('/delete/<int:student_id>', methods=['POST'])
def delete_student(student_id):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM students WHERE id=?", (student_id,))
        conn.commit()
    return redirect(url_for('index'))


@app.route('/download')
def download_students():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM students")
        students = cursor.fetchall()

    def generate():
        yield 'ID,Name,Roll Number,English,Maths,Total Marks,Percentage\n'
        for student in students:
            yield f"{student[0]},{student[1]},{student[2]},{student[3]},{student[4]},{student[5]},{student[6]}\n"

    return Response(generate(), mimetype='text/csv', headers={"Content-Disposition": "attachment;filename=students.csv"})


if __name__ == '__main__':
    init_db()
    app.run(debug=True)