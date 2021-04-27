from odoo import models, fields, api, _
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError, UserError


class SchoolProductCategory(models.Model):
    _name = 'school.product.category'
    _description = 'Product Category'
    _order = 'name'

    name = fields.Char(string="Category", required=False, )
    description = fields.Text(string="Brief Description", required=False, )
    product_ids = fields.One2many(comodel_name="school.product", inverse_name="category_id", string="Products", required=False, )
    no_of_products = fields.Integer(string="No of. Items", required=False, compute="_compute_product_count")
    need_ids = fields.One2many(comodel_name="school.needs", inverse_name="category_id", string="Needs", required=False, )
    no_of_needs = fields.Integer(string="No of. Needs", required=False, compute="_compute_needs_count")
    color = fields.Integer("Color Index")

    def _compute_needs_count(self):
        records_data = self.env['school.needs'].sudo().read_group([('category_id', 'in', self.ids)], ['category_id'],
                                                                  ['category_id'])
        result = dict((data['category_id'][0], data['category_id_count']) for data in records_data)
        for rec in self:
            rec.no_of_needs = result.get(rec.id, 0)

    def _compute_product_count(self):
        records_data = self.env['school.product'].sudo().read_group([('category_id', 'in', self.ids)], ['category_id'], ['category_id'])
        result = dict((data['category_id'][0], data['category_id_count']) for data in records_data)
        for rec in self:
            rec.no_of_products = result.get(rec.id, 0)


class SchoolProduct(models.Model):
    _name = 'school.product'
    _description = 'Products'
    _order = 'name'

    name = fields.Char(string="Product Name", required=False, default="New")
    category_id = fields.Many2one(comodel_name="school.product.category", string="Category", required=False, )
    code = fields.Char(string="Code", required=False, default="New")
    need_ids = fields.One2many(comodel_name="school.needs", inverse_name="product_id", string="Needs", required=False, )
    no_of_needs = fields.Integer(string="No of. Needs", required=False, compute="_compute_needs_count")

    def _compute_needs_count(self):
        records_data = self.env['school.needs'].sudo().read_group([('product_id', 'in', self.ids)], ['product_id'], ['product_id'])
        result = dict((data['product_id'][0], data['product_id_count']) for data in records_data)
        for rec in self:
            rec.no_of_needs = result.get(rec.id, 0)

    @api.model
    def create(self, vals):
        if vals.get('code', 'New') == 'New':
            seq_date = None
            vals['code'] = self.env['ir.sequence'].next_by_code('school.needs', sequence_date=seq_date) or '/'
        return super(SchoolProduct, self).create(vals)


