# -*- coding: utf-8 -*-
{
    'name': 'Powerful Call Center',
    'version': '0.1',
    'category': 'Sales',
    'author': 'Digital',
    'description':"""
    Now You can manage all Call Center operation
    with most efficiency at Powerful Call Center .
    """,  
    'depends': ['sale','hr'],
    'data': ['security/call_center_security.xml',
             'security/ir.model.access.csv',
             'edi/services_action_data.xml',
             'data/scheduler_data.xml',
             'call_center_module_sequence.xml',
             'call_center_partner_view.xml',
             'call_center_view.xml'],
    'price' : '150',
    'currency' : 'EUR',
    'images' : ['images/main_screenshot.png'],
    'icon' : 'static/description/icon.png',
    'application' : True, 
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: