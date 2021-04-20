from odoo import models, fields, api


class ResRegions(models.Model):
    _name = 'res.region'
    _description = 'Regions'
    _order = 'name'

    @api.depends('description', 'code')
    def compute_name(self):
        for record in self:
            if record.code and record.description:
                name = "%s [%s]" % (record.description, record.code)
                record.update({'name': name})

    name = fields.Char(string='Name', compute='compute_name', store=True)
    description = fields.Char(string="Description", required=False, )
    user_id = fields.Many2one(comodel_name="res.users", string="Responsible", required=False,
                                     default=lambda self: self.env.user.id)
    code = fields.Char(string="Code", required=False, )


class SchoolDistrict(models.Model):
    _name = 'school.district'
    _description = 'School District'
    order = 'name'

    name = fields.Char(string="Name", required=False, )
    superintendent = fields.Char(string="Superintendent", required=False, )
    phone = fields.Char(string="Tel. Nos.", required=False, )
    email = fields.Char(string="Email", required=False, )
    region_id = fields.Many2one(comodel_name="res.region", string="Region", required=False, )
    user_id = fields.Many2one(comodel_name="res.users", string="Responsible", required=False,
                              default=lambda self: self.env.user.id)