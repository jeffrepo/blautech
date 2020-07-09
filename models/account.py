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


class AccountMove(models.Model):
    _inherit = "account.move"

    proyecto_ids = fields.One2many('blautech.compra_proyecto_linea','move_id','C.C./PROYECTOS')
    id_blautech = fields.Char('Blautech id')
    # departamento = fields.Selection([ ('administrativo', 'Administrativo'),('operativo', 'Operativo'),('comercial', 'Comercial'),('otros', 'Otros')],'Departamento')

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
        activados = []
        if response_json['success'] and len(response_json['result']) > 0:
            for proyecto in response_json['result']:
                logging.warn(proyecto)
                if proyecto['status'] == 'ACTIVE':
                    if proyecto['_id'] not in proyecto_dic:
                        # logging.warn(float(proyecto['_id']))
                        proyecto_id = self.env['blautech.proyecto'].create({'name': proyecto['name'],'id_blautech': proyecto['_id'],'active':True})
                        # logging.warn(proyecto_id)
                        activados.append(proyecto['_id'])
                    else:
                        logging.warn('Ya existe')
                        proyecto_dic[proyecto['_id']].write({'name': proyecto['name']})
                        activados.append(proyecto['_id'])
                # else:
                #     if proyecto['_id'] in proyecto_dic:
                #         p = self.env['blautech.proyecto'].search([('id_blautech','=',proyecto['_id'])])
                #         if p:
                #             logging.warn('PASÓ A FALSO')
                #             p.write({'active': False})

            if len(activados) > 0:
                for p in proyecto_dic:
                    if p not in activados:
                        logging.warn('A ELIMINAR')
                        logging.warn(proyecto_dic[p])
                        proyecto_dic[p].write({'active':False})

    def post(self):
        res = super(AccountMove, self).post()
        for factura in self:
            if factura.type in ['in_receipt','in_invoice']:
                suma_porcentaje = 0
                lineas_proyectos = []
                if factura.proyecto_ids:
                    for linea_proyecto in factura.proyecto_ids:
                        suma_porcentaje += linea_proyecto.porcentaje
                        proy = {"_id": str(linea_proyecto.proyecto_id.id_blautech),"distributionType": "PERCENTAGE","distributionValue": str(linea_proyecto.porcentaje)}
                        lineas_proyectos.append(proy)
                else:
                    raise UserError(str('FAVOR DE INGRESAR POR LO MENOS UN PROYECTO O CENTRO DE COSTO'))

                if suma_porcentaje != 100:
                    raise UserError(str('EL PORCENTAJE DE PROYECTOS/CENTROS DE COSTOS NO PUEDE SER DIFERENTE DE 100%'))
                else:
                    logging.warn(factura.invoice_date)
                    logging.warn(factura.invoice_sequence_number_next)
                    logging.warn(factura.invoice_sequence_number_next_prefix)
                    logging.warn(factura.name)
                    factura_proveedor_body={"projectDistribution": lineas_proyectos,
                            "totalAmount": str(factura.amount_total),
                            "currency": str(factura.currency_id.name),
                            "vendor": str(factura.partner_id.name),
                            "purchaseOrder": str(factura.name),
                            "purchaseDate": str(factura.invoice_date),
                            "datail": {
                                "campo": "valor"
                            },
                            "createdBy": "Odoo"
                        }
                    url = "https://kykfm3bqpj.execute-api.us-east-1.amazonaws.com/dev/api/purchase"
                    headers = {
                        "x-api-key": "1qy0D4R4b39BOmRC8nOon5Umoa54aAJh5nmDuwSA",
                        'Content-type': 'application/json',
                        'Accept': 'text/plain'
                    }

                    auth = HTTPBasicAuth('x-api-key', '1qy0D4R4b39BOmRC8nOon5Umoa54aAJh5nmDuwSA')

                    response = requests.post(url, json = factura_proveedor_body, headers=headers,verify=False)
                    r = response.json()
                    logging.warn(response.json())
                    logging.warn(response)
                    if r['success']:
                        factura.id_blautech = r['result']['_id']
                        return res
                    else:
                        raise UserError(str(r['message']))

    def button_draft(self):
        res = super(AccountMove, self).button_draft()
        for factura in self:
            if factura.id_blautech:
                url = "https://kykfm3bqpj.execute-api.us-east-1.amazonaws.com/dev/api/purchase/" + str(factura.id_blautech)
                headers = {
                    "x-api-key": "1qy0D4R4b39BOmRC8nOon5Umoa54aAJh5nmDuwSA",
                    'Content-type': 'application/json',
                    'Accept': 'text/plain'
                }
                response = requests.delete(url,headers=headers)
                logging.warn(response)
                r = response.json()
                logging.warn(r)

                if r['success']:
                    factura.id_blautech = ""
                    return res
                else:
                    raise UserError("Compra no existente en ZOHO")
