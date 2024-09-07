# Copyright (c) 2023, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document
from itertools import groupby
import datetime, math
from datetime import timedelta
from dateutil.relativedelta import relativedelta
import frappe
from frappe.model.db_query import DatabaseQuery
from frappe.utils import flt, cint

class ApartadoDescansoMedico(Document):
	pass

@frappe.whitelist(allow_guest=True)
def get_data():
	contingencia_values = ['ACC. LABORAL', 'ACC. LABORAL-recurrente', 'LIC. X MATERNIDAD']
	values = {
		'seguimiento': 'CON SEGUIMIENTO',
		'status': 'Active',
		'contingencia_values': contingencia_values
	}

	try:
		items = frappe.db.sql("""
			SELECT
				adm.name AS nameDocument,
				tc.name AS nameDocumentTable,
				adm.nombre_completo AS fullName,
				adm.cantidad_de_llamadas AS qtyCalls,
				adm.fecha_de_fin_de_dm AS endDate,
				adm.apellidos_y_nombres AS IdEmployee,
				emp.status AS statusEmployee
			FROM
				`tabApartado Descanso Medico` as adm
			LEFT JOIN
				`tabtable_control` as tc ON adm.name = tc.parent
			LEFT JOIN
				`tabEmployee` as emp ON adm.apellidos_y_nombres = emp.name
			WHERE
				adm.seguimiento = %(seguimiento)s and emp.status = %(status)s
				and (adm.estado_de_creacion = 'OBSERVADO POR FALTA DE DOCUMENTO' or
					(adm.estado_de_creacion = 'VALIDADO POR EL MEDICO' and
					adm.contingencia IN %(contingencia_values)s))
		""", values=values, as_dict=True)


		if len(items) == 0:
			return {
				"data": []
			}

		grupos = {}
		for key, group in groupby(items, key=lambda x: x['nameDocument']):
			grupos[key] = list(group)

		nuevo_objeto = {
			"data":[]
		}

		for key, values in grupos.items():
			contador = 0
			objeto = {
				"nameDocument": key,
				"qtyCallsOpen": contador,
				"fullName": "",
				"endDate": "",
				"qtyCalls": "",
				"status": ""
			}
			for value in values:
				if value["nameDocumentTable"] is not None:
					contador += 1

				objeto["fullName"] = value["fullName"]
				objeto["endDate"] = value["endDate"]
				objeto["qtyCalls"] = value["qtyCalls"]
				objeto["status"] = value["statusEmployee"]
			objeto["qtyCallsOpen"] = contador
			nuevo_objeto["data"].append(objeto)


		return nuevo_objeto

	except Exception as ex:
		return str(ex)

@frappe.whitelist(allow_guest=True)
def remunerative_concepts(day_init="2024-01-01",day_end="2024-04-01",employee="HR-EMP-04918",date_joining="2024-04-01"):
	values = {
		'start_date': day_init,
		'end_date': day_end,
		'employee': employee,
		'parentfield': 'earnings',
		'salary_component': ['HABER MENSUAL','ASIGNACION FAMILIAR','VACACIONES','DESCANSO MEDICO'],
		'fecha_ingreso': date_joining
	}

	get_salary = frappe.db.sql("""
			SELECT
				ls.name AS salary_name,
				sd.parent AS parent_name,
				sd.salary_component,
				sd.amount,
				ls.start_date,
				ls.payment_days
			FROM
				`tabSalary Slip` as ls
			LEFT JOIN
				`tabSalary Detail` as sd ON ls.name = sd.parent
			WHERE
				ls.start_date BETWEEN %(start_date)s and %(end_date)s and ls.employee = %(employee)s
				and sd.parentfield = %(parentfield)s and sd.salary_component IN %(salary_component)s
				and ls.fecha_ingreso = %(fecha_ingreso)s
		""", values=values, as_dict=True)

	json_salary = {}

	for salary in get_salary:
		key = salary["salary_name"]
		if key in json_salary:
			json_salary[key].append(salary)
		else:
			json_salary[key] = [salary]

	return json_salary


@frappe.whitelist(allow_guest=True)
def monthly_subsidy_payment():
	month_json = {1:"Enero",2:"Febrero",3:"Marzo",4:"Abril",5:"Mayo",6:"Junio",7:"Julio",8:"Agosto",9:"Setiembre",10:"Octubre",11:"Noviembre",12:"Diciembre"}
	fecha_actual = datetime.date.today()
	dia_actual = datetime.date.today().day
	# dia_actual = 1
	fecha_anterior = (fecha_actual - relativedelta(months=3)).replace(day=1)
	mes_anterior_numero = fecha_anterior.month
	ultimo_dia_mes_anterior = fecha_actual - timedelta(days=1)

	if dia_actual != 1:
		return {
			'status': False,
			'message': 'No es primero del Mes'
		}

	values_salary = {
		'start_date': fecha_anterior,
		'parentfield': 'earnings',
		'salary_component': ['SUBSIDIO POR MATERNIDAD','SUBSIDIO POR ENFERMEDAD','SUBSIDIO POR ACCIDENTE']
	}

	get_salary = frappe.db.sql("""
		SELECT
			ls.name AS salary_name,
			sd.parent AS parent_name,
			sd.salary_component,
			sd.amount,
			ls.start_date,
			ls.employee
		FROM
			`tabSalary Slip` as ls
		LEFT JOIN
			`tabSalary Detail` as sd ON ls.name = sd.parent
		WHERE
			ls.start_date = %(start_date)s and sd.parentfield = %(parentfield)s 
			and sd.salary_component IN %(salary_component)s
	""", values=values_salary, as_dict=True)

	if len(get_salary) == 0:
		return {
			'status': False,
			'message': 'No hubo empleados con subsidios'
		}

	json_salary_subsidy = {}

	for salary in get_salary:
		key = salary["employee"]
		json_salary_subsidy[key] = salary

	values_subsidy = {
		'id_trabajadora': list(json_salary_subsidy.keys()),
		'mes': month_json[mes_anterior_numero]
	}

	get_subsidy_document = frappe.db.sql("""
		SELECT
			ls.name AS document_name,
			ls.id_trabajadora,
			sd.mes,
			sd.name AS name_table,
			sd.pago_adelantado
		FROM
			`tabCalculo de Subsidios` as ls
		LEFT JOIN
			`tabPago Subsidio por Mes` as sd ON ls.name = sd.parent
		WHERE
			sd.mes = %(mes)s and ls.id_trabajadora IN %(id_trabajadora)s
	""", values=values_subsidy, as_dict=True)

	json_subsidy_document = {}

	for subsidy in get_subsidy_document:
		key = subsidy["id_trabajadora"]
		json_subsidy_document[key] = subsidy

	if len(json_subsidy_document) == 0:
		return {
			'status': False,
			'message': 'No se encontraron documentos de subsidios'
		}

	for subsidy in get_subsidy_document:
		update_subsidy = frappe.db.set_value('Pago Subsidio por Mes', subsidy['name_table'], {
			'estado': 'Pagado',
			'fecha_de_pago': ultimo_dia_mes_anterior
		})

	return {
		'status': True,
		'message': 'Se actualizaron los pagos de subsidios'
	}
