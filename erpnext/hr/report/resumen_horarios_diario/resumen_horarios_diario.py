# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
import requests
import frappe
from datetime import timedelta
import calendar


def execute(filters=None):
	columns, data = [], []
	columns = get_columns()
	url = "https://capacitacion.shalom.com.pe/api/method/erpnext.hr.doctype.attendance.api.resumenHorariosDiario?"

	if filters.get("fecha") is not None:
		url = url + "&fecha=" + filters.get("fecha")

	if filters.get("empleado") is not None:
		url = url + "&empleado=" + filters.get("empleado")

	if filters.get("sucursal") is not None:
		url = url + "&sucursal=" + filters.get("sucursal")

	if filters.get("departamento") is not None:
		url = url + "&department=" + filters.get("departamento")

	arrayData = requests.get(url)
	arrayData = arrayData.json()

	if "message" in arrayData:
		return columns, arrayData.get("message")

def get_columns():
	columns = [
		{
			'label': "EMPLEADO",
			'fieldname': 'employee',
			'fieldtype': 'Data',
			'width': 100
		},
		{
			'label': "NOMBRE COMPLETO",
			'fieldname': 'employee_name',
			'fieldtype': 'Data',
			'width': 220,
		},
		{
			'label': "ENTRADA",
			'fieldname': 'entrada',
			'fieldtype': 'Data',
			'width': 120,
		},
		{
			'label': "INICIO DE ALMUERZO",
			'fieldname': 'inicio_almuerzo',
			'fieldtype': 'Data',
			'width': 120,
		},
		{
			'label': "FIN DE ALMUERZO",
			'fieldname': 'fin_almuerzo',
			'fieldtype': 'Data',
			'width': 120,
		},
		{
			'label': "SALIDA",
			'fieldname': 'salida',
			'fieldtype': 'Data',
			'width': 120,
		},
		{
			'label': "TARDANZA",
			'fieldname': 'tardanza',
			'fieldtype': 'Data',
			'width': 50,
		},
		{
			'label': "HORAS EXTRAS",
			'fieldname': 'horasExtrasReal',
			'fieldtype': 'Data',
			'width': 50,
		},
		{
			'label': "TIPO",
			'fieldname': 'employment_type',
			'fieldtype': 'Data',
			'width': 120,
		},
		{
			'label': "TURNO ENTRADA",
			'fieldname': 'turnoEntrada',
			'fieldtype': 'Data',
			'width': 120,
		},
		{
			'label': "TURNO SALIDA",
			'fieldname': 'turnoSalida',
			'fieldtype': 'Data',
			'width': 120,
		}
	]
	return columns
