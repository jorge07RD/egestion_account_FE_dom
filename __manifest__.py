# -*- coding: utf-8 -*-
{
    'name': 'Egestion_account_FE_dom',
    'version': '',
    'summary': """ Egestion_account_FE_dom Summary """,
    'author': '',
    'website': '',
    'category': '',
    'depends': ['base','account'],
    "data": [
        "wizard/FE_credito_fiscal.xml",
        "security/ir.model.access.csv",
        "views/account_inherit.xml",
    ],
    'application': True,
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
