# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class SolicituddePagos(Document):
	pass

@frappe.whitelist()
def get_list_permission_task(user):

	values_user_sistemas = {
		'parent': user,
		'role': "System Manager"
	}

	get_role_sistemas = frappe.db.sql("""
		SELECT
			br.name,
			br.role
		FROM 
			`tabHas Role` br
		WHERE 
			br.parent = %(parent)s AND br.role = %(role)s
	""", values=values_user_sistemas, as_dict=1)

	if len(get_role_sistemas) > 0:
		return ""

	if user == "43845174@shalomcontrol.com":
		transaction = "Transacción / Compensaciones"
		return "(`tabSolicitud de Pagos`.concepto = {transaction})".format(transaction=frappe.db.escape(transaction))

	values_user_finanzas = {
		'parent': user,
		'role': "Usuario Finanzas"
	}

	get_role_finanzas = frappe.db.sql("""
			SELECT
				br.name,
				br.role
			FROM 
				`tabHas Role` br
			WHERE 
				br.parent = %(parent)s AND br.role = %(role)s
		""", values=values_user_finanzas, as_dict=1)

	if len(get_role_finanzas):
		return ""

	values_user = {
		'parent': user,
		'role': "Supervisor Nacional"
	}

	get_role = frappe.db.sql("""
			SELECT
				br.name,
				br.role
			FROM 
				`tabHas Role` br
			WHERE 
				br.parent = %(parent)s AND br.role = %(role)s
		""", values=values_user, as_dict=1)

	if len(get_role) > 0:

		values_permission = {
			'allow': "Zonas Nacional",
			'user': user
		}

		get_permission = frappe.db.sql("""
				SELECT
					br.name,
					br.for_value
				FROM 
					`tabUser Permission` br
				WHERE 
					br.allow = %(allow)s AND br.user = %(user)s
			""", values=values_permission, as_dict=1)

		if len(get_permission) == 0:
			return ""

		zone_array = []

		for zone in get_permission:
			zone_array.append(zone["for_value"])

		values_branch = {
			'parent': zone_array
		}

		get_branch = frappe.db.sql("""
				SELECT
					br.name,
					br.agencias
				FROM 
					`tabTabla de Sucursales` br
				WHERE 
					br.parent IN %(parent)s
			""", values=values_branch, as_dict=1)

		branch_array = []

		for branch in get_branch:
			branch_array.append(branch["agencias"])

		formatted_branches = ','.join(["{}".format(frappe.db.escape(branch)) for branch in branch_array])
		branch_filter = "(`tabSolicitud de Pagos`.sucursal IN ({formatted_branches}))".format(formatted_branches=formatted_branches)
		return branch_filter

	values_employee = {
		'user_id': user
	}

	get_employee = frappe.db.sql("""
		SELECT
			br.name,
			br.user_id,
			br.designation
		FROM 
			`tabEmployee` br
		WHERE 
			br.user_id = %(user_id)s
	""", values=values_employee, as_dict=1)

	if len(get_employee) == 0:
		return ""

	employee_data = get_employee[0]

	if employee_data["designation"] in ["ENCARGADO DE AGENCIA","ADMINISTRADOR DE AGENCIA"]:
		return "(`tabSolicitud de Pagos`.owner = {user})".format(user=frappe.db.escape(user))

	return ""

