from odoo import models, api, fields


class SlideChannelInherited(models.Model):
    _inherit = 'slide.channel'

    teacher_id = fields.Many2one(comodel_name="school.teacher", string="Teacher", required=False, )
    state = fields.Selection(string="Status", selection=[('open', 'Open Class'), ('close', 'Close'), ], required=False, )
    grade_ids = fields.One2many(comodel_name="slide.channel.grade", inverse_name="slide_channel_id", string="Grade", required=False, )

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


class SlideChannelGrade(models.Model):
    _name = 'slide.channel.grade'
    _description = 'Grade Slide Channel'

    grade_id = fields.Many2one(comodel_name="school.grade", string="Grade", required=False, )
    slide_channel_id = fields.Many2one(comodel_name="slide.channel", string="Slide Channel", required=False, )