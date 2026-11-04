
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Student(db.Model):
    id = db.Column(db.String(32), primary_key=True)
    fname = db.Column(db.String(100), nullable=False)
    lname = db.Column(db.String(100), nullable=False)

    reports = db.relationship(
        "Report",
        back_populates="student",
        cascade="all, delete-orphan"
    )


class Report(db.Model):
    id = db.Column(db.String(32), primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(100), nullable=False)

    student_id = db.Column(
        db.String(32),
        db.ForeignKey("student.id"),
        nullable=False
    )

    student = db.relationship(
        "Student",
        back_populates="reports"
    )
