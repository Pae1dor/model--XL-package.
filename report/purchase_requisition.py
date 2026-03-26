# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle 
#
##############################################################################

from odoo import models, fields, api, _

class report_customer_loan(models.AbstractModel): 
    _name = 'report.dev_material_purchase_requisitions.report_mpr_template'
    _description = "Loan Report"

#    @api.multi
#    def get_footer_text(self,roote_number, cheque_num):
#        if roote_number and cheque_num:
#            return str(roote_number)+' '+ str(cheque_num)
            
            
    def get_state(self,obj):
        return _(dict(self.env['dev.material.request'].fields_get(allfields=['state'])['state']['selection'])[obj.state])
    
    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['dev.material.request'].browse(docids)
        return {
            'doc_ids': docs.ids,
            'doc_model': 'dev.material.request',
            'docs': docs,
            'get_state':self.get_state,
#            'get_footer_text':self.get_footer_text,
        }


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
