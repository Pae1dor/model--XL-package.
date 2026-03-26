# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://devintellecs.com>).
#
##############################################################################

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class material_request(models.Model):
	_name = 'dev.material.request'
	_inherit = ['mail.thread', 'mail.activity.mixin']
	_description = "Material Request"
	_order = 'name desc'
	
	def _get_default_employee(self):
	    employee_id = self.env['hr.employee'].search([('user_id','=',self.env.user.id)], limit=1)
	    return employee_id
	  
	
	def _get_default_department(self):
	    employee_id = self.env['hr.employee'].search([('user_id','=',self.env.user.id)], limit=1)
	    if employee_id and employee_id.department_id:
	        return employee_id.department_id
	    
	
	name = fields.Char('Name', copy=False)
	employee_id = fields.Many2one('hr.employee', string='Employee', tracking="1" , default=_get_default_employee)
	department_id = fields.Many2one('hr.department', string='Department', tracking="1", default=_get_default_department)
	department_manager_id = fields.Many2one('hr.employee', string='Department Manager',)
	date = fields.Date('Request Date', default=fields.Datetime.now, tracking="1")
	receive_date = fields.Date('Received Deadline')
	user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user.id)
	company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company.id)
	notes = fields.Text('Reason For Requisition')
	source_location_id = fields.Many2one('stock.location', string='Source Location')
	destination_location_id = fields.Many2one('stock.location', string='Destination Location')
	deliver_to = fields.Many2one('stock.picking.type', string='Deliver To')
	internal_picking_id = fields.Many2one('stock.picking.type', string='Internal Picking')
	state = fields.Selection([('draft','Draft'),('confirm','Confirm'),('department_approval','Department Approval'),('approved','Approved'),('received','Received'),('reject','Rejected'),('cancel','Cancel')], default='draft', tracking="1")
	confirm_by = fields.Many2one('res.users', string='Confirm By', copy=False)
	confirm_date = fields.Date('Confirm Date', copy=False)
	
	dep_approval_id = fields.Many2one('res.users', string='Department Approval', copy=False)
	dep_approval_date = fields.Date('Department Approval Date', copy=False)
	
	approved_by = fields.Many2one('res.users', string='Approved By', copy=False)
	approved_date = fields.Date('Approved Date', copy=False)
	
	reject_by = fields.Many2one('res.users', string='Reject By', copy=False)
	reject_date = fields.Date('Reject Date', copy=False)
	
	product_lines = fields.One2many('dev.material.request.line','request_id', string='Product Lines')
	reject_reason = fields.Text('Reject Reason')
	is_department_manager = fields.Boolean('Department Manager', compute='_set_department_manager')
	is_create_po = fields.Boolean('Create Purchase', copy=False)
	purchase_ids = fields.Many2many('purchase.order', string='Purchase', copy=False)
	purchase_count = fields.Integer('Purchase Count', compute='_get_purchase_count')
	internal_id = fields.Many2one('stock.picking', string='Internal Transfer', copy=False)
	picking_count = fields.Integer('Picking Count', compute='_get_picking_count')
	
	
	@api.depends('internal_id')
	def _get_picking_count(self):
	    for request in self:
	        if request.internal_id:
	            request.picking_count = 1
	        else:
	            request.picking_count = 0
	
	
	@api.depends('purchase_ids')
	def _get_purchase_count(self):
	    for request in self:
	        request.purchase_count = len(request.purchase_ids)
	
	def _set_department_manager(self):
	    for request in self:
	        request.is_department_manager = False
	        if request.department_id and request.department_id.manager_id:
	            if request.department_id.manager_id.user_id.id == self.env.user.id:
	                request.is_department_manager = True
	
	@api.onchange('department_id')
	def onchange_department_id(self):
	    if self.department_id:
	        self.department_manager_id = self.department_id.manager_id and self.department_id.manager_id.id or False
	        
	        
	@api.onchange('employee_id')
	def onchange_employee_id(self):
	    deliver_to = self.env['stock.picking.type'].search([('code','=','incoming'),('company_id','=',self.company_id.id)], limit=1)
	    internal = self.env['stock.picking.type'].search([('code','=','internal'),('company_id','=',self.company_id.id)], limit=1)
	    self.deliver_to = deliver_to and deliver_to.id or False
	    self.internal_picking_id = internal and internal.id or False
	    if self.employee_id:
	        self.department_id = self.employee_id.department_id and self.employee_id.department_id.id or False
	        self.department_manager_id = self.employee_id.department_id and self.employee_id.department_id.manager_id.id or False
	        self.source_location_id = self.department_id and self.department_id.destination_location_id.id or False
	        self.destination_location_id = self.employee_id.destination_location_id and self.employee_id.destination_location_id.id or False
	
	@api.model
	def create(self,vals):
	    vals['name'] = self.env['ir.sequence'].next_by_code('dev.material.request') or 'New'
	    return super(material_request, self).create(vals)
	    
	def unlink(self):
	    for request in self:
	        if request.state not in ['draft','cancel']:
	            raise ValidationError(_('You can delete in draft or cancel state.'))
	    return super(material_request, self).unlink()
	
	def action_confirm(self):
	    self.write({
	        'state':'confirm',
	        'confirm_by':self.env.user.id,
	        'confirm_date':fields.datetime.now()
	    })
	
	def action_draft(self):
	    self.state = 'draft'
	
	def action_department_approval(self):
	    if not self.product_lines:
	        raise ValidationError(_('Please Add Product Lines.'))
	    for line in self.product_lines:
	        if not line.action:
	            raise ValidationError(_('Please assign requisition action in product lines'))
	            
	    self.write({
	        'state':'department_approval',
	        'dep_approval_id':self.env.user.id,
	        'dep_approval_date':fields.datetime.now()
	    })
	
	def action_approved(self):
	    self.write({
	        'state':'approved',
	        'approved_by':self.env.user.id,
	        'approved_date':fields.datetime.now()
	    })
	
	def action_reject(self):
	    self.write({
	        'state':'reject',
	        'reject_by':self.env.user.id,
	        'reject_date':fields.datetime.now()
	    })
	
	
	def get_vendors(self):
	    partner_ids = []
	    for line in self.product_lines:
	        if line.action == 'purchase':
	            if line.vendor_id.id not in partner_ids:
	                partner_ids.append(line.vendor_id.id)
	    if partner_ids:
	        partner_ids = self.env['res.partner'].browse(partner_ids)
	    return partner_ids
	
	def create_purchase_order(self):
	    partner_ids = self.get_vendors()
	    if not partner_ids:
	        return True
	    
	    po_pool = self.env['purchase.order'].sudo()
	    line_pool = self.env['purchase.order.line'].sudo()
	    po_ids = []
	    for partner in partner_ids:
	        purchase_id = po_pool.create({
	            'partner_id':partner.id or False,
	            'state':'draft',
	            'company_id':self.company_id.id or False,
	        })
	        purchase_id.onchange_partner_id()
	        for line in self.product_lines:
	            if line.vendor_id.id == partner.id and line.action == 'purchase':
	                line_id = line_pool.create({
	                    'product_id':line.product_id and line.product_id.id or False,
	                    'name':line.name,
						'analytic_distribution':line.analytic_distribution,
	                    'price_unit': line.product_id.lst_price,
                        'product_qty': line.quantity or 1,
                        'product_uom': line.uom_id and line.uom_id.id or False,
                        'order_id':purchase_id.id
	                })
	                qty = line_id.product_qty
	                uom = line_id.product_uom.id
	                line_id.onchange_product_id()
	                line_id.write({
	                    'product_uom':uom,
	                    'product_qty':qty,
	                })
	        po_ids.append(purchase_id.id)
	    if po_ids:
	        self.purchase_ids = [(6,0, po_ids)]
	
	def create_internal_transfer(self):
	    picking_pool = self.env['stock.picking'].sudo()
	    move_pool = self.env['stock.move'].sudo()
	    internal_id = picking_pool.create({
	        'picking_type_id':self.internal_picking_id.id or False,
	        'location_id':self.source_location_id.id or False,
	        'location_dest_id':self.destination_location_id.id or False,
	        'move_type':'direct',
	        'user_id':self.env.user.id,
	        'company_id':self.company_id.id or False,
	    })
	    for line in self.product_lines:
	        if line.action == 'internal':
	            move_pool.create({
	                'product_id':line.product_id.id,
	                'name':line.name,
	                'location_id':self.source_location_id.id or False,
	                'location_dest_id':self.destination_location_id.id or False,
	                'product_uom_qty':line.quantity,
	                'quantity_done':line.quantity,
	                'product_uom':line.product_id.uom_id.id or False,
	                'picking_id':internal_id and internal_id.id or False
	            })
	    self.internal_id = internal_id.id
	
	def check_is_internal(self):
	    for line in self.product_lines:
	        if line.action == 'internal':
	            return True
	    return False
	
	def check_is_purchase(self):
	    for line in self.product_lines:
	        if line.action == 'purchase':
	            return True
	    return False
	
	def action_create_purchase(self):
	    self.is_create_po = True
	    if self.check_is_purchase():
	        self.create_purchase_order()
	    if self.check_is_internal():
	        self.create_internal_transfer()
	
	def action_receive(self):
	    self.state = 'received'
	
	def view_purchase_orders(self):
	    action = self.env["ir.actions.actions"]._for_xml_id("purchase.purchase_rfq")
	    if len(self.purchase_ids) > 1:
	        action['domain'] = [('id', 'in', self.purchase_ids.ids)]
	    elif len(self.purchase_ids) == 1:
	        form_view = [(self.env.ref('purchase.purchase_order_form').id, 'form')]
	        if 'views' in action:
	            action['views'] = form_view + [(state,view) for state,view in action['views'] if view != 'form']
	        else:
	            action['views'] = form_view
	        action['res_id'] = self.purchase_ids.id
	    else:
	        action = {'type': 'ir.actions.act_window_close'}
	    return action
	
	def view_internal_picking(self):
	    action = self.env["ir.actions.actions"]._for_xml_id("stock.action_picking_tree_all")
	    if self.internal_id:
	        form_view = [(self.env.ref('stock.view_picking_form').id, 'form')]
	        if 'views' in action:
	            action['views'] = form_view + [(state,view) for state,view in action['views'] if view != 'form']
	        else:
	            action['views'] = form_view
	        action['res_id'] = self.internal_id.id
	    else:
	        action = {'type': 'ir.actions.act_window_close'}
	    return action
	

class dev_material_line(models.Model):
	_name = 'dev.material.request.line'
	_description = "Material Request Lines"
	
	
	action = fields.Selection([('internal','Internal Transfer'),('purchase','Purchase')], string='Requisition Action')
	product_id = fields.Many2one('product.product', string='Product')
	name = fields.Text('Description')
	quantity = fields.Float(string='Quantity', default=1)
	uom_id = fields.Many2one('uom.uom')
	vendor_id = fields.Many2one('res.partner', string='Vendor')
	request_id = fields.Many2one('dev.material.request', string='Request')
	analytic_distribution = fields.Json(string="Analytic Distribution")
	analytic_precision = fields.Integer(
		string="Analytic Precision",
		default=lambda self: self.env.company.currency_id.decimal_places
	)
	
	@api.onchange('product_id')
	def _onchage_product(self):
	    if self.product_id:
	        self.name = self.product_id.display_name or ''
	        self.uom_id = self.product_id.uom_id and self.product_id.uom_id.id or False
	
	        
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

