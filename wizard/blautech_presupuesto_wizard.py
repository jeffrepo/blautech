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

            timezone = pytz.timezone(self._context.get('tz') or self.env.user.tz or 'UTC')

            formato_titulo = libro.add_format({'size': 11, 'color':'#ffffff', 'align':'center', 'fg_color':'#21618C'})
            formato_totales = libro.add_format({'size': 11, 'color':'#ffffff', 'align':'right', 'fg_color':'#2E86C1'})


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
                            compania_posicion_presupuestaria = str(linea.compania.id)+'-'+str(presupuesto.general_budget_id.id)
                            if compania_posicion_presupuestaria not in dicc_analisis_presupuestario:
                                dicc_analisis_presupuestario[compania_posicion_presupuestaria]={
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
                                'compania': presupuesto.company_id.id
                                }
                        if compania_posicion_presupuestaria in dicc_analisis_presupuestario and linea.compania.id == dicc_analisis_presupuestario[compania_posicion_presupuestaria]['compania']:
                            if presupuesto.date_from.strftime('%m') == presupuesto.date_to.strftime('%m') :
                                if presupuesto.date_from.strftime('%m') == '01':
                                    if presupuesto.planned_amount < 0:
                                        valor_positivo = presupuesto.planned_amount * -1
                                        dicc_analisis_presupuestario[compania_posicion_presupuestaria]['Enero']+= round(valor_positivo / linea.tipo_cambio,2)
                                    else:
                                        dicc_analisis_presupuestario[compania_posicion_presupuestaria]['Enero']+=round(presupuesto.planned_amount / linea.tipo_cambio,2)
                                if presupuesto.date_from.strftime('%m') == '02':
                                    if presupuesto.planned_amount < 0:
                                        valor_positivo = presupuesto.planned_amount * -1
                                        dicc_analisis_presupuestario[compania_posicion_presupuestaria]['Febrero']+=round(valor_positivo / linea.tipo_cambio,2)
                                    else:
                                        dicc_analisis_presupuestario[compania_posicion_presupuestaria]['Febrero']+=round(presupuesto.planned_amount / linea.tipo_cambio,2)
                                if presupuesto.date_from.strftime('%m') == '03':
                                    if presupuesto.planned_amount < 0:
                                        valor_positivo = presupuesto.planned_amount * -1
                                        dicc_analisis_presupuestario[compania_posicion_presupuestaria]['Marzo']+=round(valor_positivo / linea.tipo_cambio,2)
                                    else:
                                        dicc_analisis_presupuestario[compania_posicion_presupuestaria]['Marzo']+=round(presupuesto.planned_amount / linea.tipo_cambio,2)
                                if presupuesto.date_from.strftime('%m') == '04':
                                    if presupuesto.planned_amount < 0:
                                        valor_positivo = presupuesto.planned_amount * -1
                                        dicc_analisis_presupuestario[compania_posicion_presupuestaria]['Abril']+=round(valor_positivo / linea.tipo_cambio,2)
                                    else:
                                        dicc_analisis_presupuestario[compania_posicion_presupuestaria]['Abril']+=round(presupuesto.planned_amount / linea.tipo_cambio,2)
                                if presupuesto.date_from.strftime('%m') == '05':
                                    if presupuesto.planned_amount < 0:
                                        valor_positivo = presupuesto.planned_amount * -1
                                        dicc_analisis_presupuestario[compania_posicion_presupuestaria]['Mayo']+=round(valor_positivo / linea.tipo_cambio,2)
                                    else:
                                        dicc_analisis_presupuestario[compania_posicion_presupuestaria]['Mayo']+=round(presupuesto.planned_amount / linea.tipo_cambio,2)
                                if presupuesto.date_from.strftime('%m') == '06':
                                    if presupuesto.planned_amount < 0:
                                        valor_positivo = presupuesto.planned_amount * -1
                                        dicc_analisis_presupuestario[compania_posicion_presupuestaria]['Junio']+=round(valor_positivo / linea.tipo_cambio,2)
                                    else:
                                        dicc_analisis_presupuestario[compania_posicion_presupuestaria]['Junio']+=round(presupuesto.planned_amount / linea.tipo_cambio,2)
                                if presupuesto.date_from.strftime('%m') == '07':
                                    if presupuesto.planned_amount < 0:
                                        valor_positivo = presupuesto.planned_amount * -1
                                        dicc_analisis_presupuestario[compania_posicion_presupuestaria]['Julio']+= round(valor_positivo / linea.tipo_cambio,2)
                                    else:
                                        dicc_analisis_presupuestario[compania_posicion_presupuestaria]['Julio']+= round(presupuesto.planned_amount / linea.tipo_cambio,2)
                                if presupuesto.date_from.strftime('%m') == '08':
                                    if presupuesto.planned_amount < 0:
                                        valor_positivo = presupuesto.planned_amount * -1
                                        dicc_analisis_presupuestario[compania_posicion_presupuestaria]['Agosto']+= round(valor_positivo / linea.tipo_cambio,2)
                                    else:
                                        dicc_analisis_presupuestario[compania_posicion_presupuestaria]['Agosto']+= round(presupuesto.planned_amount / linea.tipo_cambio,2)
                                if presupuesto.date_from.strftime('%m') == '09':
                                    if presupuesto.planned_amount < 0:
                                        valor_positivo = presupuesto.planned_amount * -1
                                        dicc_analisis_presupuestario[compania_posicion_presupuestaria]['Septiembre']+= round(valor_positivo / linea.tipo_cambio,2)
                                    else:
                                        dicc_analisis_presupuestario[compania_posicion_presupuestaria]['Septiembre']+= round(presupuesto.planned_amount / linea.tipo_cambio,2)
                                if presupuesto.date_from.strftime('%m') == '10':
                                    if presupuesto.planned_amount < 0:
                                        valor_positivo = presupuesto.planned_amount * -1
                                        dicc_analisis_presupuestario[compania_posicion_presupuestaria]['Octubre']+=round(valor_positivo / linea.tipo_cambio,2)
                                    else:
                                        dicc_analisis_presupuestario[compania_posicion_presupuestaria]['Octubre']+=round(presupuesto.planned_amount / linea.tipo_cambio,2)
                                if presupuesto.date_from.strftime('%m') == '11':
                                    if presupuesto.planned_amount < 0:
                                        valor_positivo = presupuesto.planned_amount * -1
                                        dicc_analisis_presupuestario[compania_posicion_presupuestaria]['Noviembre']+= round(valor_positivo / linea.tipo_cambio,2)
                                    else:
                                        dicc_analisis_presupuestario[compania_posicion_presupuestaria]['Noviembre']+= round(presupuesto.planned_amount / linea.tipo_cambio,2)
                                if presupuesto.date_from.strftime('%m') == '12':
                                    if presupuesto.planned_amount < 0:
                                        valor_positivo = presupuesto.planned_amount * -1
                                        dicc_analisis_presupuestario[compania_posicion_presupuestaria]['Diciembre']+= round(valor_positivo / linea.tipo_cambio,2)
                                    else:
                                        dicc_analisis_presupuestario[compania_posicion_presupuestaria]['Diciembre']+= round(presupuesto.planned_amount / linea.tipo_cambio,2)

                                if presupuesto.planned_amount < 0:
                                    valor_positivo = presupuesto.planned_amount * -1
                                    dicc_analisis_presupuestario[compania_posicion_presupuestaria]['total']+=round(valor_positivo / linea.tipo_cambio,2)
                                else:
                                    dicc_analisis_presupuestario[compania_posicion_presupuestaria]['total']+=round(presupuesto.planned_amount / linea.tipo_cambio,2)


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
                            total_enero += round(dicc_analisis_presupuestario[elemento][ms],2)
                        if ms == 'Febrero':
                            total_febrero += round(dicc_analisis_presupuestario[elemento][ms],2)
                        if ms == 'Marzo':
                            total_marzo += round(dicc_analisis_presupuestario[elemento][ms],2)
                        if ms == 'Abril':
                            total_abril += round(dicc_analisis_presupuestario[elemento][ms],2)
                        if ms == 'Mayo':
                            total_mayo += round(dicc_analisis_presupuestario[elemento][ms],2)
                        if ms == 'Junio':
                            total_junio += round(dicc_analisis_presupuestario[elemento][ms],2)
                        if ms == 'Julio':
                            total_julio += round(dicc_analisis_presupuestario[elemento][ms],2)
                        if ms == 'Agosto':
                            total_agosto += round(dicc_analisis_presupuestario[elemento][ms],2)
                        if ms == 'Septiembre':
                            total_septiembre += round(dicc_analisis_presupuestario[elemento][ms],2)
                        if ms == 'Noviembre':
                            total_noviembre += round(dicc_analisis_presupuestario[elemento][ms],2)
                        if ms == 'Diciembre':
                            total_diciembre += round(dicc_analisis_presupuestario[elemento][ms],2)
                hoja.write(fila,columna, dicc_analisis_presupuestario[elemento]['total'])
                total_general += round(dicc_analisis_presupuestario[elemento]['total'],2)
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
