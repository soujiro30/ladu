# -*- coding: utf-8 -*-
{
    'name': "LMS LADU",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Doc. Andrie Udal",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'website', 'website_slides', 'website_forum', 'mail'],

    # always loaded
    'data': [
        'security/school_management_security.xml',
        'security/ir.model.access.csv',
        'views/school_views.xml',
        'views/student_views.xml',
        'views/teacher_views.xml',
        'views/slide_channel_views.xml',
        'views/res_users_views.xml',
        'views/menuitem_views.xml',
    ],
}
