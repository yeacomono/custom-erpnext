# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

import datetime, math

class LiquidacionesAnual(Document):
	pass


@frappe.whitelist(allow_guest=True)
def search_liquidation(dni):
	values_liquidation = {
		'document': dni
	}
	list_liquidation = frappe.db.sql("""
		SELECT
			st.name,
			st.social_benefits_certificate,
			st.job_certificate,
			st.cts_letter,
			st.low_of_t,
			st.ticket,
			st.cese_form,
			st.guide_number,
			st.docstatus,
			st.pay_state,
			st.workflow_state
		FROM
			`tabLiquidaciones Anual` as st
		WHERE
			st.document = %(document)s
	""", values=values_liquidation, as_dict=True)

	if len(list_liquidation) == 0:
		return {
			'status': False,
			'message': 'No se encontro liquidacion',
			'data': {}
		}
	else:
		return {
			'status': True,
			'message': 'Se encontro liquidacion',
			'data': list_liquidation[0]
		}

@frappe.whitelist(allow_guest=True)
def create_liquidation(data_form):

	data = frappe.parse_json(data_form)
	months = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Setiembre", "Octubre", "Noviembre", "Diciembre"];


	values_employee = {
		'passport_number': data.document
	}
	list_employee = frappe.db.sql("""
		SELECT
			st.name,
			st.nombre_completo,
			st.designation,
			st.company,
			st.fecha_de_ingreso_real,
			st.fecha_de_relevo,
			st.id_sucursal,
			st.department,
			st.date_of_birth,
			st.employment_type,
			st.zona_recursos,
			st.zona_nacional,
			st.branch
		FROM
			`tabEmployee` as st
		WHERE
			st.passport_number = %(passport_number)s
	""", values=values_employee, as_dict=True)

	employee = list_employee[0]

	fecha_actual = str(employee['fecha_de_relevo'])
	fecha_objeto = datetime.datetime.strptime(fecha_actual, "%Y-%m-%d").date()

	numero_mes = fecha_objeto.month
	numero_year = fecha_objeto.year

	doc = frappe.get_doc({
		'doctype': 'Liquidaciones Anual',
		'employee': employee['name'],
		'pay_state': 'No Pagado',
		'document': data.document,
		'month': months[numero_mes-1],
		'year': numero_year,
		'social_benefits_certificate': data.social_benefits_certificate if data.social_benefits_certificate is not None else "",
		'job_certificate': data.job_certificate if data.job_certificate is not None else "",
		'cts_letter': data.cts_letter if data.cts_letter is not None else "",
		'low_of_t': data.low_of_t if data.low_of_t is not None else "",
		'ticket': data.ticket if data.ticket is not None else "",
		'cese_form': data.cese_form if data.cese_form is not None else "",
		'workflow_state': 'Borrador',
		'full_name': list_employee[0]['nombre_completo'] if list_employee[0]['nombre_completo'] is not None else "",
		'designation': list_employee[0]['designation'] if list_employee[0]['designation'] is not None else "",
		'zone': list_employee[0]['zona_nacional'] if list_employee[0]['zona_nacional'] is not None else "",
		'rrhh_zone': list_employee[0]['zona_recursos'] if list_employee[0]['zona_recursos'] is not None else "",
		'company': list_employee[0]['company'] if list_employee[0]['company'] is not None else "",
		'branch': list_employee[0]['branch'] if list_employee[0]['branch'] is not None else "",
		'entry_date': list_employee[0]['fecha_de_ingreso_real'] if list_employee[0]['fecha_de_ingreso_real'] is not None else "",
		'relief_date': list_employee[0]['fecha_de_relevo'] if list_employee[0]['fecha_de_relevo'] is not None else "",
		'id_branch': list_employee[0]['id_sucursal'] if list_employee[0]['id_sucursal'] is not None else "",
		'department': list_employee[0]['department'] if list_employee[0]['department'] is not None else "",
		'birthdate': list_employee[0]['date_of_birth'] if list_employee[0]['date_of_birth'] is not None else "",
		'job_type': list_employee[0]['employment_type'] if list_employee[0]['employment_type'] is not None else ""
	})

	doc.db_insert()

	if doc.name is not None:
		return {
			'status': True,
			'message': 'Se creo la liquidacion'
		}
	else:
		return {
			'status': False,
			'message': 'Error al crear la liquidacion, contacte con soporte'
		}

@frappe.whitelist(allow_guest=True)
def update_liquidation(data_form, name):
	data = frappe.parse_json(data_form)
	months = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Setiembre", "Octubre", "Noviembre", "Diciembre"];

	values_employee = {
		'passport_number': data.document
	}
	list_employee = frappe.db.sql("""
		SELECT
			st.name,
			st.nombre_completo,
			st.designation,
			st.company,
			st.fecha_de_ingreso_real,
			st.fecha_de_relevo,
			st.id_sucursal,
			st.department,
			st.date_of_birth,
			st.employment_type,
			st.zona_recursos,
			st.zona_nacional,
			st.branch
		FROM
			`tabEmployee` as st
		WHERE
			st.passport_number = %(passport_number)s
	""", values=values_employee, as_dict=True)

	employee = list_employee[0]

	fecha_actual = str(employee['fecha_de_relevo'])
	fecha_objeto = datetime.datetime.strptime(fecha_actual, "%Y-%m-%d").date()

	numero_mes = fecha_objeto.month
	numero_year = fecha_objeto.year

	frappe.db.set_value('Liquidaciones Anual', name, {
		'employee': employee['name'],
		'pay_state': 'No Pagado',
		'document': data.document,
		'month': months[numero_mes-1],
		'year': numero_year,
		'social_benefits_certificate': data.social_benefits_certificate if data.social_benefits_certificate is not None else "",
		'job_certificate': data.job_certificate if data.job_certificate is not None else "",
		'cts_letter': data.cts_letter if data.cts_letter is not None else "",
		'low_of_t': data.low_of_t if data.low_of_t is not None else "",
		'ticket': data.ticket if data.ticket is not None else "",
		'cese_form': data.cese_form if data.cese_form is not None else "",
		'full_name': list_employee[0]['nombre_completo'] if list_employee[0]['nombre_completo'] is not None else "",
		'designation': list_employee[0]['designation'] if list_employee[0]['designation'] is not None else "",
		'zone': list_employee[0]['zona_nacional'] if list_employee[0]['zona_nacional'] is not None else "",
		'rrhh_zone': list_employee[0]['zona_recursos'] if list_employee[0]['zona_recursos'] is not None else "",
		'company': list_employee[0]['company'] if list_employee[0]['company'] is not None else "",
		'branch': list_employee[0]['branch'] if list_employee[0]['branch'] is not None else "",
		'entry_date': list_employee[0]['fecha_de_ingreso_real'] if list_employee[0]['fecha_de_ingreso_real'] is not None else "",
		'relief_date': list_employee[0]['fecha_de_relevo'] if list_employee[0]['fecha_de_relevo'] is not None else "",
		'id_branch': list_employee[0]['id_sucursal'] if list_employee[0]['id_sucursal'] is not None else "",
		'department': list_employee[0]['department'] if list_employee[0]['department'] is not None else "",
		'birthdate': list_employee[0]['date_of_birth'] if list_employee[0]['date_of_birth'] is not None else "",
		'job_type': list_employee[0]['employment_type'] if list_employee[0]['employment_type'] is not None else ""
	})

	return {
		'status': True,
		'message': 'Se actualizo la liquidacion'
	}

