from odoo import models, api, fields


class ForumInherited(models.Model):
    _inherit = 'forum.forum'
    _description = 'Forum'

    karma_ask = fields.Integer(string='Ask questions', default=0)
    karma_answer = fields.Integer(string='Answer questions', default=0)
    karma_edit_own = fields.Integer(string='Edit own posts', default=0)
    karma_comment_own = fields.Integer(string='Comment own posts', default=0)
    karma_comment_all = fields.Integer(string='Comment all posts', default=0)