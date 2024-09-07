# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe

from frappe.model.document import Document
from frappe.model.db_query import DatabaseQuery
from frappe.utils import flt, cint
from itertools import groupby

class Branch(Document):
	pass

@frappe.whitelist()
def get_available_branches():
	lista_agencias = frappe.db.sql("""
		SELECT
			adm.name AS nameDocument
		FROM
			`tabBranch` adm
		WHERE
			adm.estado_de_sucursal = 1
	""", as_dict=1)

	name_agencias_costo = frappe.db.sql("""
		SELECT
			adm.name AS nameDocument
		FROM
			`tabBranch` adm
		WHERE
			adm.centro_de_costos_por_agencia = 1
	""", as_dict=1)

	if len(name_agencias_costo) >= 0:
		grupos = {}
		for key, group in groupby(name_agencias_costo, key=lambda x: x['nameDocument']):
			grupos[key] = list(group)
		return grupos
		agencias_no_disponibles = frappe.db.sql("""
			SELECT
				adm.agencia AS nameBranch
			FROM
				`tabTabla Costo por Agencia` adm
			WHERE
				adm.parent IN """+name_agencias_costo+"""
		""", as_dict=1)

		return agencias_no_disponibles

	return name_agencias_costo

@frappe.whitelist()
def update_zone_employee(branch=None,zone=None):
	values_employee = {
		'branch': branch,
		'status': "Inactive"
	}

	get_employee = frappe.db.sql("""
		SELECT
			br.name,
			br.branch,
			br.zona_nacional
		FROM 
			`tabEmployee` br
		WHERE 
			br.status != %(status)s AND br.branch = %(branch)s
	""", values=values_employee, as_dict=1)

	for employee in get_employee:
		doc = frappe.get_doc('Employee', employee["name"])
		doc.zona_nacional = zone
		doc.save()
		frappe.db.commit()

	return True

@frappe.whitelist()
def search_permission_create(doctype=None, user=None):

	values_employee = {
		'user_id': user
	}

	list_employee = frappe.db.sql("""
		SELECT
			br.name,
			br.branch,
			br.nombre_completo,
			br.department
		FROM 
			`tabEmployee` br
		WHERE 
			br.user_id = %(user_id)s""", values=values_employee, as_dict=1)

	if len(list_employee) > 0:
		if list_employee[0]['department'] == "SSOMA - SE":
			return {
				'status': True,
				'message': 'Acceso Permitido'
			}
		else:
			branch = list_employee[0]['branch']

			values_access = {
				'doctype_ssoma': doctype,
				'parent': branch
			}

			list_access = frappe.db.sql("""
				SELECT
					br.doctype_ssoma,
					br.acceso
				FROM 
					`tabInspeccion SSOMA` br
				WHERE 
					br.doctype_ssoma = %(doctype_ssoma)s AND br.parent = %(parent)s
			""", values=values_access, as_dict=1)

			if len(list_access) == 0:
				return {
					'status': False,
					'message': 'Acceso No Permitido'
				}

			acceso = list_access[0]['acceso']

			if acceso == 0:
				return {
					'status': False,
					'message': 'Acceso No Permitido'
				}
			else:
				return {
					'status': True,
					'message': 'Acceso Permitido'
				}

	else:
		values_role = {
			'parent': user,
			'role': 'Concencionario'
		}

		list_role = frappe.db.sql("""
			SELECT
				br.role
			FROM 
				`tabHas Role` br
			WHERE 
				br.parent = %(parent)s and br.role = %(role)s
		""", values=values_role, as_dict=1)

		if len(list_role) > 0:
			values_permission = {
				'allow': 'Branch',
				'user': user
			}

			list_permission = frappe.db.sql("""
					SELECT
						br.for_value
					FROM 
						`tabUser Permission` br
					WHERE 
						br.allow = %(allow)s and br.user = %(user)s
				""", values=values_permission, as_dict=1)

			if len(list_permission) == 0:
				return {
					'status': False,
					'message': 'Acceso No Permitido'
				}

			branch = list_permission[0]['for_value']

			values_access = {
				'doctype_ssoma': doctype,
				'parent': branch
			}

			list_access = frappe.db.sql("""
				SELECT
					br.doctype_ssoma,
					br.acceso
				FROM 
					`tabInspeccion SSOMA` br
				WHERE 
					br.doctype_ssoma = %(doctype_ssoma)s AND br.parent = %(parent)s
			""", values=values_access, as_dict=1)

			if len(list_access) == 0:
				return {
					'status': False,
					'message': 'Acceso No Permitido'
				}

			acceso = list_access[0]['acceso']

			if acceso == 0:
				return {
					'status': False,
					'message': 'Acceso No Permitido'
				}
			else:
				return {
					'status': True,
					'message': 'Acceso Permitido'
				}

		else:
			return {
				'status': False,
				'message': 'Acceso No Permitido'
			}

