
# ============================================================
# WEB SERVICES HOMEWORK - STUDENTS AND REPORTS API
# ============================================================

from flask import Flask, request
import secrets
import time

app = Flask(__name__)


# ============================================================
# 1. TEMPORARY DATA STORAGE
# ============================================================

# Data is stored in memory and resets when Flask restarts.
students = []
reports = []

# Access tokens and refresh tokens are stored separately.
access_tokens = {}
refresh_tokens = {}

# Demo credentials for the homework.
# Replace these with real user authentication in production.
DEMO_USERNAME = "student"
DEMO_PASSWORD = "webservices123"

# Token lifetime in seconds.
ACCESS_TOKEN_LIFETIME = 300       # 5 minutes
REFRESH_TOKEN_LIFETIME = 3600     # 1 hour


# ============================================================
# 2. STUDENT CLASS
# ============================================================

class Student:
    def __init__(self, ID_S, FN, LN, DMjr, Level):
        self.ID_S = ID_S
        self.FN = FN
        self.LN = LN
        self.DMjr = DMjr
        self.Level = Level

    def to_dict(self):
        return {
            "ID_S": self.ID_S,
            "FN": self.FN,
            "LN": self.LN,
            "DMjr": self.DMjr,
            "Level": self.Level
        }


# ============================================================
# 3. REPORT CLASS
# ============================================================

class Report:
    def __init__(self, ID_R, Title, Type, K1, K2, K3, Release_Date):
        self.ID_R = ID_R
        self.Title = Title
        self.Type = Type
        self.K1 = K1
        self.K2 = K2
        self.K3 = K3
        self.Release_Date = Release_Date

    def to_dict(self):
        return {
            "ID_R": self.ID_R,
            "Title": self.Title,
            "Type": self.Type,
            "K1": self.K1,
            "K2": self.K2,
            "K3": self.K3,
            "Release_Date": self.Release_Date
        }


# ============================================================
# 4. HELPER FUNCTIONS
# ============================================================

# Read a JSON object and reject malformed or missing JSON.
def read_json():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return None

    return data


# Check that all required fields are present.
def has_fields(data, fields):
    return all(field in data for field in fields)


# Check that an ID is a positive integer, not a boolean.
def valid_id(value):
    return type(value) is int and value > 0


# ============================================================
# 5. TOKEN AUTHENTICATION
# ============================================================

# Generate an access token and a refresh token.
# Access tokens authorize student GET requests.
# Refresh tokens allow a client to obtain a new access token.

@app.route("/token", methods=["POST"])
def create_token():
    data = read_json()

    if data is None:
        return {"error": "A valid JSON object is required"}, 400

    if not has_fields(data, ["username", "password"]):
        return {"error": "Username and password are required"}, 400

    if (
        data["username"] != DEMO_USERNAME
        or data["password"] != DEMO_PASSWORD
    ):
        return {"error": "Invalid username or password"}, 401

    access_token = secrets.token_urlsafe(32)
    refresh_token = secrets.token_urlsafe(32)

    access_tokens[access_token] = {
        "expires_at": time.time() + ACCESS_TOKEN_LIFETIME
    }

    refresh_tokens[refresh_token] = {
        "expires_at": time.time() + REFRESH_TOKEN_LIFETIME
    }

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "Bearer",
        "expires_in": ACCESS_TOKEN_LIFETIME
    }, 200


# Check the Bearer access token in the Authorization header.
def authenticate():
    auth_header = request.headers.get("Authorization", "")

    parts = auth_header.split()

    if len(parts) != 2 or parts[0].lower() != "bearer":
        return {"error": "Access token required"}, 401

    token = parts[1]
    token_data = access_tokens.get(token)

    if token_data is None:
        return {"error": "Invalid access token"}, 401

    if time.time() >= token_data["expires_at"]:
        del access_tokens[token]
        return {"error": "Access token expired"}, 401

    return None


# Exchange a valid refresh token for a new access token.
@app.route("/token/refresh", methods=["POST"])
def refresh_access_token():
    data = read_json()

    if data is None:
        return {"error": "A valid JSON object is required"}, 400

    refresh_token = data.get("refresh_token")

    if not isinstance(refresh_token, str) or not refresh_token:
        return {"error": "Refresh token required"}, 400

    token_data = refresh_tokens.get(refresh_token)

    if token_data is None:
        return {"error": "Invalid refresh token"}, 401

    if time.time() >= token_data["expires_at"]:
        del refresh_tokens[refresh_token]
        return {"error": "Refresh token expired"}, 401

    new_access_token = secrets.token_urlsafe(32)

    access_tokens[new_access_token] = {
        "expires_at": time.time() + ACCESS_TOKEN_LIFETIME
    }

    return {
        "access_token": new_access_token,
        "token_type": "Bearer",
        "expires_in": ACCESS_TOKEN_LIFETIME
    }, 200


# ============================================================
# 6. HOME ENDPOINT
# ============================================================

@app.route("/", methods=["GET"])
def home():
    return {"message": "API is running!"}, 200


# ============================================================
# 7. STUDENT ENDPOINTS
# ============================================================

# POST /students - Add a student.
# Creation remains public; the professor's notes specifically
# require a token for GET student requests.

