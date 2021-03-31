from odoo import models, fields, api, _
from datetime import datetime, date
from odoo.exceptions import ValidationError, UserError


class SchoolStudentAccess(models.TransientModel):
    _name = 'school.teacher.access'
    _description = 'Create Teacher Portal'

    def create_user_access(self):
        students = self.env['school.teacher'].browse(self._context.get('active_ids'))
        for student in students:
            student.create_user_access()