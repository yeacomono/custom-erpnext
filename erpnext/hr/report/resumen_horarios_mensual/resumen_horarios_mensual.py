# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
import requests
import frappe
from datetime import timedelta
import calendar

def resumenHorariosMensual(mes=None, anio=None, empleadito=None, sucursal=None, department=None):
	months = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Setiembre', 'Octubre', 'Noviembre', 'Diciembre'];
	# empleadito = "HR-EMP-01411"
	# mes= "02"
	# anio = "2024"

	if mes is not None:
		mesString = months[int(mes) - 1]
		ultimo_dia = ultimo_dia_mes(int(anio) if anio is not None else 2024, int(mes))

	# sucursal = "PLAZA NORTE ENTREGAS"
	# department = "Supervisión nacional  - SE"

	where = ""
	whereHoraExtra = ""

	if anio is None or mes is None:
		return "Debe ingresar un año o un mes"

	if anio is not None and mes is not None:
		whereHoraExtra += f"AND hr.año = '{anio}' AND hr.mes = '{mesString}' "

	if empleadito is not None:
		where += f"AND emp.employee = '{empleadito}' "

	if sucursal is not None:
		where += f"AND emp.sucursal = '{sucursal}' "

	if department is not None:
		where += f"AND emp.departamento = '{department}' "

	where += f"AND (emp.late_time IS NOT NULL OR emp.overtime_time IS NOT NULL )"

	sqlConsulta = f"""
        SELECT
            emp.employee, emp.late_time, emp.overtime_time, emp.fecha_de_consolidado
        FROM
            `tabEmployee Checkin` as emp
        WHERE (emp.fecha_de_consolidado BETWEEN '{anio}-{mes}-01' AND '{anio}-{mes}-{ultimo_dia}') {where}
    """


	dataCheckin = frappe.db.sql(sqlConsulta, as_dict=True)
	empleado = []
	empleadoArray = {}
	for element in dataCheckin:
		element["late_time"] = int(element["late_time"]) if element["late_time"] else 0
		element["overtime_time"] = int(element["overtime_time"]) if element["overtime_time"] else 0

		if element["employee"] not in empleado:
			empleado.append(element["employee"])
			empleadoArray[element["employee"]] = element
		else:
			empleadoArray[element["employee"]]["late_time"] += element["late_time"]
			empleadoArray[element["employee"]]["overtime_time"] += element["overtime_time"]
	if len(empleado) >0:
		empleado = "(" + ", ".join(["'" + e + "'" for e in empleado]) + ")"
	else:
		return empleadoArray
	whereHoraExtra += f"AND hr.empleado IN {empleado} "

	consultaHoraExtra = f"""
        SELECT
            hr.empleado, hr.año, hr.mes, hr.hhee_al_25, hr.hhee_al_35, hr.hhee_al_100
        FROM
            `tabHoras Extras` as hr
        WHERE 1=1 {whereHoraExtra} 
    """

	dataHoraExtra = frappe.db.sql(consultaHoraExtra, as_dict=True)
	dataHora = {}
	for element in dataHoraExtra:
		hhee_al_25 = float(element["hhee_al_25"]) if element["hhee_al_25"] else 0
		hhee_al_35 = float(element["hhee_al_35"]) if element["hhee_al_35"] else 0
		hhee_al_100 = float(element["hhee_al_100"]) if element["hhee_al_100"] else 0
		if element["empleado"] in empleadoArray:
			empleadoArray[element["empleado"]]["horasExtrasReal"] = hhee_al_25 + hhee_al_35 + hhee_al_100


	empleadoArray = empleadoArray.values()
	return empleadoArray

def ultimo_dia_mes(año, mes):
	return calendar.monthrange(año, mes)[1]

def execute(filters=None):
	columns, data = [], []
	columns = get_columns()
	url = "https://capacitacion.shalom.com.pe/api/method/erpnext.hr.doctype.attendance.api.resumenHorariosMensual?mes="+filters.get("month")+"&anio="+filters.get("year")
	if filters.get("empleado") is not None:
		url = url + "&empleadito=" + filters.get("empleado")

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
			'width': 150
		},
		{
			'label': "NOMBRE COMPLETO",
			'fieldname': 'employee_name',
			'fieldtype': 'Data',
			'width': 220,
		},
		{
			'label': "TARDANZAS",
			'fieldname': 'late_time',
			'fieldtype': 'Data',
			'width': 160,
		},
		{
			'label': "HORAS EXTRAS REALES",
			'fieldname': 'overtime_time',
			'fieldtype': 'Data',
			'width': 160,
		},
		{
			'label': "HORAS EXTRAS INGRESADAS",
			'fieldname': 'horasExtrasReal',
			'fieldtype': 'Data',
			'width': 160,
		}
	]
	return columns
