# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = 'account.move'


    l10n_latam_available_document_type_ids = fields.Many2many('l10n_latam.document.type')
    l10n_latam_use_documents = fields.Boolean("Use Documents", readonly=True)
    l10n_latam_document_type_id = fields.Many2one(
        "l10n_latam.document.type", "Document Type", ondelete="cascade"
    ) 
    l10n_do_fiscal_number = fields.Char(
        "Fiscal Number",
        index=True,
        tracking=True,
        copy=False,
        help="Stored field equivalent of l10n_latam_document number",
    )