class SchoolNeeds(models.Model):
    _name = 'school.needs'
    _description = 'School Needs'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name desc, date_implemented'

    name = fields.Char(string="Code", required=False, default='New')
    date_filed = fields.Date(string="Date Filed", required=False, default=fields.Date.context_today, )
    product_id = fields.Many2one(comodel_name="school.product", string="Product/Item", required=False, )
    category_id = fields.Many2one(comodel_name="school.product.category", string="Category", required=False,
                                  related="product_id.category_id", store=True)
    school_id = fields.Many2one(comodel_name="school.school", string="School", required=False, )
    quantity = fields.Float(string="Quantity",  required=False, )
    amount = fields.Float(string="Estimated Amount",  required=False, )
    amount_per_quantity = fields.Float(string="Amount per Quantity",  required=False, compute="compute_amount", store=True)
    no_of_beneficiary_student = fields.Integer(string="No. of Beneficiary Student",  required=False, )
    no_of_beneficiary_personnel = fields.Integer(string="No. of Beneficiary Personnel", required=False, )
    date_implemented = fields.Date(string="Date of Implementation", required=False, )
    responsible_id = fields.Many2one(comodel_name="res.users", string="Accountable Person", required=False,
                                     related="school_id.responsible_id", store=True)
    email = fields.Char(string="Email", required=False,
                        related="school_id.email", store=True)
    phone = fields.Char(string="Phone Number", required=False,
                        related="school_id.phone", store=True)
    state = fields.Selection(string="Status", selection=[('draft', 'Looking for Partners'),
                                                         ('ongoing', 'Ongoing Partnership'),
                                                         ('done', 'Completed')], required=False, default="draft")
    state_name = fields.Char(string="Status Name", required=False, default="Looking for Partners", compute="compute_actual_percentage", store=True)
    description = fields.Text(string="Description", required=False, )
    year_name = fields.Char(string="Year", required=False, compute="compute_year_name", store=True)
    no_of_stakeholder = fields.Integer(string="No. of Stakeholder(s) Inquiries", required=False,
                                       compute='_compute_stakeholder_count')
    stakeholder_ids = fields.One2many(comodel_name="stakeholder.project", inverse_name="need_id",
                                      string="Stakeholder Inquiries", required=False, )
    stakeholder_approved_ids = fields.One2many(comodel_name="stakeholder.project", inverse_name="need_id",
                                      string="Approved Stakeholder", required=False,
                                               domain=lambda self: [('state', 'in', ['approve', 'done'])])
    no_of_stakeholder_approved = fields.Integer(string="No. of Approved Stakeholder(s)", required=False,
                                                compute='_compute_stakeholder_approve_count')
    full_percentage = fields.Float(string="Full Percentage",  required=False, default=100.00)
    actual_percentage = fields.Float(string="Project Progress",  required=False, compute='compute_actual_percentage',
                                     store=True, digits=(12, 2))
    attachment_number = fields.Integer(compute='_get_attachment_number', string="Number of Attachments")
    attachment_ids = fields.One2many('ir.attachment', 'res_id', domain=[('res_model', '=', 'school.needs')],
                                     string='Attachments')

    def _get_attachment_number(self):
        read_group_res = self.env['ir.attachment'].read_group(
            [('res_model', '=', 'school.needs'), ('res_id', 'in', self.ids)],
            ['res_id'], ['res_id'])
        attach_data = dict((res['res_id'], res['res_id_count']) for res in read_group_res)
        for record in self:
            record.attachment_number = attach_data.get(record.id, 0)

    def action_get_attachment_tree_view(self):
        action = self.env['ir.actions.act_window']._for_xml_id('base.action_attachment')
        action['context'] = {'default_res_model': self._name, 'default_res_id': self.ids[0]}
        action['domain'] = str(['&', ('res_model', '=', self._name), ('res_id', 'in', self.ids)])
        action['search_view_id'] = (self.env.ref('snds.ir_attachment_view_search_inherit_school_needs').id, )
        return action

    def action_get_attachment_tree_readonly_view(self):
        action = self.env['ir.actions.act_window']._for_xml_id('base.action_attachment')
        action['context'] = {'default_res_model': self._name, 'default_res_id': self.ids[0]}
        action['domain'] = str(['&', ('res_model', '=', self._name), ('res_id', 'in', self.ids)])
        action['view_id'] = (self.env.ref('snds.view_attachment_tree_readonly').id, )
        action['search_view_id'] = (self.env.ref('snds.ir_attachment_view_search_inherit_school_needs').id, )
        return action

    @api.constrains('amount')
    def check_amount_needed(self):
        if self.amount == 0.00 or self.amount < 0.00:
            raise ValidationError(_("Please check the amount needed for the project."))

    @api.depends('stakeholder_approved_ids', 'amount', 'state')
    def compute_actual_percentage(self):
        for record in self:
            total_amount_donated = 0
            actual_percentage = 0
            state_name = record.state_name
            state = record.state
            if record.stakeholder_approved_ids and record.amount and record.state in ('ongoing', 'done'):
                for stakeholder in record.stakeholder_approved_ids:
                    total_amount_donated += stakeholder.amount_donated
                actual_percentage = round(total_amount_donated / record.amount, 2) * 100.00
                if total_amount_donated == record.amount:
                    state_name = "Completed"
                    state = "done"
                else:
                    state_name = "%s%s" % (str(round(actual_percentage, 2)), '% Completed')

            record.update({'actual_percentage': actual_percentage, 'state_name': state_name, 'state': state})

    def _compute_stakeholder_count(self):
        stakeholder_data = self.env['stakeholder.project'].sudo().read_group([('need_id', 'in', self.ids),
                                                                              ('state', '=', 'send')], ['need_id'], ['need_id'])
        result = dict((data['need_id'][0], data['need_id_count']) for data in stakeholder_data)
        for stakeholder in self:
            stakeholder.no_of_stakeholder = result.get(stakeholder.id, 0)

    def _compute_stakeholder_approve_count(self):
        stakeholder_data = self.env['stakeholder.project'].sudo().read_group([('need_id', 'in', self.ids),
                                                                              ('state', 'in', ['approve', 'done'])], ['need_id'], ['need_id'])
        result = dict((data['need_id'][0], data['need_id_count']) for data in stakeholder_data)
        for stakeholder in self:
            stakeholder.no_of_stakeholder_approved = result.get(stakeholder.id, 0)

    @api.depends('quantity', 'amount')
    def compute_amount(self):
        for record in self:
            if record.quantity or record.amount:
                amount_per_quantity = record.amount / record.quantity
                record.update({'amount_per_quantity': amount_per_quantity})

    @api.depends('date_implemented')
    def compute_year_name(self):
        if self.date_implemented:
            self.year_name = (self.date_implemented).strftime('%Y')

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            seq_date = None
            if 'date_implemented' in vals:
                seq_date = fields.Datetime.context_timestamp(self, fields.Datetime.to_datetime(vals['date_implemented']))
            vals['name'] = self.env['ir.sequence'].next_by_code('school.needs', sequence_date=seq_date) or '/'
        return super(SchoolNeeds, self).create(vals)
