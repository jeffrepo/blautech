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
import logging
from requests.auth import HTTPBasicAuth
import requests
import json


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    proyecto_ids = fields.One2many('blautech.compra_proyecto_linea','sale_id','C.C./PROYECTOS')
    id_blautech = fields.Char('Blautech id')


    def _get_proyectos(self):
        proyecto_ids = self.env['blautech.proyecto'].search([])
        proyecto_dic = {}
        if proyecto_ids:
            for proyecto in proyecto_ids:
                if proyecto.id_blautech:
                    proyecto_dic[proyecto.id_blautech] = proyecto
        return proyecto_dic