@app.route("/students", methods=["POST"])
def add_student():
    data = read_json()

    if data is None:
        return {"error": "A valid JSON object is required"}, 400

    required = ["ID_S", "FN", "LN", "DMjr", "Level"]

    if not has_fields(data, required):
        return {"error": "Missing required fields"}, 400

    if not valid_id(data["ID_S"]):
        return {"error": "ID_S must be a positive integer"}, 400

    if not all(
        isinstance(data[field], str) and data[field].strip()
        for field in ["FN", "LN"]
    ):
        return {"error": "FN and LN must be non-empty strings"}, 400

    if (
        type(data["DMjr"]) is not int
        or data["DMjr"] not in (0, 1)
        or type(data["Level"]) is not int
        or data["Level"] not in (1, 2, 3, 4)
    ):
        return {"error": "Invalid DMjr or Level"}, 400

    if any(s.ID_S == data["ID_S"] for s in students):
        return {"error": "Student ID already exists"}, 409

    student = Student(
        data["ID_S"],
        data["FN"].strip(),
        data["LN"].strip(),
        data["DMjr"],
        data["Level"]
    )

    students.append(student)

    return student.to_dict(), 201


# GET /students - Retrieve all students.
# A valid access token is required.

@app.route("/students", methods=["GET"])
def get_students():
    error = authenticate()

    if error:
        return error

    return [s.to_dict() for s in students], 200


# GET /students/<id> - Retrieve one student.
# A valid access token is required.

@app.route("/students/<int:student_id>", methods=["GET"])
def get_student(student_id):
    error = authenticate()

    if error:
        return error

    for student in students:
        if student.ID_S == student_id:
            return student.to_dict(), 200

    return {"error": "Student not found"}, 404


# PUT /students/<id> - Update a student (optional).

@app.route("/students/<int:student_id>", methods=["PUT"])
def update_student(student_id):
    data = read_json()

    if data is None:
        return {"error": "A valid JSON object is required"}, 400

    required = ["FN", "LN", "DMjr", "Level"]

    if not has_fields(data, required):
        return {"error": "Missing required fields"}, 400

    if not all(
        isinstance(data[field], str) and data[field].strip()
        for field in ["FN", "LN"]
    ):
        return {"error": "FN and LN must be non-empty strings"}, 400

    if (
        type(data["DMjr"]) is not int
        or data["DMjr"] not in (0, 1)
        or type(data["Level"]) is not int
        or data["Level"] not in (1, 2, 3, 4)
    ):
        return {"error": "Invalid DMjr or Level"}, 400

    for student in students:
        if student.ID_S == student_id:
            student.FN = data["FN"].strip()
            student.LN = data["LN"].strip()
            student.DMjr = data["DMjr"]
            student.Level = data["Level"]

            return student.to_dict(), 200

    return {"error": "Student not found"}, 404


# DELETE /students/<id> - Delete a student (optional).

@app.route("/students/<int:student_id>", methods=["DELETE"])
def delete_student(student_id):
    for student in students:
        if student.ID_S == student_id:
            students.remove(student)
            return {"message": "Student deleted"}, 200

    return {"error": "Student not found"}, 404


# ============================================================
# 8. REPORT ENDPOINTS
# ============================================================

# POST /reports - Add a report.

@app.route("/reports", methods=["POST"])
def add_report():
    data = read_json()

    if data is None:
        return {"error": "A valid JSON object is required"}, 400

    required = [
        "ID_R", "Title", "Type",
        "K1", "K2", "K3", "Release_Date"
    ]

    if not has_fields(data, required):
        return {"error": "Missing required fields"}, 400

    if not valid_id(data["ID_R"]):
        return {"error": "ID_R must be a positive integer"}, 400

    if any(r.ID_R == data["ID_R"] for r in reports):
        return {"error": "Report ID already exists"}, 409

    if not all(
        isinstance(data[field], str) and data[field].strip()
        for field in ["Title", "Type", "Release_Date"]
    ):
        return {"error": "Title, Type and Release_Date must be non-empty strings"}, 400

    report = Report(
        data["ID_R"],
        data["Title"].strip(),
        data["Type"].strip(),
        data["K1"],
        data["K2"],
        data["K3"],
        data["Release_Date"].strip()
    )

    reports.append(report)

    return report.to_dict(), 201


# GET /reports - Public: no token required.

@app.route("/reports", methods=["GET"])
def get_reports():
    return [r.to_dict() for r in reports], 200


# GET /reports/<id> - Public: no token required.

@app.route("/reports/<int:report_id>", methods=["GET"])
def get_report(report_id):
    for report in reports:
        if report.ID_R == report_id:
            return report.to_dict(), 200

    return {"error": "Report not found"}, 404


# PUT /reports/<id> - Update a report (optional).

@app.route("/reports/<int:report_id>", methods=["PUT"])
def update_report(report_id):
    data = read_json()

    if data is None:
        return {"error": "A valid JSON object is required"}, 400

    required = ["Title", "Type", "K1", "K2", "K3", "Release_Date"]

    if not has_fields(data, required):
        return {"error": "Missing required fields"}, 400

    if not all(
        isinstance(data[field], str) and data[field].strip()
        for field in ["Title", "Type", "Release_Date"]
    ):
        return {"error": "Title, Type and Release_Date must be non-empty strings"}, 400

    for report in reports:
        if report.ID_R == report_id:
            report.Title = data["Title"].strip()
            report.Type = data["Type"].strip()
            report.K1 = data["K1"]
            report.K2 = data["K2"]
            report.K3 = data["K3"]
            report.Release_Date = data["Release_Date"].strip()

            return report.to_dict(), 200

    return {"error": "Report not found"}, 404


# DELETE /reports/<id> - Delete a report (optional).

@app.route("/reports/<int:report_id>", methods=["DELETE"])
def delete_report(report_id):
    for report in reports:
        if report.ID_R == report_id:
            reports.remove(report)
            return {"message": "Report deleted"}, 200

    return {"error": "Report not found"}, 404


# ============================================================
# 9. START THE SERVER
# ============================================================

# This block must remain at the bottom of the file.
if __name__ == "__main__":
    app.run(debug=True)
