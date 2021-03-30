from odoo import models, fields, api, _


class ResUsersInherited(models.Model):
    _inherit = 'res.users'

    grade_id = fields.Many2one(comodel_name="school.grade", string="Grade Level", required=False, )