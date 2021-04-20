from odoo import models, fields, api, _
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError, UserError


class AccountablePerson(models.Model):
    _name = 'accountable.person'

    name = fields.Char(string="Name of Accountable Person", required=False, )
    identification_id = fields.Char(string="Identification No.", required=False, )
    responsible_id = fields.Many2one(comodel_name="res.users", string="Encoded By", required=False,
                                     default=lambda self: self.env.user.id)
    user_id = fields.Many2one(comodel_name="res.users", string="Related User", required=False)
    position_id = fields.Many2one(comodel_name="school.position", string="Position", required=False, )
    access_type = fields.Selection(string="Type of Access", selection=[('1', 'School'),
                                                                       ('2', 'Schools Division Office'),
                                                                       ('3', 'Regional Office')], required=False,
                                   default='1')
    email = fields.Char(string="Email", required=False, )
    phone = fields.Char(string="Mobile Number", required=False, )
    active = fields.Boolean(string="Active", default=True)
    user_check = fields.Boolean(string="Check Portal",  )

    def create_user_access(self):
        if self.env.user.has_group('snds.group_snds_user') or self.env.user.has_group('snds.group_snds_ro') or \
                self.env.user.has_group('snds.group_snds_sdo'):
            found = self.env['res.users'].sudo().search(
                ['|', ('login', 'ilike', self.email), ('name', 'ilike', self.name)])
            company_id = self.env.user.company_id
            if not found and not self.user_id:
                company = [(4, company_id.id)]
                groups_id = [(4, self.env.ref('base.group_user').id)]
                if self.access_type == '1':
                    groups_id.append((4, self.env.ref('snds.group_snds_school').id))
                if self.access_type == '2':
                    groups_id.append((4, self.env.ref('snds.group_snds_sdo').id))
                if self.access_type == '3':
                    groups_id.append((4, self.env.ref('snds.group_snds_ro').id))

                if self.env.user.has_group('snds.group_snds_sdo') and self.access_type == '3':
                    raise ValidationError(
                        _("You are not allowed to do this action. Please contact your administrator."))

                user_id = self.env['res.users'].sudo().create({'name': self.name,
                                                               'login': self.email,
                                                               'password': self.identification_id,
                                                               'company_ids': company,
                                                               'company_id': company_id.id,
                                                               'groups_id': groups_id})
                self.user_id = user_id.id
                self.user_check = True
                if self.user_id:
                    partner = self.env['res.partner'].sudo().search([('id', '=', self.user_id.partner_id.id)], limit=1)
                    if partner:
                        partner.sudo().update({'email': self.email})

            if found:
                found.sudo().write({'active': True})
                self.user_id = found.id
                self.user_check = True
        else:
            raise ValidationError(_("You are not allowed to do this action. Please contact your administrator."))


class SchoolPosition(models.Model):
    _name = 'school.position'
    _description = 'Position Information'
    _order = 'sequence, name'

    name = fields.Char(string="Position Name", required=False, )
    sequence = fields.Integer(string="Sequence", required=False, default=10)


class School(models.Model):
    _name = 'school.school'
    _description = 'School Information'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'

    name = fields.Char(string="School Name", required=False, )
    abbreviation = fields.Char(string="Abbreviation", required=False, )
    identification_id = fields.Char(string="School ID", required=False, )
    complete_address = fields.Text(string="School Address", required=False, )
    accountable_person = fields.Many2one(comodel_name="accountable.person", string="Accountable Person", required=False, )
    responsible_id = fields.Many2one(comodel_name="res.users", string="User ID", required=False, related='accountable_person.user_id', store=True)
    position_id = fields.Many2one(comodel_name="school.position", string="Position", required=False, related='accountable_person.position_id', store=True)
    email = fields.Char(string="Email", required=False, related='accountable_person.email', store=True)
    phone = fields.Char(string="Phone Number", required=False, related='accountable_person.phone', store=True)
    district_id = fields.Many2one(comodel_name="school.district", string="District", required=False, )
    region_id = fields.Many2one(comodel_name="res.region", string="Region", required=False, related="district_id.region_id", store=True)
    need_ids = fields.One2many(comodel_name="school.needs", inverse_name="school_id", string="Needs", required=False, )
    no_of_needs = fields.Integer(string="No. of Need(s)", required=False, compute='_compute_needs_count')

    @api.constrains('district_id')
    def check_district_id(self):
        if self.env.user.has_group('snds.group_snds_sdo'):
            if self.district_id:
                if self.district_id.user_id.id != self.env.user.id:
                    raise ValidationError(_("Please specify your own district."))

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