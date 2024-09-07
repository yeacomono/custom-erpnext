# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _, _dict
from erpnext import get_company_currency, get_default_company
from erpnext.accounts.report.sales_register.sales_register import get_mode_of_payments
import requests
from requests.adapters import HTTPAdapter, Retry

def execute(filters=None):
	if not filters:
		return [], []
	session = requests.Session()
	retry = Retry(connect=3, backoff_factor=0.5)
	adapter = HTTPAdapter(max_retries=retry)
	session.mount('http://', adapter)
	session.mount('https://', adapter)
	terminals_empresarial = session.get("http://moradexx.shalomcontrol.com/query/get_terminals_app_markings_pos")
	terminalJSON = {}
	terminals_empresarial = terminals_empresarial.json()
	for entry in terminals_empresarial:
		terminalJSON[entry['ter_id']] = entry
	validate_filters(filters)

	columns = get_columns(filters)

	group_by_field = get_group_by_field(filters.get("group_by"))
	pos_entries = get_pos_entries(filters, group_by_field, terminalJSON)
	for newkey in pos_entries:
		newkey['sucursal'] = terminalJSON[str(newkey['idsucursal'])]['nombre']
		newkey['tipo_local'] = "CONCESIONARIO" if str(newkey["idsucursal"]) in terminalJSON.keys() and terminalJSON[str(newkey["idsucursal"])]["tipo_local"] == "Concesionario" else "PROPIO"

	if group_by_field != "mode_of_payment":
		concat_mode_of_payments(pos_entries)

	# return only entries if group by is unselected
	if not group_by_field:
		return columns, pos_entries

	# handle grouping
	invoice_map, grouped_data = {}, []
	for d in pos_entries:
		invoice_map.setdefault(d[group_by_field], []).append(d)

	for key in invoice_map:
		invoices = invoice_map[key]
		grouped_data += invoices
		add_subtotal_row(grouped_data, invoices, group_by_field, key)

	# move group by column to first position
	column_index = next((index for (index, d) in enumerate(columns) if d["fieldname"] == group_by_field), None)
	columns.insert(0, columns.pop(column_index))
	return columns, grouped_data

def get_pos_entries(filters, group_by_field, terminalJSON):
	conditions = get_conditions(filters)
	order_by = "p.posting_date"
	select_mop_field, from_sales_invoice_payment, group_by_mop_condition = "", "", ""
	if group_by_field == "mode_of_payment":
		select_mop_field = ", sip.mode_of_payment"
		from_sales_invoice_payment = ", `tabSales Invoice Payment` sip"
		group_by_mop_condition = "sip.parent = p.name AND ifnull(sip.base_amount, 0) != 0 AND"
		order_by += ", sip.mode_of_payment"

	elif group_by_field:
		order_by += ", p.{}".format(group_by_field)

	data_entries = frappe.db.sql(
		"""
		SELECT 
			p.posting_date,p.posting_time, p.name as pos_invoice, p.pos_profile,br.zona_nacional as region,zn.nombre_supervisor as supervisor, pro.branch as sucursal, br.ideentificador as idsucursal,
			br.categoria, us.full_name as owner,us.full_name as owner_name,p.status_comprobante as status_comprobante, p.base_grand_total as grand_total, itm.amount as paid_amount,
			p.customer, p.is_return,p.documento,p.venta_web, itm.description as item, itm.qty as item_q {select_mop_field} , itm.item_group as grupoItem
		FROM
			`tabPOS Invoice Item` itm {from_sales_invoice_payment}
		LEFT JOIN `tabPOS Invoice` p on (itm.parent=p.name)
		LEFT JOIN `tabPOS Profile` pro on (p.pos_profile = pro.name)
		LEFT JOIN `tabBranch` br on (pro.branch = br.name)
		LEFT JOIN `tabZonas Nacional` zn on (br.zona_nacional = zn.name)
		LEFT JOIN tabUser us on( us.name = p.owner )
		WHERE
			p.docstatus != 2 and
			{group_by_mop_condition}
			{conditions}
		ORDER BY
			{order_by}
		""".format(
			select_mop_field=select_mop_field,
			from_sales_invoice_payment=from_sales_invoice_payment,
			group_by_mop_condition=group_by_mop_condition,
			conditions=conditions,
			order_by=order_by
		), filters, as_dict=1)
	data = []
	for entry in data_entries:
		data.append({
			"posting_date": entry.posting_date,
			"posting_time": entry.posting_time,
			"pos_invoice": entry.pos_invoice,
			"pos_profile": entry.pos_profile,
			"region": entry.region,
			"supervisor": entry.supervisor,
			"sucursal": entry.sucursal,
			"idsucursal": entry.idsucursal,
			"categoria": entry.categoria,
			"owner": entry.owner,
			"owner_name": entry.owner_name,
			"status_comprobante": ("FACTURA" if entry.documento and len(entry.documento) == 11 else "BOLETA") if entry.status_comprobante != "Liquidaciones" else "FACTURA",
			"grand_total": entry.grand_total,
			"paid_amount": entry.paid_amount,
			"customer": entry.customer,
			"is_return": entry.is_return,
			"item": entry.item,
			"item_group": entry.grupoItem,
			"item_q": entry.item_q,
			"venta_web": entry.venta_web,
			"type_payment": (entry.status_comprobante if entry.status_comprobante in ["Pago por PINPAD","QR","Planilla","Link"] else "CONTADO") if entry.status_comprobante != "Liquidaciones" else "LIQUIDACIONES",
		})

	return data

