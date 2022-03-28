# -*- coding: utf-8 -*-
{
    'name': "Blautech",

    'summary': """ Blautech """,

    'description': """
        Customs para Blautech
    """,

    'author': "JS",
    'website': "",

    'category': 'Uncategorized',
    'version': '0.1',

    'depends': ['account','base'],

    'data': [
        'security/blautech_groups.xml',
        'views/menu_item_views.xml',
        'views/account_move_views.xml',
        'security/ir.model.access.csv',
        'views/blautech_presupuesto_wizard_view.xml',

    ],
}
