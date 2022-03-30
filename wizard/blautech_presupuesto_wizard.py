# -*- coding: utf-8 -*-

from odoo import models, fields, api
from collections import defaultdict
import logging
import xlsxwriter
import io
import base64
import dateutil.parser
import datetime
from datetime import date, timezone
import dateutil.parser
import pytz

class PresupuestoWizard(models.TransientModel):
    _name = 'blautech.reporte_presupuesto.wizard'
    _description = "Wizard creado para reporte de presupuestos"

    fecha_inicio = fields.Date('Fecha inicio')
    fecha_final = fields.Date('Fecha final')
    linea_ids = fields.One2many('blautech.reporte_presupuesto.lineas', 'presupuesto_id', 'lineas')
    archivo = fields.Binary('Archivo')
    name = fields.Char('File Name', size=32)

    def generando_excel (self):
        for w in self:
            f = io.BytesIO()
            libro = xlsxwriter.Workbook(f)
            formato_fecha = libro.add_format({'num_format': 'dd/mm/yy'})
            hoja = libro.add_worksheet('Reporte')

            #Tamaño de la fila
            hoja.set_row(1, 25)

            #Tamaño de la columna
            hoja.set_column('A:A',25)
            hoja.set_column('B:C',20)
            hoja.set_column('D:E',15)

            timezone = pytz.timezone(self._context.get('tz') or self.env.user.tz or 'UTC')

            formato_titulo = libro.add_format({'size': 18, 'color':'#ffffff', 'align':'center', 'fg_color':'#a0a2a3'})
            formato_subtitulo = libro.add_format({'size': 11, 'color':'#ffffff', 'align':'center', 'fg_color':'#697880'})

            hoja.merge_range('A2:E2', 'Reporte de presupuestos', formato_titulo)

            hoja.write(4,0, 'Posición presupuestaria', formato_subtitulo)
            hoja.write(4,1, 'Fecha inicio', formato_subtitulo)
            hoja.write(4,2, 'Fecha final', formato_subtitulo)
            hoja.write(4,3, 'Importe previsto', formato_subtitulo)
            hoja.write(4,4, 'Importe real', formato_subtitulo)

            dicc_analisis_presupuestario = {}

            for linea in w.linea_ids:
                analisis_presupuestos = self.env['crossovered.budget.lines'].sudo().search([('company_id', '=', linea.compania.id)])
                calculo = 0
                calculo_importe_real = 0
                for presupuesto in analisis_presupuestos:
                    mes_pos_presupuestaria = str(presupuesto.date_from.month)+'-'+ presupuesto.general_budget_id.name
                    fecha_inicio = presupuesto.date_from.strftime('%d/%m/%Y')
                    fecha_final = presupuesto.date_to.strftime('%d/%m/%Y')

                    if presupuesto.date_from >= w.fecha_inicio and presupuesto.date_to <= w.fecha_final:
                        if presupuesto.general_budget_id:
                            if mes_pos_presupuestaria not in dicc_analisis_presupuestario:
                                dicc_analisis_presupuestario[mes_pos_presupuestaria]={
                                'fecha_inicio':fecha_inicio,
                                'fecha_final':fecha_final,
                                'posicion_presupuestaria':presupuesto.general_budget_id.name,
                                'importe_previsto': 0.0,
                                'importe_real':0.0,
                                }

                            if mes_pos_presupuestaria in dicc_analisis_presupuestario and presupuesto.planned_amount:
                                if presupuesto.planned_amount != 0:
                                    logging.warning(fecha_inicio+'----'+presupuesto.general_budget_id.name+':    '+str(presupuesto.planned_amount) + ' / '+ str(linea.tipo_cambio))
                                    calculo = round(presupuesto.planned_amount / linea.tipo_cambio, 2)
                                dicc_analisis_presupuestario[mes_pos_presupuestaria]['importe_previsto'] += calculo
                                if presupuesto.practical_amount != 0:
                                    calculo_importe_real = round(presupuesto.practical_amount/ linea.tipo_cambio,2)
                                dicc_analisis_presupuestario[mes_pos_presupuestaria]['importe_real'] += calculo_importe_real
                logging.warning('')
                logging.warning('')

            fila = 5
            estilo_fecha = libro.add_format({'align':'center'})
            for elemento1 in dicc_analisis_presupuestario:
                hoja.write(fila,0, dicc_analisis_presupuestario[elemento1]['posicion_presupuestaria'])
                hoja.write(fila,1, dicc_analisis_presupuestario[elemento1]['fecha_inicio'], estilo_fecha)
                hoja.write(fila,2, dicc_analisis_presupuestario[elemento1]['fecha_final'], estilo_fecha)
                hoja.write(fila,3, dicc_analisis_presupuestario[elemento1]['importe_previsto'])
                hoja.write(fila,4, dicc_analisis_presupuestario[elemento1]['importe_real'])
                fila+=1


            logging.warning('diccionario')
            logging.warning(dicc_analisis_presupuestario)
            libro.close()
            datos = base64.b64encode(f.getvalue())
            self.write({'archivo': datos, 'name':'reporte_presupuesto.xls'})

        return {
                'context': self.env.context,
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'blautech.reporte_presupuesto.wizard',
                'res_id': self.id,
                'view_id': False,
                'type': 'ir.actions.act_window',
                'target': 'new',
            }

    def print_report(self):
        datas = {'ids': self.env.context.get('active_ids', [])}
        res = self.read(['fecha_inicio','fecha_final'])
        res = res and res[0] or {}
        datas['form'] = res
        # datas['form'] = False
        return self.env.ref('blautech.reporte_presupuesto.wizard').report_action([], data=datas)

class PresupuestoLineas(models.TransientModel):
    _name = 'blautech.reporte_presupuesto.lineas'
    _description='lineas del wizard'

    presupuesto_id = fields.Many2one('blautech.reporte_presupuesto.wizard', string="presupuesto")
    compania = fields.Many2one('res.company', string='Compañia')
    tipo_cambio = fields.Float('Tipo de cambio')
