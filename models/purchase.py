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


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    proyecto_ids = fields.One2many('blautech.compra_proyecto_linea','purchase_id','Proyectos')

    def _get_proyectos(self):
        proyecto_ids = self.env['blautech.proyecto'].search([])
        proyecto_dic = {}
        if proyecto_ids:
            for proyecto in proyecto_ids:
                if proyecto.id_blautech:
                    proyecto_dic[proyecto.id_blautech] = proyecto
        return proyecto_dic

    @api.onchange('proyecto_ids')
    def _onchange_prooyecto_ids(self):
        url = "https://kykfm3bqpj.execute-api.us-east-1.amazonaws.com/dev/api/project/find/all?status=ACTIVE"
        headers = {
            "x-api-key": "1qy0D4R4b39BOmRC8nOon5Umoa54aAJh5nmDuwSA"
        }
        auth = HTTPBasicAuth('x-api-key', '1qy0D4R4b39BOmRC8nOon5Umoa54aAJh5nmDuwSA')

        response = requests.get(url, headers=headers)
        response_json = response.json()
        proyecto_dic = self._get_proyectos()
        if response_json['success'] and len(response_json['result']) > 0:
            for proyecto in response_json['result']:
                if proyecto['_id'] not in proyecto_dic:
                    # logging.warn(float(proyecto['_id']))
                    proyecto_id = self.env['blautech.proyecto'].create({'name': proyecto['name'],'id_blautech': proyecto['_id']})
                    # logging.warn(proyecto_id)
                else:
                    logging.warn('Ya existe')
                    proyecto_dic[proyecto['_id']].write({'name': proyecto['name']})
