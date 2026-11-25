import uuid
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from db import students
from schemas import StudentSchema


blp = Blueprint("Students", "students", description="Operations on students")


@blp.route("/student/<string:student_id>")
class Student(MethodView):
    @blp.response(200, StudentSchema)
    def get(cls, student_id):
        try:
            # You presumably would want to include the student's details here too
            # More on that when we look at databases
            return students[student_id]
        except KeyError:
            abort(404, message="Student not found.")

    def delete(cls, student_id):
        try:
            del students[student_id]
            return {"message": "Student deleted."}
        except KeyError:
            abort(404, message="Student not found.")


@blp.route("/student")
class StudentList(MethodView):
    @blp.response(200, StudentSchema(many=True))
    def get(cls):
        return students.values()

    @blp.arguments(StudentSchema)
    @blp.response(201, StudentSchema)

    def post(self, student_data):
        for student in students.values():
            if (
                student_data["fname"] == student["fname"]
                and student_data["lname"] == student["lname"]
            ):
                abort(400, message="Student already exists.")

        student_id = uuid.uuid4().hex
        student = {**student_data, "id": student_id}
        students[student_id] = student

        return student