from db import db


class StudentModel(db.Model):
    __tablename__ = "students"

    id = db.Column(db.Integer, primary_key=True)
    fname = db.Column(db.String(20), unique=True, nullable=False)
    lname = db.Column(db.String(20), unique=True, nullable=False)

    reports = db.relationship(
        "ReportModel", back_populates="student", lazy="dynamic", cascade="all, delete"
    )

    #lazy="dynamic" ==> Returns a query object instead of a pre-loaded Python list
    #cascade="all, delete"  ==> Propagates ORM operations from parent to child