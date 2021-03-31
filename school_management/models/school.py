from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from datetime import datetime, date


class SchoolYear(models.Model):
    _name = 'school.year'
    _description = 'School Year'
    _order = 'name'

    name = fields.Char(string="School Year", required=False)
    date_start = fields.Date(string="Date Start", required=False, )
    date_stop = fields.Date(string="Date Stop", required=False, )
    default = fields.Boolean(string="Default", default=False)

    @api.onchange('date_start', 'date_stop')
    def _onchange_date_start_date_stop(self):
        if self.date_start and self.date_stop:
            start = (self.date_start).strftime('%Y')
            end = (self.date_stop).strftime('%Y')
            self.name = 'S.Y. %s-%s' % (start, end)

    def set_as_default(self):
        self.default = True
        for record in self.search([('id', '!=', self.id)]):
            if record:
                record.write({'default': False})
        model_obj = self.env['ir.model.data']
        data_id = model_obj._get_id('school_management', 'school_year_tree_view')
        view_id = model_obj.sudo().browse(data_id).res_id
        return {'type': 'ir.actions.client',
                'tag': 'reload',
                'name': _('SSS Matrix'),
                'res_model': 'hr.sss.matrix',
                'view_type': 'tree',
                'view_mode': 'tree',
                'view_id': view_id,
                'target': 'current',
                'nodestroy': True}


class School(models.Model):
    _name = 'school.school'
    _description = 'School Information'
    _order = 'name'

    name = fields.Char(string="School Name", required=False, )
    abbreviation = fields.Char(string="Abbreviation", required=False, )
    school_id = fields.Char(string="School ID", required=False, )
    complete_address = fields.Text(string="School Address", required=False, )
    principal = fields.Char(string="Principal", required=False, )
    teacher_ids = fields.One2many(comodel_name="school.teacher", inverse_name="school_id", string="Teachers", required=False, )

    @api.constrains('school_id')
    def check_record_existence(self):
        for record in self:
            result = self.search([('id', '!=', record.id), ('school_id', '=', record.school_id)])
            if result:
                raise ValidationError(_("Identification Number already exists!"))


class SchoolPosition(models.Model):
    _name = 'school.position'
    _description = 'Position Information'
    _order = 'name'

    name = fields.Char(string="Position Name", required=False, )







