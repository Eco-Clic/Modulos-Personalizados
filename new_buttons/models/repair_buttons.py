from odoo import models, api

class ResPartner(models.Model):
    _inherit = 'res.partner'

    def action_open_repairs(self):
        return {
            'name': 'Reparaciones',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'repair.order',
            'domain': [('partner_id', '=', self.id)],
            'context': dict(self.env.context, default_partner_id=self.id),
            'target': 'current',
        }