def concat_mode_of_payments(pos_entries):
	mode_of_payments = get_mode_of_payments(set(d["pos_invoice"] for d in pos_entries))
	for entry in pos_entries:
		if mode_of_payments.get(entry["pos_invoice"]):
			entry["mode_of_payment"] = ", ".join(mode_of_payments.get(entry["pos_invoice"], []))

def add_subtotal_row(data, group_invoices, group_by_field, group_by_value):
	grand_total = sum(d["grand_total"] for d in group_invoices)
	paid_amount = sum(d["paid_amount"] for d in group_invoices)
	data.append({
		group_by_field: group_by_value,
		"grand_total": grand_total,
		"paid_amount": paid_amount,
		"bold": 1
	})
	data.append({})

def validate_filters(filters):
	# if not filters.get("company"):
	# 	frappe.throw(_("{0} is mandatory").format(_("Company")))

	if not filters.get("from_date") and not filters.get("to_date"):
		frappe.throw(_("{0} and {1} are mandatory").format(frappe.bold(_("From Date")), frappe.bold(_("To Date"))))

	if filters.from_date > filters.to_date:
		frappe.throw(_("From Date must be before To Date"))

	if (filters.get("pos_profile") and filters.get("group_by") == _('POS Profile')):
		frappe.throw(_("Can not filter based on POS Profile, if grouped by POS Profile"))

	if (filters.get("customer") and filters.get("group_by") == _('Customer')):
		frappe.throw(_("Can not filter based on Customer, if grouped by Customer"))

	if (filters.get("owner") and filters.get("group_by") == _('Cashier')):
		frappe.throw(_("Can not filter based on Cashier, if grouped by Cashier"))

	if (filters.get("mode_of_payment") and filters.get("group_by") == _('Payment Method')):
		frappe.throw(_("Can not filter based on Payment Method, if grouped by Payment Method"))

def get_conditions(filters):
	conditions = "posting_date >= %(from_date)s AND posting_date <= %(to_date)s"

	if filters.get("pos_profile"):
		conditions += " AND pos_profile = %(pos_profile)s"

	if filters.get("status_comprobante"):
		if  filters.get("status_comprobante") == "Boleta":
			conditions += " AND LENGTH(documento) < 11 "
		else:
			conditions += " AND LENGTH(documento) = 11 "

	if filters.get("owner"):
		conditions += " AND owner = %(owner)s"

	if filters.get("customer"):
		conditions += " AND customer = %(customer)s"

	if filters.get("is_return"):
		conditions += " AND is_return = %(is_return)s"

	if filters.get("type_payment"):
		if filters.get("type_payment") in  ["Link", "Pago por PINPAD", "QR","Planilla","Liquidaciones","Venta Web"]:
			if filters.get("type_payment") == "Venta Web":
				conditions += " AND p.venta_web = 1 "
			else:
				conditions += " AND status_comprobante = %(type_payment)s"
		else:
			conditions += " AND status_comprobante NOT IN ('Link', 'Pago por PINPAD', 'QR','Planilla','Liquidaciones')"

	if filters.get("mode_of_payment"):
		conditions += """
			AND EXISTS(
					SELECT name FROM `tabSales Invoice Payment` sip
					WHERE parent=p.name AND ifnull(sip.mode_of_payment, '') = %(mode_of_payment)s
				)"""

	return conditions

