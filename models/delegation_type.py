from odoo import fields, models, api


class DelegationType(models.Model):
    _name = 'delegation.type'
    _description = ''

    name = fields.Char(string='Delegation Name')
    users_ids = fields.Many2many('hr.employee', string='Users')
    groups_ids = fields.Many2many('res.groups', string='Groups')

    _sql_constraints = [
        ('unique_name', 'unique("name")', 'This name is exist')
    ]