@frappe.whitelist()
def restore_inspection(branch=None):
	all_inspections = ['Inspecciones de Extintores','Inspeccion Equipos de Emergencia','Inspeccion de Primeros Auxilios',
					   'Inspeccion  de Orden y Limpieza','Uniformes y Epp','Inspeccion Carritos','Inspeccion de Estocas',
					   'Inspeccion de Estocas','Inspeccion de Montacargas','Inspeccion de Gabinete Contra Incendio',
					   'Inspeccion de Puerta Corrediza Electrica','Inspeccion de Apilador Electrico','Inspeccion del Grupo Electrogeno',
					   'Inspeccion de Apilador Hidraulico Manual']

	name_inspections = {
		'Inspecciones de Extintores': 'Inspecciones de Extintores',
		'Inspeccion Equipos de Emergencia': 'Equipos de emergencia',
		'Inspeccion de Primeros Auxilios': 'Inspeccion de Primeros Auxilios',
		'Inspeccion  de Orden y Limpieza': 'Orden Y Limpieza',
		'Uniformes y Epp': 'Uniformes y EPP',
		'Inspeccion Carritos': 'Inspección de carritos',
		'Inspeccion de Estocas': 'Inspeccion de Estocas',
		'Inspeccion de Apilador Hidraulico Manual': 'Inspección de Apilador Hidráulico Manual',
		'Inspeccion de Montacargas': 'Inspección de Montacargas',
		'Inspeccion de Gabinete Contra Incendio': 'Inspección de Gabinete Contra Fuego',
		'Inspeccion de Puerta Corrediza Electrica': 'Inspección de Puerta Corrediza Electrica',
		'Inspeccion de Apilador Electrico': 'Inspección de Apilador Electrico',
		'Inspeccion del Grupo Electrogeno': 'Inspeccion de Grupo Electrogeno'
	}

	values_table = {
		'parent': branch
	}

	list_table = frappe.db.sql("""
		SELECT
			br.name
		FROM 
			`tabInspeccion SSOMA` br
		WHERE 
			br.parent = %(parent)s
		""", values=values_table, as_dict=1)

	if len(list_table) > 0:
		for item in list_table:
			frappe.db.delete("Inspeccion SSOMA", {
				"name": item['name']
			})

	for inspection in all_inspections:
		new_doc = frappe.new_doc("Inspeccion SSOMA")
		new_doc.parent = branch
		new_doc.parentfield = 'tabla_inspecciones'
		new_doc.parenttype = 'Branch'
		new_doc.acceso = 0
		new_doc.doctype_ssoma = inspection
		new_doc.link_type = 'DocType'
		new_doc.inspeccion_ssoma = name_inspections[inspection]
		new_doc.db_insert()
		if new_doc.name is None:
			return {
				'status': False,
				'message': 'Error al crear, contacte con soporte'
			}

	return {
		'status': True,
		'message': 'Lista de Inspecciones restaurada'
	}

