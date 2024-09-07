# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import datetime, math
from datetime import timedelta
from dateutil.relativedelta import relativedelta
import calendar
from datetime import datetime


class SolicituddeRenovaciones(Document):
	pass

@frappe.whitelist()
def create_renovation_doc(employees=None):
	data_employees = frappe.parse_json(employees)
	month_json = {1:"Enero",2:"Febrero",3:"Marzo",4:"Abril",5:"Mayo",6:"Junio",7:"Julio",8:"Agosto",9:"Setiembre",10:"Octubre",11:"Noviembre",12:"Diciembre"}
	today = datetime.today().date()
	first_day_of_next_month = today.replace(day=1, month=today.month + 1)
	mes_texto = month_json[first_day_of_next_month.month]
	day_text = str(first_day_of_next_month.day)
	ano = first_day_of_next_month.year
	response_create = []

	for employee in data_employees:
		new_doc = frappe.new_doc("Solicitud de Cambio de Modalidad")
		new_doc.empleado = employee["name"]
		new_doc.modalidad_nueva = employee["employment_type"]
		new_doc.fecha_de_inicio = "0" + day_text + "-" + mes_texto
		new_doc.anio = ano
		new_doc.insert(ignore_permissions=True,ignore_mandatory=True)
		update_renovation = frappe.db.set_value('Trabajadores pendiete de renovar', employee["name_table"], {
			'cambio_de_modalidad': 1
		})
		frappe.db.commit()
		response_create.append(new_doc)

	return response_create