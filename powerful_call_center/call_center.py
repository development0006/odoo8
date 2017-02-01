# -*- coding: utf-8 -*-

from openerp.osv import fields, osv
from openerp import api, models
from openerp.tools.translate import _
from datetime import date, timedelta
import datetime, time
import smtplib
from dateutil import relativedelta
from openerp.osv.orm import BaseModel, Model, MAGIC_COLUMNS, except_orm

class call_center(osv.osv):
    _name = 'call.center'
    _inherit = ['mail.thread']
    _rec_name = 'number'

    def _calls(self, cr, uid, ids, field_name, arg, context=None):
        calls = self.pool['call.center.line']
        return {
            call_center_id: calls.search_count(cr,uid, [('call_center_id', '=', call_center_id)], context=context)
            for call_center_id in ids
        }

    _columns = {
        'number': fields.char('Services Number', required=True,readonly=True, select=True, copy=False),
        'partner_id': fields.many2one('res.partner', 'Customer'),
        'civil_number': fields.char('Civil NO.',readonly=True),
        'file_number': fields.char('File No.',readonly=True),
        'mobile': fields.char('Mobile',readonly=True),
        'phone': fields.char('Phone',readonly=True),
        'marketer_id': fields.many2one('hr.employee','Marketer',readonly=True),
        'created_date': fields.datetime('Created Date',readonly=True),
        'closed_date': fields.datetime('Closed Date',readonly=True),
        'created_by_id': fields.many2one('res.users', 'Created By',readonly=True),
        'closed_by_id': fields.many2one('res.users', 'Closed By',readonly=True),
        'call_type_id': fields.many2one('call.type', 'Call Type', required=True),
        'call_category_id': fields.many2one('call.category', 'Call Category', required=True),
        'assignto_id': fields.many2one('hr.employee', 'Assigned to'),
        'participant_type_id': fields.many2one('participant.type', 'Participant Type'),
        'calls_count' :fields.function(_calls, type="integer"),
        'call_center_line_ids': fields.one2many('call.center.line','call_center_id','Calls'),
        'due_date': fields.datetime('Due date',readonly=True),
        'contact_number': fields.char('Contact No.', required=True),
        'action': fields.char('Action', required=True),
        'support_action': fields.char('Support Action'),
        'description': fields.text('Description'),
        'Comment': fields.text('Comment'),
        'send_mail': fields.boolean('Send Mail'),
        'state': fields.selection([('open','Open'),('under_investigation','Under Investigation'),('pending','Pending'),('resolved','Resolved'),('closed','Closed')], 'Status')
        }

    _defaults = {
        'number': lambda obj, cr, uid, context: '/',
        'created_date': fields.datetime.now,
        'state': 'open',
        'created_by_id':lambda self, cr, uid, ctx=None: uid
   }

    @api.multi
    def action_service_sent(self):
        assert len(self) == 1, 'This option should only be used for a single id at a time.'
        template = self.env.ref('tmas_call_center.email_template_edi_service', False)
        compose_form = self.env.ref('mail.email_compose_message_wizard_form', False)
        ctx = dict(
            default_model='call.center',
            default_res_id=self.id,
            default_use_template=bool(template),
            default_template_id=template.id,
            default_composition_mode='comment',
            mark_invoice_as_sent=True,
        )
        return {
            'name': _('Send Email'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form.id, 'form')],
            'view_id': compose_form.id,
            'target': 'new',
            'context': ctx,
        }

    def service_check_state(self, cr, uid, context=None):
        services_obj = self.pool.get('call.center')
        services_ids = services_obj.search(cr, uid, [('state','in',('open','under_investigation'))])
        for service_id in services_ids:
            service = services_obj.browse(cr, uid,service_id ,context=context) 
            date_two = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            if date_two > service.due_date:
                services_obj.write(cr, uid, service_id, {'state': 'pending'}, context=context)
            
    def onchange_partner_id(self, cr, uid, ids, partner_id, context=None):
        res_partner_pool = self.pool.get('res.partner')
        partner = res_partner_pool.browse(cr, uid, partner_id, context=context)
        
        return {
            'value': {
                'civil_number': partner.civil_number,
                'phone': partner.phone,
                'mobile': partner.mobile,
                'file_number': partner.file_number,
                'marketer_id': partner.marketer_id.id,
            }
        }

    def onchange_call_category_id(self, cr, uid, ids, call_category_id, context=None):
        if call_category_id :
            call_category_pool = self.pool.get('call.category')
            call_category = call_category_pool.browse(cr, uid, call_category_id, context=context)
        
            peroid = call_category.due_date_period
            current_date = datetime.datetime.now()
            due_date = current_date + timedelta(hours=int(peroid))
            return {
                'value': {
                   'due_date': due_date,
               }
            }
        else:
            return True

    def onchange_assign_to_id(self, cr, uid, ids, assignto_id, context=None):
        if assignto_id :
            return {
                'value': {
                   'send_mail': True,
               }
            }
        else:
            return {
                'value': {
                   'send_mail': False,
               }
            }
            
    def set_to_under_nvestigation(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state':'under_investigation'}) 

    def set_to_resolve(self, cr, uid, ids, context=None):
        if not self.browse(cr, uid, ids, context=context).support_action:
            raise osv.except_osv(_('Warning!'),_('You Have To Fill Support Action Field'))
        closed_date = datetime.datetime.now()
        return self.write(cr, uid, ids, {'state':'resolved','closed_date':closed_date,'closed_by_id':uid}) 

    def set_to_close(self, cr, uid, ids, context=None):
        closed_date = datetime.datetime.now()
        return self.write(cr, uid, ids, {'state':'closed','closed_date':closed_date,'closed_by_id':uid})

    def send_email(self, cr, uid, ids, context=None):
        sender = 'ahmedqudah1988@gmail.com'
        receivers = 'mahmouddaher09@gmail.com'
        
        message = """test
        """
        
        
        smtpObj = smtplib.SMTP(host='smtp.gmail.com', port=587)
        smtpObj.ehlo()
        smtpObj.starttls()
        smtpObj.ehlo()
        smtpObj.login(user="ahmedqudah1988@gmail.com", password="ahmed1988")
        smtpObj.sendmail(sender, receivers, message)         
        print "Successfully sent email"
        raise osv.except_osv(_('alert!'),_('Successfully sent email'))
        return True
        
    def unlink(self, cr, uid, ids, context=None):
        user = self.pool.get('res.users').has_group(cr, uid, 'tmas_call_center.group_user') 
        if user :
            manager = self.pool.get('res.users').has_group(cr, uid, 'tmas_call_center.group_manager') 
            if manager :
                return super(call_center, self).unlink(cr, uid, ids, context=context)
            else :
                raise except_orm(_('Invalid Action'), _("You Don`t Have Permission To Delete Existing Services"))        

    def write(self, cr, uid, ids, vals, context=None):
        user = self.pool.get('res.users').has_group(cr, uid, 'tmas_call_center.group_user') 
        if user :
            manager = self.pool.get('res.users').has_group(cr, uid, 'tmas_call_center.group_manager') 
            if manager :
                if 'partner_id' in vals:
                    val = self.onchange_partner_id(cr, uid, ids, vals['partner_id'], context)
                    vals.update(val['value']) 
                if 'call_category_id' in vals:
                    val = self.onchange_call_category_id(cr, uid, ids, vals['call_category_id'], context)
                    vals.update(val['value']) 
                return super(call_center, self).write(cr, uid, ids, vals, context=context)
            else :
                if 'Comment' in vals or 'support_action' in vals or 'state' in vals:
                    if 'partner_id' in vals:
                        val = self.onchange_partner_id(cr, uid, ids, vals['partner_id'], context)
                        vals.update(val['value']) 
                    if 'call_category_id' in vals:
                        val = self.onchange_call_category_id(cr, uid, ids, vals['call_category_id'], context)
                        vals.update(val['value']) 
                    return super(call_center, self).write(cr, uid, ids, vals, context=context)
                else : 
                    raise except_orm(_('Invalid Action'), _("You Don`t Have Permission To Update Existing Services"))        

    def create(self, cr, uid, vals, context=None):
        if context is None:
            context = {}
        if vals.get('number','/')=='/':
            vals['number'] = self.pool.get('ir.sequence').get(cr, uid, 'call.center') or '/'
        
        if vals.get('partner_id'):
            val = self.onchange_partner_id(cr, uid, [],vals['partner_id'], context)
            vals.update(val['value']) 
        if vals.get('call_category_id'):
            val = self.onchange_call_category_id(cr, uid, [], vals['call_category_id'], context)
            vals.update(val['value']) 

        return super(call_center, self).create(cr, uid, vals, context=context)

class call_type(osv.osv):
    _name = 'call.type'
    _columns = {
        'name': fields.char('Name',required=True),
        }

class call_category(osv.osv):
    _name = 'call.category'
    _columns = {
        'name': fields.char('Name',required=True),
        'due_date_period': fields.char('Due Date Period'),
        }

class participant_type(osv.osv):
    _name = 'participant.type'
    _columns = {
        'name': fields.char('Name',required=True),
        }

class call_center_line(osv.osv):
    _name = 'call.center.line'
    _columns = {
        'call_center_id': fields.many2one('call.center', 'Call Center'),
        'created_date': fields.datetime('Created Date',readonly=True),
        'created_by_id': fields.many2one('res.users', 'Created By',readonly=True),
        'description': fields.text('Description', required=True),
        'type': fields.selection([('in','In'),('out','Out')], 'Call Type', required=True),
        }

    _defaults = {
        'created_date': fields.datetime.now,
        'created_by_id':lambda self, cr, uid, ctx=None: uid
   }

    def unlink(self, cr, uid, ids, context=None):
        user = self.pool.get('res.users').has_group(cr, uid, 'tmas_call_center.group_user') 
        if user :
            manager = self.pool.get('res.users').has_group(cr, uid, 'tmas_call_center.group_manager') 
            if manager :
                return super(call_center_line, self).unlink(cr, uid, ids, context=context)
            else :
                raise except_orm(_('Invalid Action'), _("You Don`t Have Permission To Delete This Record"))
    
    def write(self, cr, uid, ids, vals, context=None):
        user = self.pool.get('res.users').has_group(cr, uid, 'tmas_call_center.group_user') 
        if user :
            manager = self.pool.get('res.users').has_group(cr, uid, 'tmas_call_center.group_manager') 
            if manager :
                return super(call_center_line, self).write(cr, uid, ids, vals, context=context)
            else :
                raise except_orm(_('Invalid Action'), _("You Don`t Have Permission To Update This Record"))


class call_center_activity(osv.osv):
    _name = 'call.center.activity'
    _columns = {
        'name': fields.char('Name'),
        'phone': fields.char('Phone', required=True),
        'created_date': fields.datetime('Created Date',readonly=True),
        'created_by_id': fields.many2one('res.users', 'Created By',readonly=True),
        'description': fields.text('Description'),
        }

    _defaults = {
        'created_date': fields.datetime.now,
        'created_by_id':lambda self, cr, uid, ctx=None: uid
   }

    def unlink(self, cr, uid, ids, context=None):
        user = self.pool.get('res.users').has_group(cr, uid, 'tmas_call_center.group_user') 
        if user :
            manager = self.pool.get('res.users').has_group(cr, uid, 'tmas_call_center.group_manager') 
            if manager :
                return super(call_center_activity, self).unlink(cr, uid, ids, context=context)
            else :
                raise except_orm(_('Invalid Action'), _("You Don`t Have Permission To Delete This Record"))
    
    def write(self, cr, uid, ids, vals, context=None):
        user = self.pool.get('res.users').has_group(cr, uid, 'tmas_call_center.group_user') 
        if user :
            manager = self.pool.get('res.users').has_group(cr, uid, 'tmas_call_center.group_manager') 
            if manager :
                return super(call_center_activity, self).write(cr, uid, ids, vals, context=context)
            else :
                raise except_orm(_('Invalid Action'), _("You Don`t Have Permission To Update This Record"))

class mail_compose_message(models.Model):
    _inherit = 'mail.compose.message'

    @api.multi
    def send_mail(self):
        context = self._context
        if context.get('default_model') == 'call.center' and \
                context.get('default_res_id') and context.get('mark_invoice_as_sent'):
            service = self.env['call.center'].browse(context['default_res_id'])
            service = service.with_context(mail_post_autofollow=True)
        return super(mail_compose_message, self).send_mail()

class FooterlessNotification(models.Model):
    _inherit = 'mail.notification'

    def get_signature_footer(self, cr, uid, user_id, res_model=None, res_id=None, context=None, user_signature=True):
        return ""

""" 
solve problem :
    This function used to delete footer from email send by System  " Sent by Your Company using KanzERP ,"
"""
class mail_mail(osv.Model):
    """ Update of mail_mail class, to add the signin URL to notifications. """
    _inherit = 'mail.mail'

    def _get_partner_access_link(self, cr, uid, mail, partner=None, context=None):
        return ""
"""
    This Function To Remove link with Email "access directly to call.center # 00009" 
    Or Go to settings -> general settings and uncheck 'Activate the customer portal'.

"""