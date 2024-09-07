# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
import requests

def execute(filters=None):
	columns, data = [], []
	columns = get_columns()
	arrayData = requests.post("https://recursoshumanos.shalom.com.pe/api/reporte/reportProgramaActualSST", json = filters)
	arrayData = arrayData.json()
	if "data" in arrayData:
		return columns, arrayData.get("data")


def get_columns():
	columns = [
		{
			'label': "Lista de actividades",
			'fieldname': 'actividad',
			'fieldtype': 'Data',
			'width': 300
		},
		{
            'label': "Indicador",
            'fieldname': 'indicador',
            'fieldtype': 'Data',
            'width': 300
        },
		{
			'label': "Mes de Ejecución",
			'fieldname': 'mes_ejecucion',
			'fieldtype': 'Data',
			'width': 100,
		},
		{
			'label': "Total Programadas",
			'fieldname': 'total_programados',
			'fieldtype': 'Data',
			'width': 100,
		},
		{
			'label': "Total Ejecutadas",
			'fieldname': 'total_ejecutados',
			'fieldtype': 'Data',
			'width': 100,
		},
		{
			'label': "Total Reprogramadas",
			'fieldname': 'total_reprogramados',
			'fieldtype': 'Data',
			'width': 100,
		},
		{
			'label': "% DE EFICIENCIA",
			'fieldname': 'eficiencia',
			'fieldtype': 'Data',
			'width': 100,
		},

	]
	return columns