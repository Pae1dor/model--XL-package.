from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)

class ProjectProject(models.Model):
    _inherit = "project.project"

    sale_order_id = fields.Many2one(
        'sale.order',
        string="Sale Order",
        store=True
    )

    @api.model
    def create(self, vals):
        sale_order_id = vals.get('sale_order_id') or self.env.context.get('default_sale_order_id')
        project = super().create(vals)

        if sale_order_id and not project.sale_order_id:
            # _logger.info(f"[FIX] Forcing sale_order_id={sale_order_id} into project {project.id}")
            project.sale_order_id = sale_order_id

        # _logger.info(f"[DEBUG] Created project id={project.id} sale_order_id={project.sale_order_id}")
            # ถ้ามี Sale Order เชื่อมกับ Project นี้
        if project.sale_order_id and project.analytic_account_id:
            project_key = str(project.analytic_account_id.id)
            for line in project.sale_order_id.order_line:
                line.analytic_distribution = {project_key: 100}

        return project