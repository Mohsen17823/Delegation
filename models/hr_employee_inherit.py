from odoo import fields, models, api


class HrEmployeeInherit(models.Model):
    _inherit = 'hr.employee'

    delegated_manager = fields.Many2one('hr.employee')
