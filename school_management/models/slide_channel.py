from odoo import models, api, fields


class SlideChannelInherited(models.Model):
    _inherit = 'slide.channel'

    state = fields.Selection(string="Status", selection=[('open', 'Open Class'), ('close', 'Close'), ], required=False, )

    @api.model
    def create(self, values):
        res = super(SlideChannelInherited, self).create(values)
        if res:
            forum = self.env['forum.forum']
            channel = self.browse(res.id)
            vals = {
                'name': channel.name,
                'mode': 'discussions',
                'default_order': 'write_date desc',
            }
            result = forum.create(vals)
            channel.sudo().write({'forum_id': result.id})
        return res


class SlideChannelTagGroupInherited(models.Model):
    _inherit = 'slide.channel.tag'

    @api.depends('description', 'group_id')
    def compute_name(self):
        for record in self:
            if record.group_id and record.description:
                name = "[%s] %s" % (record.group_id.name, record.description)
                record.update({'name': name})

    name = fields.Char(string='Name', compute='compute_name', store=True)
    description = fields.Char(string="Description", required=False, )

