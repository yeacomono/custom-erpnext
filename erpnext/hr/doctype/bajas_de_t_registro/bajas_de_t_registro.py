# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document
from itertools import groupby
from datetime import timedelta, datetime
from dateutil.relativedelta import relativedelta
import frappe

class BajasdeTRegistro(Document):
	pass

@frappe.whitelist(allow_guest=True)
def create_register_t(id_employee, date_leave, date_joining):

	values_register_t = {
		'id_empleado': id_employee,
		'fecha_de_ingreso': date_joining
	}

	get_register_t = frappe.db.sql("""
		SELECT
			ls.name,
			ls.docstatus
		FROM
			`tabBajas de T Registro` as ls
		WHERE
			ls.id_empleado = %(id_empleado)s and ls.fecha_de_ingreso = %(fecha_de_ingreso)s
	""", values=values_register_t, as_dict=True)

	if len(get_register_t) > 0:
		if get_register_t[0]["docstatus"] == 0:
			doc = frappe.get_doc('Bajas de T Registro', get_register_t[0]['name'])
			doc.fecha_de_relevo = date_leave
			doc.save()
			return {
				"status" : True,
				"message": "Se actualizo la fecha de relevo en la baja t"
			}
		elif get_register_t[0]["docstatus"] == 1:
			return {
				"status" : True,
				"message": "Ya cuenta con registro de baja"
			}

	month_json = {1:"Enero",2:"Febrero",3:"Marzo",4:"Abril",5:"Mayo",6:"Junio",7:"Julio",8:"Agosto",9:"Setiembre",10:"Octubre",11:"Noviembre",12:"Diciembre"}
	date_leave = datetime.strptime(date_leave, '%Y-%m-%d')
	month_text = month_json[date_leave.month]
	year_text = date_leave.year

	new_doc = frappe.new_doc("Bajas de T Registro")
	new_doc.id_empleado = id_employee
	new_doc.ano = year_text
	new_doc.mes = month_text
	new_doc.insert()

	return {
		"status" : True,
		"message": "Se creo el registro de baja"
	}

@frappe.whitelist(allow_guest=True)
def delete_register_t(id_employee):
	values_register_t = {
		'id_empleado': id_employee,
		'docstatus': 0
	}

	get_register_t = frappe.db.sql("""
		SELECT
			ls.name,
			ls.docstatus
		FROM
			`tabBajas de T Registro` as ls
		WHERE
			ls.id_empleado = %(id_empleado)s and ls.docstatus = %(docstatus)s
	""", values=values_register_t, as_dict=True)

	if len(get_register_t) == 0:
		return {
			'status': True,
			'message': 'No se encontraron documentos de baja t'
		}

	for register in get_register_t:
		frappe.db.delete("Bajas de T Registro", {
			"name": register["name"]
		})
		frappe.db.commit()

	return {
		'status': True,
		'message': 'Se eliminaron los documentos de baja t'
	}