def get_group_by_field(group_by):
	group_by_field = ""

	if group_by == "POS Profile":
		group_by_field = "pos_profile"
	elif group_by == "Cashier":
		group_by_field = "owner"
	elif group_by == "Customer":
		group_by_field = "customer"
	elif group_by == "Payment Method":
		group_by_field = "mode_of_payment"

	return group_by_field

def get_columns(filters):
	columns = [
		{
			"label": _("Posting Date"),
			"fieldname": "posting_date",
			"fieldtype": "Date",
			"width": 90
		},
		{
			"label": _("POS Invoice"),
			"fieldname": "pos_invoice",
			"fieldtype": "Link",
			"options": "POS Invoice",
			"width": 120
		},
		# {
		# 	"label": _("Customer"),
		# 	"fieldname": "customer",
		# 	"fieldtype": "Link",
		# 	"options": "Customer",
		# 	"width": 120
		# },
		{
			"label": _("POS Profile"),
			"fieldname": "pos_profile",
			"fieldtype": "Link",
			"options": "POS Profile",
			"width": 160
		},
		{
			"label": _("Sucursal"),
			"fieldname": "sucursal",
			"fieldtype": "Data",
			"width": 160
		},
		{
			"label": _("Id de la terminal"),
			"fieldname": "idsucursal",
			"fieldtype": "Data",
			"width": 100
		},
		{
			"label": _("Cashier"),
			"fieldname": "owner",
			"fieldtype": "Link",
			"options": "User",
			"width": 140
		},
		{
			"label": _("Paid Amount"),
			"fieldname": "paid_amount",
			"fieldtype": "Currency",
			"options": "company:currency",
			"width": 120
		},
		# {
		# 	"label": _("Payment Method"),
		# 	"fieldname": "mode_of_payment",
		# 	"fieldtype": "Data",
		# 	"width": 150
		# },
		# {
		# 	"label": _("Nombre Completo"),
		# 	"fieldname": "owner_name",
		# 	"fieldtype": "Data",
		# 	"width": 200
		# },
		{
			"label": _("Tipo Comprobante"),
			"fieldname": "status_comprobante",
			"fieldtype": "Data",
			"width": 150
		},
		{
			"label": _("Posting Time"),
			"fieldname": "posting_time",
			"fieldtype": "Time",
			"width": 90
		},
		{
			"label": _("Region"),
			"fieldname": "region",
			"fieldtype": "Data",
			"width": 160
		},
		{
			"label": _("Categoria"),
			"fieldname": "categoria",
			"fieldtype": "Data",
			"width": 100
		},
		{
			"label": _("Tipo de agencia"),
			"fieldname": "tipo_local",
			"fieldtype": "Data",
			"width": 100
		},
		{
			"label": _("Producto vendido"),
			"fieldname": "item",
			"fieldtype": "Data",
			"width": 150
		},
		{
			"label": _("Grupo de Productos"),
			"fieldname": "item_group",
			"fieldtype": "Data",
			"width": 150
		},
		{
			"label": _("Cantidad de Productos"),
			"fieldname": "item_q",
			"fieldtype": "Data",
			"width": 150
		},
		{
			"label": _("Forma de pago"),
			"fieldname": "type_payment",
			"fieldtype": "Data",
			"width": 150
		},
		{
			"label": _("Supervisor Region"),
			"fieldname": "supervisor",
			"fieldtype": "Data",
			"width": 160
		},
	]

	return columns

@frappe.whitelist(allow_guest=True)
def report_pos_register(filters=None):
	if not filters: filters = {}

	from_date = filters.get('from_date')
	to_date = filters.get('to_date')

	if not filters:
		return [], []
	session = requests.Session()
	retry = Retry(connect=3, backoff_factor=0.5)
	adapter = HTTPAdapter(max_retries=retry)
	session.mount('http://', adapter)
	session.mount('https://', adapter)
	terminals_empresarial = session.get("http://moradexx.shalomcontrol.com/query/get_terminals_app_markings_pos")
	terminalJSON = {}
	terminals_empresarial = terminals_empresarial.json()
	for entry in terminals_empresarial:
		terminalJSON[entry['ter_id']] = entry

	pos_entries = get_pos_entries(filters, "", terminalJSON)

	for newkey in pos_entries:
		newkey['sucursal'] = terminalJSON[str(newkey['idsucursal'])]['nombre']
		newkey['tipo_local'] = "CONCESIONARIO" if str(newkey["idsucursal"]) in terminalJSON.keys() and terminalJSON[str(newkey["idsucursal"])]["tipo_local"] == "Concesionario" else "PROPIO"

	return [pos_entries]

