from ast import In

from db import db


class ReportModel(db.Model):
    __tablename__ = "reports"   #Sets the SQL table name to reports.

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), unique=False, nullable=False)
    type = db.Column(db.String(20), unique=False, nullable=False)

    student_id = db.Column(
        db.Integer, db.ForeignKey("students.id"), unique=False, nullable=False
    )
    student = db.relationship("StudentModel", back_populates="reports")

    #What back_populates Does Two-way awareness: Telling ReportModel.student to back_populates="reports" tells SQLAlchemy that "reports" is the matching relationship attribute on StudentModel (and vice versa).
    #In-memory synchronization: Before committing to the database, assigning report.student = Sana automatically updates Sana.reports in Python—and appending report to Sana.reports automatically sets report.student = Sana.
    #Explicit pairing: Both sides explicitly declare their db.relationship(), making it clear how each model names the related collection or object.