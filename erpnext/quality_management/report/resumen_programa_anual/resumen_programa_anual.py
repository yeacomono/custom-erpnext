# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
import requests

def execute(filters=None):
	columns, data = [], []
	columns = get_columns()
	arrayData = requests.post("https://horario-salida-qa-erpwin.shalom.com.pe/api/reporte/board-activity-sst", json = filters)
	arrayData = arrayData.json()
	if "data" in arrayData:
		return columns, arrayData.get("data")



def get_columns():
	columns = [
		{
			'label': "DESCRIPCIÓN",
			'fieldname': 'description',
			'fieldtype': 'Data',
			'width': 300
		},
		{
			'label': "ENERO",
			'fieldname': 'enero',
			'fieldtype': 'Data',
			'width': 80,
		},
		{
			'label': "FEBRERO",
			'fieldname': 'febrero',
			'fieldtype': 'Data',
			'width': 80,
		},
		{
			'label': "MARZO",
			'fieldname': 'marzo',
			'fieldtype': 'Data',
			'width': 80,
		},
		{
			'label': "ABRIL",
			'fieldname': 'abril',
			'fieldtype': 'Data',
			'width': 80,
		},
		{
			'label': "MAYO",
			'fieldname': 'mayo',
			'fieldtype': 'Data',
			'width': 80,
		},
		{
			'label': "JUNIO",
			'fieldname': 'junio',
			'fieldtype': 'Data',
			'width': 80,
		},
		{
			'label': "JULIO",
			'fieldname': 'julio',
			'fieldtype': 'Data',
			'width': 80,
		},
		{
			'label': "AGOSTO",
			'fieldname': 'agosto',
			'fieldtype': 'Data',
			'width': 80,
		},
		{
			'label': "SETIEMBRE",
			'fieldname': 'setiembre',
			'fieldtype': 'Data',
			'width': 80,
		},
		{
			'label': "OCTUBRE",
			'fieldname': 'octubre',
			'fieldtype': 'Data',
			'width': 80,
		},
		{
			'label': "NOVIEMBRE",
			'fieldname': 'noviembre',
			'fieldtype': 'Data',
			'width': 80,
		},
		{
			'label': "DICIEMBRE",
			'fieldname': 'diciembre',
			'fieldtype': 'Data',
			'width': 80,
		},
		{
			'label': "TOTAL",
			'fieldname': 'total',
			'fieldtype': 'Data',
			'width': 80,
		},
	]
	return columns
