# -*- coding: utf-8 -*-

from openerp.osv import fields, osv
from openerp.tools.translate import _
from datetime import datetime, time, date, timedelta
from openerp import api
from openerp.osv.orm import BaseModel, Model, MAGIC_COLUMNS, except_orm

class call_center_partner(osv.osv):
    _inherit = 'res.partner'

    def _services_count(self, cr, uid, ids, field_name, arg, context=None):
        res = dict(map(lambda x: (x,0), ids))
        try:
            for partner in self.browse(cr, uid, ids, context):
                res[partner.id] = len(partner.services_ids) + len(partner.mapped('child_ids.services_ids'))
        except:
            pass
        return res


    _columns = {
        'is_call_center_partner': fields.boolean('Is Call Center Partner'),
        'civil_number': fields.char('Civil NO.'),
        'file_number': fields.char('File No.'),
        'services_count' :fields.function(_services_count, type="integer"),
        'services_ids': fields.one2many('call.center','partner_id','Services'),
        'marketer_id': fields.many2one('hr.employee','Marketer')
        }

    def unlink(self, cr, uid, ids, context=None):
        user = self.pool.get('res.users').has_group(cr, uid, 'tmas_call_center.group_user') 
        if user :
            manager = self.pool.get('res.users').has_group(cr, uid, 'tmas_call_center.group_manager') 
            if manager :
                return super(call_center_partner, self).unlink(cr, uid, ids, context=context)
            else :
                raise except_orm(_('Invalid Action'), _("You Don`t Have Permission To Delete Existing Customer"))
    
    def write(self, cr, uid, ids, vals, context=None):
        user = self.pool.get('res.users').has_group(cr, uid, 'tmas_call_center.group_user') 
        if user :
            manager = self.pool.get('res.users').has_group(cr, uid, 'tmas_call_center.group_manager') 
            if manager :
                return super(call_center_partner, self).write(cr, uid, ids, vals, context=context)
            else :
                raise except_orm(_('Invalid Action'), _("You Don`t Have Permission To Update Customer Information"))
        return super(call_center_partner, self).write(cr, uid, ids, vals, context=context)
        


    