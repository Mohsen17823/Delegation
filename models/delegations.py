from datetime import date
from typing import Any

from odoo import fields, models, api
from odoo.exceptions import ValidationError
from datetime import timedelta


class Delegations(models.Model):
    _name = 'delegations'
    _description = 'Delegations'

    delegation_type_id = fields.Many2one('delegation.type',required=True)
    delegation_from = fields.Many2one('hr.employee',
                                      readonly=True ,
                                      default=lambda self: self.env['hr.employee'].search([('user_id', '=', self.env.uid)]),
                                      limit=1,
                                      required=True
                                      )
    delegation_to = fields.Many2one('hr.employee',required=True)
    delegated_manager = fields.Many2one('hr.employee',required=True)
    delegation_date_from = fields.Datetime(default=fields.Datetime.now(),required=True)
    delegation_date_to = fields.Datetime(required=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('revoke', 'Revoke'),
    ], default='draft', readonly=True)
    default_groups = fields.Many2many('res.groups')


    # Revoke Flag used for assignments if it confirmed
    #      and return all assignments to its original if revoke
    def delegation_to_assignment(self,revoke_flag = False):
        for rec in self:
            if rec.delegation_to:
                employees = self.env['hr.employee'].search([
                    ('parent_id', '=', rec.delegation_from.id),
                    ('id','!=', rec.delegation_to.id)
                ])
                if not revoke_flag:
                    for emp in employees:
                        emp.delegated_manager = rec.delegation_to
                else:
                    for emp in employees:
                        emp.delegated_manager = False


    def delegated_manager_assignment(self,revoke_flag = False):
        for rec in self:
            if not rec.delegation_to or not rec.delegation_from:
                continue
            elif not revoke_flag:
                rec.delegation_to.delegated_manager = rec.delegated_manager
            else:
                rec.delegation_to.delegated_manager = False

    def groups_assign_method(self,revoke_flag = False):
        for rec in self:
            groups = rec.delegation_type_id.groups_ids
            user = rec.delegation_to.user_id   #short-cut
            if not revoke_flag:
                #save default_groups
                for gid in user.groups_id.ids:
                    rec.write({
                        'default_groups': [(4, gid)],
                    })
                user.write({
                    'groups_id': [(4, g.id) for g in groups]
                })
            else:
                def get_all_inherited_groups(group):
                    all_groups = {group.id}
                    if group.implied_ids:
                        for g_im in group.implied_ids:
                            all_groups |= get_all_inherited_groups(g_im)
                    return all_groups

                protected_groups = {
                    self.env.ref('base.group_user').id,
                    self.env.ref('base.group_portal').id,
                    self.env.ref('base.group_public').id,
                }

                for g in groups:
                    groups_ids_to_remove = list(get_all_inherited_groups(g))
                    safe_groups_ids_to_remove = [
                        gid for gid in groups_ids_to_remove
                        if gid not in protected_groups
                        and gid not in rec.default_groups.ids
                        and gid in user.groups_id.ids
                    ]
                    user.write({
                        'groups_id': [(3, gid) for gid in safe_groups_ids_to_remove]
                    })

                rec.write({
                    'default_groups': [(5, 0, 0)],
                })




    def confirm_method(self):
        for rec in self:
            rec.groups_assign_method()
            rec.delegation_to_assignment()
            rec.delegated_manager_assignment()
            rec.write({
                'state': 'confirmed',
            })

    def revoke_method(self):
        for rec in self:
            rec.groups_assign_method(True)
            rec.delegation_to_assignment(True)
            rec.delegated_manager_assignment(True)
            rec.write({
                'state': 'revoke',
            })

    #cron
    def check_delegation_date(self):
        delegation_ids = self.search([('state', 'in', ['draft', 'confirmed'])])
        for rec in delegation_ids:
            if rec.delegation_date_to:
                # Additional
                if rec.state == 'draft' and rec.delegation_date_from <= fields.Datetime.now():
                    rec.confirm_method()
                elif rec.state == 'confirmed' and rec.delegation_date_to < fields.Datetime.now():
                    rec.revoke_method()
