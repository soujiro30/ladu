# -*- coding: utf-8 -*-
{
    'name': "Go Get Funded",

    'summary': """
        Helping Schools and Finding Partners for Greater Sustainability""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Niel John Balogo",
    'website': "http://gogetfunded.net",
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'mail', 'website'],

    # always loaded
    'data': [
        'security/snds_security.xml',
        'security/ir.model.access.csv',
        'data/init_data.xml',
        'data/ir_sequence_data.xml',
        'wizard/account_access_views.xml',
        'views/mail_views.xml',
        'views/localization_views.xml',
        'views/school_views.xml',
        'views/necessity_views.xml',
        'views/stakeholder_views.xml',
        'views/menu_views.xml',
        'data/res_region_data.xml',
        'data/school_position_data.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
