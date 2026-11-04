import uuid
from flask import Flask, request
from flask_smorest import abort
from sqlalchemy import event

from db import db, Student, Report

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///object.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

with app.app_context():

    @event.listens_for(db.engine, "connect")
    def enable_foreign_keys(connection, record):
        cursor = connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    db.create_all()



# REPORT ENDPOINTS

@app.get("/report/<string:report_id>")
def get_report(report_id):
    report = db.session.get(Report, report_id)

    if report is None:
        abort(404, message="Report not found")

    return {
        "id": report.id,
        "title": report.title,
        "type": report.type,
        "student_id": report.student_id
    }


@app.post("/report")
def create_report():
    report_data = request.get_json()

    if not report_data or not all(
        field in report_data
        for field in ["title", "type", "student_id"]
    ):
        abort(400, message="Missing required fields: title, type and student_id")

    student = db.session.get(Student, report_data["student_id"])

    if student is None:
        abort(404, message="Student not found")

    existing_report = Report.query.filter_by(
        title=report_data["title"],
        type=report_data["type"],
        student_id=report_data["student_id"]
    ).first()

    if existing_report:
        abort(400, message="Report with the same title already exists")

    report = Report(
        id=uuid.uuid4().hex,
        title=report_data["title"],
        type=report_data["type"],
        student_id=report_data["student_id"]
    )

    db.session.add(report)
    db.session.commit()

    return {
        "id": report.id,
        "title": report.title,
        "type": report.type,
        "student_id": report.student_id
    }, 201


@app.get("/report")
def get_all_reports():
    reports = Report.query.all()

    return {
        "reports": [
            {
                "id": report.id,
                "title": report.title,
                "type": report.type,
                "student_id": report.student_id
            }
            for report in reports
        ]
    }


@app.delete("/report/<string:report_id>")
def delete_report(report_id):
    report = db.session.get(Report, report_id)

    if report is None:
        abort(404, message="Report not found")

    db.session.delete(report)
    db.session.commit()

    return {"message": "Report deleted successfully"}


@app.put("/report/<string:report_id>")
def update_report(report_id):
    report = db.session.get(Report, report_id)

    if report is None:
        abort(404, message="Report not found")

    report_data = request.get_json()

    if not report_data or "title" not in report_data or "type" not in report_data:
        abort(400, message="Missing required fields: title and type")

    if "student_id" in report_data:
        student = db.session.get(Student, report_data["student_id"])

        if student is None:
            abort(404, message="Student not found")

        report.student_id = report_data["student_id"]

    report.title = report_data["title"]
    report.type = report_data["type"]

    db.session.commit()

    return {
        "id": report.id,
        "title": report.title,
        "type": report.type,
        "student_id": report.student_id
    }



#=================================================
#=================================================


# STUDENT ENDPOINTS

@app.get("/student/<string:student_id>")
def get_student(student_id):
    student = db.session.get(Student, student_id)

    if student is None:
        abort(404, message="Student not found")

    return {
        "id": student.id,
        "fname": student.fname,
        "lname": student.lname
    }


@app.post("/student")
def add_student():
    student_data = request.get_json()

    if "fname" not in student_data or "lname" not in student_data:
        abort(400, message="Missing required fields: fname and lname")

    existing_student = Student.query.filter_by(
        fname=student_data["fname"],
        lname=student_data["lname"]
    ).first()

    if existing_student:
        abort(400, message="Student with the same name already exists")

    student = Student(
        id=uuid.uuid4().hex,
        fname=student_data["fname"],
        lname=student_data["lname"]
    )

    db.session.add(student)
    db.session.commit()

    return {
        "id": student.id,
        "fname": student.fname,
        "lname": student.lname
    }, 201


@app.get("/student")
def get_students():
    students = Student.query.all()

    return {
        "students": [
            {
                "id": student.id,
                "fname": student.fname,
                "lname": student.lname
            }
            for student in students
        ]
    }
