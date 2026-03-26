# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle
#
##############################################################################

from odoo import api, fields, models, _


class reject_material_request_reason(models.TransientModel):
    _name = "reject.material.request.reason"
    _description = "Reject Material Request Reason"

    reason = fields.Text('Reason', required="1")

    def action_reject(self):
        model = self._context.get('active_model')
        active_id = self._context.get('active_id')
        model_id = self.env[model].browse(active_id)
        model_id.reject_reason = self.reason
        model_id.action_reject()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
