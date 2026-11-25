from marshmallow import Schema, fields


class ReportSchema(Schema):
    id = fields.Str(dump_only=True)
    title = fields.Str(required=True)
    type = fields.Str(required=True)
    student_id = fields.Str(required=True)


class ReportUpdateSchema(Schema):
    title = fields.Str()
    type = fields.Str()


class StudentSchema(Schema):
    id = fields.Str(dump_only=True)
    fname = fields.Str(required=True)
    lname = fields.Str(required=True)