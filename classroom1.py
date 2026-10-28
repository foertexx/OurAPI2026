from flask import Flask, request

app = Flask(__name__)

students = []


@app.get("/student") #return all students inside your list
def get_students():
    return {"students": students}

@app.post("/student") #add a new student to your list
def add_student():
    request_data = request.get_json()
    new_student = {
        "id": len(students) + 1,
        "Fname": request_data.get("Fname"),
        "Lname": request_data.get("Lname"),
        "reports": request_data.get("reports", [])
    }
    students.append(new_student)
    return {"message": "Student added successfully", "student": new_student}, 201
 #add a new report to a specific student
@app.post("/student/<int:student_id>/report")
def add_report(student_id):
    request_data = request.get_json()
    student = next((s for s in students if s["id"] == student_id),  None)
    if not student:
        return {"message": "Student not found"}, 404
    new_report = {
        "Title": request_data["Title"],
        "Type": request_data["Type"]
    }
    student["reports"].append(new_report)
    return new_report, 201
@app.get("/student/<int:student_id>")
def get_student(student_id):
    for student in students:
        if student["id"] == student_id:
            return {"student": student}

    return {"error": "Student not found"}, 404  

#
@app.get("/student/<int:student_id>/report")
def get_student_reports(student_id):
    student = next((s for s in students if s["id"] == student_id), None)
    if not student:
        return {"message": "Student not found"}, 404
    return {"reports": student["reports"]}