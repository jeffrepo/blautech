# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.osv import expression
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.float_utils import float_compare
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tools.misc import formatLang, get_lang


class BlautechCompraProyectoLinea(models.Model):
    _name = "blautech.compra_proyecto_linea"
    _rec_name = "proyecto_id"

    move_id = fields.Many2one('account.move','Factura')
    proyecto_id = fields.Many2one('blautech.proyecto','Proyecto')
    porcentaje = fields.Float('%')


class BlautechProyecto(models.Model):
    _name = "blautech.proyecto"

    name = fields.Char('Nombre')
    id_blautech = fields.Char('Id blautech')
    active = fields.Boolean('Activo', default=True)
