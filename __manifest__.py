# -*- coding: utf-8 -*-
{
    'name': "Custom Formio Actions",

    'summary': "Custom actions for formio submissions",

    'description': "",

    'author': "jgs",
    'website': "https://www.jgsdev.de",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Tools',
    'version': '0.2',
    'license': 'LGPL-3',

    # any module necessary for this one to work correctly
    'depends': ['base', 'website', 'website_blog', 'formio'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/inherit_formioFormBuilder.xml',
        'views/model_Action.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False
}
