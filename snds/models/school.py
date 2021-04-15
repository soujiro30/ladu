from odoo import models, fields, api, _
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError, UserError


class School(models.Model):
    _name = 'school.school'
    _description = 'School Information'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'

    name = fields.Char(string="School Name", required=False, )
    abbreviation = fields.Char(string="Abbreviation", required=False, )
    identification_id = fields.Char(string="School ID", required=False, )
    complete_address = fields.Text(string="School Address", required=False, )
    responsible_id = fields.Many2one(comodel_name="res.users", string="Accountable Person", required=False, )
    position_id = fields.Many2one(comodel_name="school.position", string="Position", required=False, )
    email = fields.Char(string="Email", required=False, )
    phone = fields.Char(string="Phone Number", required=False, )
    district_id = fields.Many2one(comodel_name="school.district", string="District", required=False, )
    region_id = fields.Many2one(comodel_name="res.region", string="Region", required=False, related="district_id.region_id", store=True)
    need_ids = fields.One2many(comodel_name="school.needs", inverse_name="school_id", string="Needs", required=False, )
    no_of_needs = fields.Integer(string="No. of Need(s)", required=False, compute='_compute_needs_count')

    def _compute_needs_count(self):
        needs_data = self.env['school.needs'].sudo().read_group([('school_id', 'in', self.ids)], ['school_id'], ['school_id'])
        result = dict((data['school_id'][0], data['school_id_count']) for data in needs_data)
        for need in self:
            need.no_of_needs = result.get(need.id, 0)

    @api.constrains('identification_id')
    def check_record_existence(self):
        for record in self:
            result = self.search([('id', '!=', record.id), ('identification_id', '=', record.identification_id)])
            if result:
                raise ValidationError(_("School Identification Number already exists!"))


class SchoolPosition(models.Model):
    _name = 'school.position'
    _description = 'Position Information'
    _order = 'sequence, name'

    name = fields.Char(string="Position Name", required=False, )
    sequence = fields.Integer(string="Sequence", required=False, default=10)