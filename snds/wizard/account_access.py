from odoo import models, fields, api, _
from datetime import datetime, date
from odoo.exceptions import ValidationError, UserError


class AccountAccess(models.TransientModel):
    _name = 'account.access'
    _description = 'Access Portal'

    def create_user_access(self):
        records = self.env['accountable.person'].browse(self._context.get('active_ids'))
        for record in records:
            record.create_user_access()
