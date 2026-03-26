# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://devintellecs.com>).
#
##############################################################################

from odoo import api, fields, models, _

class hr_employee(models.Model):
	_inherit = 'hr.employee'
	
	destination_location_id = fields.Many2one('stock.location', string='Destination Location')

class hr_department(models.Model):
	_inherit = 'hr.department'
	
	destination_location_id = fields.Many2one('stock.location', string='Destination Location')
	
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

