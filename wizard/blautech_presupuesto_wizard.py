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
            # hoja.set_row(1, 25)

            #Tamaño de la columna
            hoja.set_column('A:A',30)
            hoja.set_column('B:N',20)
            # hoja.set_column('D:E',15)

            timezone = pytz.timezone(self._context.get('tz') or self.env.user.tz or 'UTC')

            formato_titulo = libro.add_format({'size': 11, 'color':'#ffffff', 'align':'center', 'fg_color':'#21618C'})
            formato_totales = libro.add_format({'size': 11, 'color':'#ffffff', 'align':'right', 'fg_color':'#2E86C1'})

            # hoja.merge_range('A2:E2', 'Reporte de presupuestos', formato_titulo)

            # hoja.write(4,0, 'Posición presupuestaria', formato_subtitulo)
            # hoja.write(4,1, 'Fecha inicio', formato_subtitulo)
            # hoja.write(4,2, 'Fecha final', formato_subtitulo)
            # hoja.write(4,3, 'Importe previsto', formato_subtitulo)
            # hoja.write(4,4, 'Importe real', formato_subtitulo)

            hoja.write(0,0, 'SOLUCIONES BLAUTECH', formato_titulo)
            anio_final = w.fecha_final.strftime('%Y')
            hoja.write(1,0, 'PRESUPUESTOS GENERAL '+anio_final, formato_titulo)
            hoja.write(2,0, 'Cantidad expresada en '+anio_final, formato_titulo)
            columna = 1
            lista_meses = ['UNKNOW', 'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
            for i in lista_meses:
                hoja.write(3, columna, 'Cantidad planificada ', formato_titulo)
                if i != 'UNKNOW':
                    hoja.write(4, columna, i+' '+anio_final, formato_titulo)
                    columna += 1
            hoja.write(3, columna, 'Proyección', formato_titulo)
            hoja.write(4, columna, 'Total', formato_titulo)

            dicc_analisis_presupuestario = {}

            for linea in w.linea_ids:
                analisis_presupuestos = self.env['crossovered.budget.lines'].sudo().search([('company_id', '=', linea.compania.id)])
                for presupuesto in analisis_presupuestos:
                    if presupuesto.date_from >= w.fecha_inicio and presupuesto.date_to <= w.fecha_final:
                        if presupuesto.general_budget_id:
                            if presupuesto.general_budget_id.id not in dicc_analisis_presupuestario:
                                dicc_analisis_presupuestario[presupuesto.general_budget_id.id]={
                                'posicion_presupuestaria':presupuesto.general_budget_id.name,
                                'Enero':0,
                                'Febrero':0,
                                'Marzo':0,
                                'Abril':0,
                                'Mayo':0,
                                'Junio':0,
                                'Julio':0,
                                'Agosto':0,
                                'Septiembre':0,
                                'Octubre':0,
                                'Noviembre':0,
                                'Diciembre':0,
                                'total': 0.0,
                                }
                        if presupuesto.general_budget_id.id in dicc_analisis_presupuestario:
                            if presupuesto.date_from.strftime('%m') == presupuesto.date_to.strftime('%m'):
                                # logging.warning('Que fecha tiene esto?')
                                # logging.warning(presupuesto.date_from.strftime('%m') + ' ' +presupuesto.date_to.strftime('%m'))
                                if presupuesto.date_from.strftime('%m') == '01':
                                    dicc_analisis_presupuestario[presupuesto.general_budget_id.id]['Enero']+=presupuesto.planned_amount
                                if presupuesto.date_from.strftime('%m') == '02':
                                    dicc_analisis_presupuestario[presupuesto.general_budget_id.id]['Febrero']+=presupuesto.planned_amount
                                if presupuesto.date_from.strftime('%m') == '03':
                                    dicc_analisis_presupuestario[presupuesto.general_budget_id.id]['Marzo']+=presupuesto.planned_amount
                                if presupuesto.date_from.strftime('%m') == '04':
                                    dicc_analisis_presupuestario[presupuesto.general_budget_id.id]['Abril']+=presupuesto.planned_amount
                                if presupuesto.date_from.strftime('%m') == '05':
                                    dicc_analisis_presupuestario[presupuesto.general_budget_id.id]['Mayo']+=presupuesto.planned_amount
                                if presupuesto.date_from.strftime('%m') == '06':
                                    dicc_analisis_presupuestario[presupuesto.general_budget_id.id]['Junio']+=presupuesto.planned_amount
                                if presupuesto.date_from.strftime('%m') == '07':
                                    dicc_analisis_presupuestario[presupuesto.general_budget_id.id]['Julio']+=presupuesto.planned_amount
                                if presupuesto.date_from.strftime('%m') == '08':
                                    dicc_analisis_presupuestario[presupuesto.general_budget_id.id]['Agosto']+=presupuesto.planned_amount
                                if presupuesto.date_from.strftime('%m') == '09':
                                    dicc_analisis_presupuestario[presupuesto.general_budget_id.id]['Septiembre']+=presupuesto.planned_amount
                                if presupuesto.date_from.strftime('%m') == '10':
                                    dicc_analisis_presupuestario[presupuesto.general_budget_id.id]['Octubre']+=presupuesto.planned_amount
                                if presupuesto.date_from.strftime('%m') == '11':
                                    dicc_analisis_presupuestario[presupuesto.general_budget_id.id]['Noviembre']+=presupuesto.planned_amount
                                if presupuesto.date_from.strftime('%m') == '12':
                                    dicc_analisis_presupuestario[presupuesto.general_budget_id.id]['Diciembre']+=presupuesto.planned_amount
                                dicc_analisis_presupuestario[presupuesto.general_budget_id.id]['total']+=presupuesto.planned_amount
                #             if mes_pos_presupuestaria in dicc_analisis_presupuestario and presupuesto.planned_amount:
                #                 if presupuesto.planned_amount != 0:
                #                     logging.warning(fecha_inicio+'----'+presupuesto.general_budget_id.name+':    '+str(presupuesto.planned_amount) + ' / '+ str(linea.tipo_cambio))
                #                     calculo = round(presupuesto.planned_amount / linea.tipo_cambio, 2)
                #                 dicc_analisis_presupuestario[mes_pos_presupuestaria]['importe_previsto'] += calculo
                #                 if presupuesto.practical_amount != 0:
                #                     calculo_importe_real = round(presupuesto.practical_amount/ linea.tipo_cambio,2)
                #                 dicc_analisis_presupuestario[mes_pos_presupuestaria]['importe_real'] += calculo_importe_real
                # logging.warning('')
                # logging.warning('')

            fila = 5
            total_enero, total_febrero, total_marzo, total_abril, total_mayo, total_junio, total_julio, total_agosto, total_septiembre=(0,0,0,0,0,0,0,0,0)
            total_octubre, total_noviembre, total_diciembre = (0,0,0)
            total_general = 0
            for elemento in dicc_analisis_presupuestario:
                hoja.write(fila,0, dicc_analisis_presupuestario[elemento]['posicion_presupuestaria'])
                columna=1
                for ms in lista_meses:
                    if ms != 'UNKNOW':
                        hoja.write(fila,columna, dicc_analisis_presupuestario[elemento][ms])
                        columna+=1
                        if ms == 'Enero':
                            total_enero += dicc_analisis_presupuestario[elemento][ms]
                        if ms == 'Febrero':
                            total_febrero += dicc_analisis_presupuestario[elemento][ms]
                        if ms == 'Marzo':
                            total_marzo += dicc_analisis_presupuestario[elemento][ms]
                        if ms == 'Abril':
                            total_abril += dicc_analisis_presupuestario[elemento][ms]
                        if ms == 'Mayo':
                            total_mayo += dicc_analisis_presupuestario[elemento][ms]
                        if ms == 'Junio':
                            total_junio += dicc_analisis_presupuestario[elemento][ms]
                        if ms == 'Julio':
                            total_julio += dicc_analisis_presupuestario[elemento][ms]
                        if ms == 'Agosto':
                            total_agosto += dicc_analisis_presupuestario[elemento][ms]
                        if ms == 'Septiembre':
                            total_septiembre += dicc_analisis_presupuestario[elemento][ms]
                        if ms == 'Noviembre':
                            total_noviembre += dicc_analisis_presupuestario[elemento][ms]
                        if ms == 'Diciembre':
                            total_diciembre += dicc_analisis_presupuestario[elemento][ms]
                hoja.write(fila,columna, dicc_analisis_presupuestario[elemento]['total'])
                total_general +=dicc_analisis_presupuestario[elemento]['total']
                fila+=1
            hoja.write(fila,0, 'RESULTADO', formato_titulo)
            hoja.write(fila,1, total_enero, formato_totales)
            hoja.write(fila,2, total_febrero, formato_totales)
            hoja.write(fila,3, total_marzo, formato_totales)
            hoja.write(fila,4, total_abril, formato_totales)
            hoja.write(fila,5, total_mayo, formato_totales)
            hoja.write(fila,6, total_junio, formato_totales)
            hoja.write(fila,7, total_julio, formato_totales)
            hoja.write(fila,8, total_agosto, formato_totales)
            hoja.write(fila,9, total_septiembre, formato_totales)
            hoja.write(fila,10, total_octubre, formato_totales)
            hoja.write(fila,11, total_noviembre, formato_totales)
            hoja.write(fila,12, total_diciembre, formato_totales)
            hoja.write(fila,13, total_general, formato_totales)
            # estilo_fecha = libro.add_format({'align':'center'})
            # for elemento1 in dicc_analisis_presupuestario:
            #     hoja.write(fila,0, dicc_analisis_presupuestario[elemento1]['posicion_presupuestaria'])
            #     hoja.write(fila,1, dicc_analisis_presupuestario[elemento1]['fecha_inicio'], estilo_fecha)
            #     hoja.write(fila,2, dicc_analisis_presupuestario[elemento1]['fecha_final'], estilo_fecha)
            #     hoja.write(fila,3, dicc_analisis_presupuestario[elemento1]['importe_previsto'])
            #     hoja.write(fila,4, dicc_analisis_presupuestario[elemento1]['importe_real'])
            #     fila+=1


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
