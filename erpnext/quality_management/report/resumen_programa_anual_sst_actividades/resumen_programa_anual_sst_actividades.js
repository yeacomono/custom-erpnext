// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Resumen Programa Anual SST Actividades"] = {
	"filters": [
		{
			"fieldname":"politics",
			"label": __("Politicas"),
			"fieldtype": "Link",
			"options": "Politicas SSOMA",
			"default": "",
			"width": "100px"
		},
		{
			"fieldname":"mes",
			"label": __("Mes"),
			"fieldtype": "Select",
			"default": "",
			"options": ["","enero", "febrero", "marzo", "abril", "mayo", "junio","julio","agosto","setiembre","octubre","noviembre","diciembre"],
			"width": "100px"
		},
		{
			"fieldname":"fecha",
			"label": __("Fecha"),
			"fieldtype": "Date",
			"options": "Politicas SSOMA",
			"default": "",
			"width": "100px"
		},
		{
			"fieldname":"estado",
			"label": __("Estado"),
			"fieldtype": "Select",
			"default": "",
			"options": ["","Programado", "Ejecutado", "Reprogramado", "En Proceso"],
			"width": "100px"
		},
	],

};
