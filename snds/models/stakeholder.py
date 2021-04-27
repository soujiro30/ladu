from odoo import models, fields, api, _
from datetime import datetime, date
from odoo.exceptions import ValidationError, UserError
# from urlparse import urljoin


class StakeholderProject(models.Model):
    _name = 'stakeholder.project'
    _description = 'Donations'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name desc'

    name = fields.Char(string="Code", required=False, default="New")
    user_id = fields.Many2one(comodel_name="res.users", string="Contributors", required=False, default=lambda self: self.env.user.id)
    stakeholder_name = fields.Char(string="Name of Stakeholder", required=False, )
    date_filed = fields.Date(string="Date Filed", required=False, default=fields.Date.context_today,)
    email = fields.Char(string="Email", required=False, )
    phone = fields.Char(string="Mobile Number", required=False, )
    need_id = fields.Many2one(comodel_name="school.needs", string="Needs Reference", required=False, )
    description = fields.Text(string="Description", required=False, )
    state = fields.Selection(string="Status", selection=[('draft', 'Inquire'), ('send', 'Sent Project'), ('approve', 'Approved'),
                                                         ('done', 'Project Implemented'), ('cancel', 'Cancelled'),
                                                         ('refuse', 'Refused')], required=False, default='draft')
    amount_donated = fields.Float(string="Amount Donated",  required=False, compute="compute_amount_donated", store=True)
    product_id = fields.Many2one(comodel_name="school.product", string="Donated Item(s)", required=False,
                                 related="need_id.product_id", store=True)
    category_id = fields.Many2one(comodel_name="school.product.category", string="Category", required=False,
                                  related="product_id.category_id", store=True)
    school_id = fields.Many2one(comodel_name="school.school", string="School", required=False,
                                related="need_id.school_id", store=True)
    quantity = fields.Float(string="Quantity", required=False, related="need_id.quantity")
    amount = fields.Float(string="Estimated Amount", required=False, related="need_id.amount")
    no_of_beneficiary_student = fields.Integer(string="No. of Beneficiary Student",
                                               required=False, related="need_id.no_of_beneficiary_student")
    no_of_beneficiary_personnel = fields.Integer(string="No. of Beneficiary Personnel",
                                                 required=False, related="need_id.no_of_beneficiary_personnel")
    date_implemented = fields.Date(string="Date of Implementation", required=False,
                                   related="need_id.date_implemented")
    responsible_id = fields.Many2one(comodel_name="res.users", string="Accountable Person", required=False,
                                     related="school_id.responsible_id")
    responsible_id_email = fields.Char(string="Personnel Email", required=False, related="school_id.email")
    responsible_id_phone = fields.Char(string="Phone Number", required=False, related="school_id.phone")
    inquire = fields.Boolean(string="Send a message to this school",  default=False)
    amount_ids = fields.One2many(comodel_name="stakeholder.project.donate", inverse_name="project_id", string="Donated Amount", required=False, )

    @api.depends('amount_ids')
    def compute_amount_donated(self):
        for record in self:
            amount_donated = 0.0
            if record.amount_ids:
                for rec in record.amount_ids:
                    amount_donated += rec.amount
            record.update({'amount_donated': amount_donated})

    @api.onchange('amount_donated', 'need_id')
    def _onchange_amount_donated(self):
        if self.amount_donated and self.need_id:
            if self.need_id.amount < self.amount_donated:
                raise ValidationError(_("Your donation amount is greater than the amount needed."))

    @api.constrains('amount_donated', 'need_id')
    def check_amount_donated(self):
        if self.amount_donated and self.need_id:
            if self.need_id.amount < self.amount_donated:
                raise ValidationError(_("Your donation amount is greater than the amount needed."))

    @api.onchange('user_id')
    def onchange_user_id(self):
        if self.user_id:
            self.stakeholder_name = self.user_id.name
            self.email = self.user_id.login

    def get_mail_channel(self, sender, receiver):
        mail_channels = self.env['mail.channel']
        if sender and receiver:
            sender_partner = sender.partner_id
            receiver_partner = receiver.partner_id
            if sender_partner and receiver_partner:
                mail_channels_res = mail_channels.sudo().search([('public', '=', 'private'), ('channel_type', '=', 'chat'),
                                                                 ('channel_partner_ids', 'in', [sender_partner.id, receiver_partner.id]),
                                                                 '|', ('name', 'ilike', sender_partner.name + ', ' + receiver_partner.name),
                                                                 ('name', 'ilike', receiver_partner.name + ', ' + sender_partner.name)], limit=1, order='create_date desc')
                if mail_channels_res:
                    result = mail_channels_res
                else:
                    partners = [(4, sender_partner.id, None), (4, receiver_partner.id, None)]
                    mail_channel_create = mail_channels.sudo().create({'name': receiver_partner.name + ', ' + sender_partner.name,
                                                                       'public': 'private',
                                                                       'channel_type': 'chat',
                                                                       'channel_partner_ids': partners})
                    result = mail_channel_create
                return result

    def create_mail_message(self, channel, sender, receiver, body):
        if channel and sender and receiver:
            mail_message = self.env['mail.message']
            sender_partner = sender.partner_id
            receiver_partner = receiver.partner_id
            if sender_partner and receiver_partner:
                vals = {
                    'subject': 'Notification Approval',
                    'date': datetime.now(),
                    'email_from': '\"' + sender_partner.name + '\"<' + sender_partner.email + '>',
                    'author_id': sender_partner.id,
                    'record_name': channel.name,
                    'model': 'mail.channel',
                    'res_id': int(channel.id),
                    'message_type': 'comment',
                    'subtype_id': self.env.ref('mail.mt_comment').id,
                    'reply_to': '\"' + sender_partner.name + '\"<' + sender_partner.email + '>',
                    'channel_ids': [(4, channel.id, None)],
                    'body': body
                }
                result = mail_message.sudo().create(vals)
                return result

    def action_send(self):
        if self.inquire == False or not self.inquire:
            raise ValidationError(_("You cannot send this inquiry. Please check the inquiry checkbox and complete the information below."))
        self.state = 'send'
        sender = self.user_id
        receiver = self.responsible_id
        channel = self.get_mail_channel(sender, receiver)
        body = "<p>Hello Sir/Maam @" + self.responsible_id.name + ", I would like to inquire about the needs of your school with the reference number " + self.need_id.name + ".</p>"
        self.create_mail_message(channel, sender, receiver, body)
        model_obj = self.env['ir.model.data']
        data_id = model_obj._get_id('snds', 'stakeholder_project_tree_view')
        view_id = model_obj.sudo().browse(data_id).res_id
        return {'type': 'ir.actions.client',
                'tag': 'reload',
                'name': _('Stakeholder Inquiries'),
                'res_model': 'stakeholder.project',
                'view_mode': 'tree',
                'view_id': view_id,
                'target': 'current',
                'nodestroy': True}

    def send_email(self):
        mail_mail = self.env['mail.mail']
        for project in self:
            if project.user_id.partner_id or project.email:
                sender_email = project.responsible_id_email
                author = project.responsible_id.company_id.partner_id if project.responsible_id.company_id.partner_id else project.responsible_id.partner_id
                receiver_email = project.email
                header = "<p>Dear " + self.stakeholder_name + ",</p>"
                body_html = header
                if project.state == 'refuse':
                    body_html += "<p>Thank you for participating on our project necessity however your request has been refuse. You may contact us if you have any verification. <br/>Thank You! </p>"
                if project.state == 'approve':
                    body_html += "<p>Congratulations! Your project request has been approved!<br/>You may see on your portal for the verification of your donation. Thank you! </p>"
                if project.state == 'done':
                    body_html += "<p>Congratulations! your donation is now implemented to the school. <br/>We are looking forward for more projects to come together with your partnership. <br/>Godbless and Thank you!</p>"
                body_html += "<br/><p>Best regards, </p><p><b> " + project.school_id.responsible_id.name + "</b></p><p>"+ project.school_id.position_id.name +"</p><p>" + project.school_id.name + "</p><br/>"

                vals = {
                    'subject': "Wish List System Project Status",
                    'date': datetime.now(),
                    'email_from': '\"' + author.name + '\"<' + sender_email + '>',
                    'email_to': receiver_email,
                    'author_id': author.id,
                    'recipient_ids': [(4, project.user_id.partner_id.id)],
                    # 'reply_to': '\"' + author.name + '\"<' + sender_email + '>',
                    'body_html': body_html,
                    'auto_delete': False,
                    'message_type': 'email',
                    'notification': True,
                    'mail_server_id': self.env.ref('snds.config_email_server_gmail_noreply').id,
                    'model': project._name,
                    'res_id': project.id,
                }
                result = mail_mail.sudo().create(vals)
                result.sudo().send()
                return result

    def action_approve(self):
        if self.school_id.responsible_id.id == self.env.user.id:
            self.state = "approve"
            need = self.need_id
            need.write({'state': 'ongoing'})
            sender = self.responsible_id
            receiver = self.user_id
            channel = self.get_mail_channel(sender, receiver)
            body = "<p>Hello Sir/Maam @" + self.user_id.name + ", Congratulations! Your project request has been approved! Please see on your portal with this reference numebr " + self.name + ".</p>"
            self.create_mail_message(channel, sender, receiver, body)
            self.send_email()
        else:
            raise ValidationError(_("You are not allowed to approve this project. Please contact the administrator"))

    def action_done(self):
        if self.school_id.responsible_id.id == self.env.user.id and self.amount_donated > 0.00:
            self.state = "done"
            need = self.need_id
            need.compute_actual_percentage()
            sender = self.responsible_id
            receiver = self.user_id
            channel = self.get_mail_channel(sender, receiver)
            body = "<p>Hello Sir/Maam @" + self.user_id.name + ", <p>Congratulations! your donation is now implemented to the school. <br/>We are looking forward for more projects to come together with your partnership. <br/>Godbless and Thank you!</p>"
            self.create_mail_message(channel, sender, receiver, body)
            self.send_email()
        else:
            raise ValidationError(_("You are not allowed to complete this project. Please contact the administrator"))

    def action_cancel(self):
        if self.user_id.id == self.env.user.id:
            self.state = 'cancel'
        else:
            raise ValidationError(_("You are not allowed to cancel this project. Please contact the administrator"))

    def action_refuse(self):
        if self.school_id.responsible_id.id == self.env.user.id:
            self.state = 'refuse'
            sender = self.responsible_id
            receiver = self.user_id
            channel = self.get_mail_channel(sender, receiver)
            body = "<p>Thank you for participating on our project necessity however your request has been refuse. You may contact us if you have any verification. <br/>Thank You! </p>"
            self.create_mail_message(channel, sender, receiver, body)
            self.send_email()
        else:
            raise ValidationError(_("You are not allowed to refuse this project. Please contact the administrator"))

    @api.model
    def create(self, values):
        if values.get('name', 'New') == 'New':
            seq_date = None
            values['name'] = self.env['ir.sequence'].next_by_code('stakeholder.project', sequence_date=seq_date) or '/'
        return super(StakeholderProject, self).create(values)


class StakeholderProjectAmount(models.Model):
    _name = 'stakeholder.project.donate'
    _description = 'Amount Donated'

    project_id = fields.Many2one(comodel_name="stakeholder.project", string="Project", required=False, )
    amount = fields.Float(string="Amount Donated",  required=False, )

    @api.model
    def create(self, values):
        res = super(StakeholderProjectAmount, self).create(values)
        if res:
            if values['amount'] in values:
                if values['amount'] == 0.00:
                    raise ValidationError(_("Please check the amount to be donated."))
            project = self.env['stakeholder.project'].browse(values['project_id'])
            need = self.env['school.needs'].search([('id', '=', project.need_id.id)])
            if need:
                total_donations = 0.00
                for donate in need.stakeholder_approved_ids:
                    total_donations += donate.amount_donated
                if total_donations > need.amount:
                    amount = need.amount - (total_donations - values['amount'])
                    raise ValidationError(_("Amount donated is greater than the actual needed for the project. Amount needed is P %s left" % amount))
        return res