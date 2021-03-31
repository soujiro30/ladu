from odoo import models, fields, api, _
from datetime import datetime, date
from odoo.exceptions import ValidationError, UserError


class SchoolStudentAccess(models.TransientModel):
    _name = 'school.student.access'
    _description = 'Create Student Portal'

    def create_user_access(self):
        students = self.env['school.student'].browse(self._context.get('active_ids'))
        for student in students:
            student.create_user_access()


class SchoolStudentChangeLevel(models.TransientModel):
    _name = 'school.student.change.level'
    _description = 'Change Level'

    teacher_id = fields.Many2one(comodel_name="school.teacher", string="Teacher Adviser", required=False)
    school_year_id = fields.Many2one(comodel_name="school.year", string="School Year", required=False, )
    grade_id = fields.Many2one(comodel_name="slide.channel.tag", string="Current Grade/Section", required=False, )

    def change_year_level(self):
        if self.env.user.has_group('school_management.group_school_access_right') or \
                self.env.user.has_group('school_management.group_school_principal') or \
                self.env.user.has_group('school_management.group_school_teacher'):
            students = self.env['school.student'].browse(self._context.get('active_ids'))
            for student in students:
                student.write({'teacher_id': self.teacher_id.id,
                               'school_year_id': self.school_year_id.id,
                               'grade_id': self.grade_id.id
                               })
        else:
            raise ValidationError(_("You cannot change the level of the student. Please contact the administrator!"))
