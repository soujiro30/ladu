import base64
from random import choice
from string import digits
import itertools
from werkzeug import url_encode
import pytz

from odoo import api, fields, models, _, SUPERUSER_ID
from odoo.exceptions import ValidationError, AccessError
from odoo.modules.module import get_module_resource

SUFFIX = [
    ('jr', 'JR'),
    ('sr', 'SR'),
    ('iii', 'III'),
    ('iv', 'IV'),
    ('v', 'V'),
    ('vi', 'VI'),
    ('vii', 'VII')
]


class SchoolStudent(models.Model):
    _name = 'school.student'
    _description = 'Student Information'
    _order = 'name'

    @api.model
    def _default_image(self):
        image_path = get_module_resource('hr', 'static/src/img', 'default_image.png')
        return base64.b64encode(open(image_path, 'rb').read())

    def get_default_teacher(self):
        user_id = self.env['school.teacher'].search([('user_id', '=', self.env.user.id)])
        if user_id:
            return user_id.id
        else:
            return False

    name = fields.Char(string="Name", required=False, )
    first_name = fields.Char(string="First Name", required=False, )
    middle_name = fields.Char(string="Middle Name", required=False, )
    last_name = fields.Char(string="Last Name", required=False, )
    suffix = fields.Selection(SUFFIX, string="Suffix")
    identification_id = fields.Char(string="ID No.", required=False, )
    phone = fields.Char(string="Phone Number", required=False, )
    teacher_id = fields.Many2one(comodel_name="school.teacher", string="Teacher Adviser", required=False, default=get_default_teacher)
    school_year_id = fields.Many2one(comodel_name="school.year", string="School Year", required=False, )
    grade_id = fields.Many2one(comodel_name="slide.channel.tag", string="Current Grade/Section", required=False, )
    year_level_id = fields.Many2one(comodel_name="slide.channel.tag.group", string="Current Level",
                                    required=False, related='grade_id.group_id', store=True)
    user_id = fields.Many2one('res.users', 'User ID', ondelete="cascade",
                              required=False)
    gender = fields.Selection(string="Gender", selection=[('male', 'Male'), ('female', 'Female'), ], required=False, )
    birthday = fields.Date(string="Birthday", required=False, )
    marital = fields.Selection(string="Marital Status", selection=[('single', 'Single'), ('married', 'Married'),
                                                                   ('widowed', 'Widowed'), ('separated', 'Separated'),
                                                                   ('singleparent', 'Single Parent')], required=False, )
    complete_address = fields.Text(string="Complete Address", required=False, )
    image_1920 = fields.Image(default=_default_image)
    user_check = fields.Boolean(string="Check User Portal")
    state = fields.Selection(string="Status", selection=[('in', 'In School'), ('out', 'Drop Out'), ], required=False, default='in')

    @api.constrains('identification_id')
    def check_record_existence(self):
        for record in self:
            result = self.search([('id', '!=', record.id), ('identification_id', '=', record.identification_id)])
            if result:
                raise ValidationError(_("Identification Number already exists!"))

    @api.onchange('first_name', 'middle_name', 'last_name', 'suffix')
    def onchange_name(self):

        name = ''
        period = '.'
        fname = ''
        lname = ''
        mname = ''
        if self.last_name:
            lname = self.last_name.title().strip()
            name = '%s' % lname

        if self.first_name and self.last_name:
            fname = self.first_name.title().strip()
            lname = self.last_name.title().strip()
            name = '%s %s' % (fname, lname)

        if self.first_name and self.last_name and self.middle_name:
            fname = self.first_name.title().strip()
            lname = self.last_name.title().strip()
            mname = self.middle_name.title().strip()
            name = '%s %s%s %s' % (fname, mname[:1], period, lname)

        if self.first_name and self.last_name and self.middle_name and self.suffix:
            fname = self.first_name.title().strip()
            lname = self.last_name.title().strip()
            mname = self.middle_name.title().strip()
            suffix = self._get_suffix(self.suffix)
            name = '%s %s%s %s %s' % (fname, mname[:1], period, lname, suffix)

        if self.first_name and self.last_name and self.suffix and not self.middle_name:
            fname = self.first_name.title().strip()
            lname = self.last_name.title().strip()
            suffix = self._get_suffix(self.suffix)
            name = '%s %s %s' % (fname,  lname, suffix)

        self.name = name
        self.first_name = fname.title().strip()
        self.middle_name = mname.title().strip()
        self.last_name = lname.title().strip()

    def _get_suffix(self, values):
        if values == 'jr':
            suffix = 'Jr'

        elif values == 'sr':
            suffix = 'Sr'

        elif values == 'ii':
            suffix = 'II'

        elif values == 'iii':
            suffix = 'III'

        elif values == 'iv':
            suffix = 'IV'

        elif values == 'v':
            suffix = 'V'

        elif values == 'vi':
            suffix = 'VI'

        elif values == 'vii':
            suffix = 'VII'

        else:
            suffix = ''

        return suffix

    def create_user_access(self):
        if self.env.user.has_group('school_management.group_school_access_right') or \
                self.env.user.has_group('school_management.group_school_principal') or \
                self.env.user.has_group('school_management.group_school_teacher'):
            found = self.env['res.users'].sudo().search(['|', ('login', 'ilike', self.identification_id), ('name', 'ilike', self.name)])
            company_id = self.env.user.company_id
            if not found and not self.user_id:
                company = [(4, company_id.id)]
                groups_id = [(4, self.env.ref('school_management.group_school_student').id), (4, self.env.ref('base.group_user').id)]
                user_id = self.env['res.users'].sudo().create({'name': self.name,
                                                               'login': self.identification_id,
                                                               'password': self.identification_id,
                                                               'company_ids': company,
                                                               'company_id': company_id.id,
                                                               'groups_id': groups_id})
                self.user_id = user_id.id
                self.user_check = True

            if found:
                found.write({'active': True})
                self.user_id = found.id
                self.user_check = True
        else:
            raise ValidationError(_("You are not allowed for this action. Please contact your administrator."))
