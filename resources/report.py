import uuid
from flask.views import MethodView
from flask_smorest import Blueprint, abort

from schemas import ReportSchema, ReportUpdateSchema
from db import reports

blp = Blueprint("Reports", "Reports", description="Operations on Reports")


@blp.route("/report/<string:report_id>")
class Report(MethodView):
    @blp.response(200, ReportSchema)
    def get(self, report_id):
        try:
            return reports[report_id]
        except KeyError:
            abort(404, message="Report not found.")

    def delete(self, report_id):
        try:
            del reports[report_id]
            return {"message": "Report deleted."}
        except KeyError:
            abort(404, message="Report not found.")

    @blp.arguments(ReportUpdateSchema)
    @blp.response(200, ReportSchema)
    def put(self, report_data, report_id):
        try:
            report = reports[report_id]

            report |= report_data

            return report
        except KeyError:
            abort(404, message="Report not found.")


@blp.route("/report")
class ReportList(MethodView):
    @blp.response(200, ReportSchema(many=True))
    def get(self):
        return reports.values()

    @blp.arguments(ReportSchema)
    @blp.response(201, ReportSchema)
    def post(self, report_data):
        for report in reports.values():
            if (
                report_data["title"] == report["title"]
                and report_data["student_id"] == report["student_id"]
            ):
                abort(400, message=f"Report already exists.")

        report_id = uuid.uuid4().hex
        report = {**report_data, "id": report_id}
        reports[report_id] = report

        return report