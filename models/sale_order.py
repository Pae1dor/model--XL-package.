from odoo import models, fields, api, _
from odoo.exceptions import UserError

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    project_id = fields.Many2one(
        'project.project',
        string="Related Project",
        ondelete='set null'
    )

    def action_create_project(self):
        self.ensure_one()
        if self.project_id:
            raise UserError(_("Project already created for this Sale Order."))
        project = self.env['project.project'].create({
            'name': f'Project for {self.name}',
            'sale_order_id': self.id,
        })
        self.project_id = project.id
        return {
            'type': 'ir.actions.act_window',
            'name': _('Project'),
            'res_model': 'project.project',
            'view_mode': 'form',
            'res_id': project.id,
            'target': 'current',
        }
