from frappe.utils.pdf import get_pdf
import frappe
import pdfkit
import jinja2
import os
from frappe.utils import getdate, nowdate, cstr, get_datetime, formatdate
from datetime import datetime, date, timedelta
import calendar
from itertools import groupby
from operator import itemgetter
import copy
import requests
import numpy as np
import json
from frappe.utils.nestedset import get_root_of
from erpnext.accounts.doctype.pos_profile.pos_profile import get_item_groups
from erpnext.accounts.doctype.pos_invoice.pos_invoice import get_stock_availability
from frappe.model.document import Document
from dateutil.relativedelta import relativedelta

import pandas as pd


@frappe.whitelist(allow_guest=True)
def create_supervision_quarterly():
    month_json = {1:"Enero",2:"Febrero",3:"Marzo",4:"Abril",5:"Mayo",6:"Junio",7:"Julio",8:"Agosto",9:"Setiembre",10:"Octubre",11:"Noviembre",12:"Diciembre"}
    month_to_create = ["Enero","Abril","Julio","Octubre"]
    current_month = datetime.date.today().month
    current_day = datetime.date.today().day
    date_now = datetime.date.today()

    if current_day != 1:
        return {
            'status': False,
            'message': 'No es primero del Mes'
        }

    if month_json[int(current_month)] not in month_to_create:
        return {
            'status': False,
            'message': 'El mes no esta dentro del trimestre'
        }

    array_supervision_table = [
        {
            "supervision": "Arqueo de Caja",
            "parentfield": 'tabla_supervisores',
            "parenttype": "Programacion de Supervisores"
        },
        {
            "supervision": "Check List Para Vehiculos",
            "parentfield": "tabla_supervisores",
            "parenttype": "Programacion de Supervisores"
        },
        {
            "supervision": "Check List Sucursal",
            "parentfield": "tabla_supervisores",
            "parenttype": "Programacion de Supervisores"
        },
        {
            "supervision": "Control de Lineas Moviles",
            "parentfield": "tabla_supervisores",
            "parenttype": "Programacion de Supervisores"
        },
        {
            "supervision": "Formato EPPs",
            "parentfield": "tabla_supervisores",
            "parenttype": "Programacion de Supervisores"
        }
    ]

    values_branch = {
        'estado_de_sucursal': 1,
        'fecha': date_now,
        'es_programacion_trimestral': 1
    }

    get_branch = frappe.db.sql("""
		SELECT
			br.name,
			br.estado_de_sucursal,
			br.supervisor,
			br.zona_nacional
		FROM
			`tabBranch` as br
		WHERE
			br.estado_de_sucursal = %(estado_de_sucursal)s and br.supervisor IS NOT NULL and
			br.zona_nacional IS NOT NULL and br.zona_nacional != '-'
	""", values=values_branch, as_dict=True)

    json_branch_id = [branch_id["name"] for branch_id in get_branch]

    values_program = {
        'fecha': date_now,
        'es_programacion_trimestral': 1,
        'sucursal': json_branch_id
    }

    get_program = frappe.db.sql("""
		SELECT
			ps.name,
			ps.fecha,
			ps.es_programacion_trimestral,
			ps.sucursal
		FROM
			`tabProgramacion de Supervisores` as ps
		WHERE
			ps.fecha = %(fecha)s and ps.es_programacion_trimestral = %(es_programacion_trimestral)s
			and ps.sucursal IN %(sucursal)s
	""", values=values_program, as_dict=True)


    json_branch = {}
    json_program = {}

    for item_branch in get_branch:
        key = item_branch["name"]
        json_branch[key] = item_branch

    for item_program in get_program:
        key = item_program["sucursal"]
        json_program[key] = item_program

    branch_to_create = []

    for key, object in json_branch.items():
        if key not in json_program:
            branch_to_create.append(object)

    if len(branch_to_create) == 0:
        return {
            'status': True,
            'message': 'Las Programaciones Trimestrales ya fueron creadas'
        }

    i = 1

    for branch in branch_to_create:
        new_doc = frappe.new_doc("Programacion de Supervisores")
        new_doc.fecha = date_now
        new_doc.sucursal = branch["name"]
        new_doc.prog_supervisores = "Programado"
        new_doc.supervisor = branch["supervisor"]
        new_doc.es_programacion_trimestral = 1
        for item in array_supervision_table:
            new_doc.append('tabla_supervisores', {
                'supervision': item["supervision"],
                'parentfield': item["parentfield"],
                'parenttype': item["parenttype"]
            })
        new_doc.insert(ignore_permissions=True,ignore_mandatory=True)
        frappe.db.commit()
        i += 1
    # if i == 70:
    # 	break

    return {
        'status': True,
        'message': 'Se Crearon las Programaciones Trimestrales'
    }


@frappe.whitelist(allow_guest=True)
def insert_marking_employee():

    dataSend = frappe.form_dict.sendData
    values = json.loads(dataSend)

    sql_insert_query = f"""
        INSERT INTO `tabEmployee Checkin` (
        `name`, 
        `employee`, 
        `urlimagen`, 
        `log_type`, 
        `time` ,
        `coordenadas` ,
        `urlimagen2`, 
        `fecha_de_consolidado`, 
        `sucursal`, 
        `employee_name`, 
        `departamento`,
        `creation`,
        `modified`,
        `offline`,
        `late_time`,
        `overtime_time`
        )
        VALUES (
        '{values.get("name")}', 
        '{values.get("employee")}', 
        '{values.get("urlimagen")}',
        '{values.get("log_type")}',
        '{values.get("time")}',
        '{values.get("coordenadas")}',
        '{values.get("urlimagen2")}',
        '{values.get("fecha_de_consolidado")}',
        '{values.get("sucursal")}',
        '{values.get("employee_name")}',
        '{values.get("departamento")}',
        '{values.get("creation")}',
        '{values.get("modified")}',
        '{values.get("offline")}',
        '{values.get("late_time")}',
        '{values.get("overtime_time")}'
        )
    """

    responseData = dict()

    try:

        data = frappe.db.sql(sql_insert_query)
        frappe.db.commit()
        responseData["data"] = data
        responseData["msn"] = "Exito"
        responseData["status"] = True

    except Exception as e:

        responseData["msn"] = e
        responseData["status"] = False

    frappe.response['response'] =  responseData


@frappe.whitelist(allow_guest=True)
def insert_doctype():
    data = frappe.form_dict.sendData
    doctype = frappe.form_dict.doctype
    dataSend = json.loads(data)

    columns = ", ".join([f"`{key}`" for key in dataSend.keys()])
    placeholders = ", ".join([f"%({key})s" for key in dataSend.keys()])
    sql = f"""INSERT INTO `{doctype}` ({columns}) VALUES ({placeholders})"""

    responseData = dict()

    try:

        data = frappe.db.sql(sql, values=dataSend)
        frappe.db.commit()
        responseData["msn"] = "Exito"
        responseData["status"] = True

    except Exception as e:

        responseData["msn"] = e
        responseData["status"] = False

    frappe.response['response'] =  responseData


@frappe.whitelist(allow_guest=True)
def update_massive_register():

    json_data = frappe.local.form_dict
    registros = frappe.get_all(json_data["doctype"], filters={"branch": json_data["branch"]})
    for registro in registros:
        doc = frappe.get_doc(json_data["doctype"], registro.name)
        doc.categoria_sucursal = json_data["categoria"]
        doc.save()

    return "Se actualizaron los empleados"

@frappe.whitelist()
def get_items_test():
    start = 0
    page_length = 40
    price_list = "Venta estándar"
    item_group = "Todos los grupos de artículos"
    search_term = ""
    pos_profile = "JAUJA"
    packaging = "false"
    warehouse, hide_unavailable_items = frappe.db.get_value(
        'POS Profile', pos_profile, ['warehouse', 'hide_unavailable_items'])

    lft, rgt = frappe.db.get_value('Item Group', item_group, ['lft', 'rgt'])
    condition = get_conditions(search_term)
    condition += get_item_group_condition(pos_profile)
    bin_join_selection, bin_join_condition, packaging_condition = "", "", ""


    items_data = frappe.db.sql("""
		SELECT
			item.name AS item_code,
			item.item_name,
			item.description,
			item.stock_uom,
			item.image AS item_image,
			item.embalaje AS item_embalaje,
			substring(item.item_code,1,6) AS substring_embalaje,
			item.is_stock_item,
			item.posicion
		FROM
			`tabItem` item {bin_join_selection}
		WHERE
			item.disabled = 0
			AND item.has_variants = 0
			AND item.is_sales_item = 1
			AND item.is_fixed_asset = 0
			AND substring(item.item_code,1,6) != 'SEREMB'
			AND item.item_group in (SELECT name FROM `tabItem Group` WHERE lft >= {lft} AND rgt <= {rgt})
			AND {condition}
			{bin_join_condition}
		ORDER BY
			item.name asc
		LIMIT
				{start}, {page_length}"""
        .format(
        start=start,
        page_length=page_length,
        lft=lft,
        rgt=rgt,
        condition=condition,
        bin_join_selection=bin_join_selection,
        bin_join_condition=bin_join_condition
    ), {'warehouse': warehouse}, as_dict=1)

    return items_data


@frappe.whitelist()
def get_report():

    productos = [
        {
            "descripcion":"PRUEBA",
            "importe":15,
            "precioUnitario":15,
            "cantidad":1
        }
    ]

    datos = {
        "tipoComprobante":'boleta',
        "entidadPaga":"75013406",
        "razonSocial": "GIAN PIERO VILLANUEVA GASTELLO",
        "productos":productos,
        "cdn": "ACC-PSINV-2023-00003",
        "userDni":'70503353',
        "medio_pago": 'CONTADO'
    }

    response = requests.post('https://fileserver.shalomcontrol.com/api/registrar-comprobante-erp', data=datos)

    return response


@frappe.whitelist()
def search_for_serial_or_batch_or_barcode_number(search_value):
    # search barcode no
    barcode_data = frappe.db.get_value('Item Barcode', {'barcode': search_value}, ['barcode', 'parent as item_code'], as_dict=True)
    if barcode_data:
        return barcode_data

    # search serial no
    serial_no_data = frappe.db.get_value('Serial No', search_value, ['name as serial_no', 'item_code'], as_dict=True)
    if serial_no_data:
        return serial_no_data

    # search batch no
    batch_no_data = frappe.db.get_value('Batch', search_value, ['name as batch_no', 'item as item_code'], as_dict=True)
    if batch_no_data:
        return batch_no_data

    return {}

@frappe.whitelist()
def search_by_term(search_term, warehouse, price_list):
    result = search_for_serial_or_batch_or_barcode_number(search_term) or {}

    item_code = result.get("item_code") or search_term
    serial_no = result.get("serial_no") or ""
    batch_no = result.get("batch_no") or ""
    barcode = result.get("barcode") or ""

    if result:
        item_info = frappe.db.get_value("Item", item_code,
                                        ["name as item_code", "item_name", "description", "stock_uom", "image as item_image", "is_stock_item"],
                                        as_dict=1)

        item_stock_qty = get_stock_availability(item_code, warehouse)
        price_list_rate, currency = frappe.db.get_value('Item Price', {
            'price_list': price_list,
            'item_code': item_code
        }, ["price_list_rate", "currency"]) or [None, None]

        item_info.update({
            'serial_no': serial_no,
            'batch_no': batch_no,
            'barcode': barcode,
            'price_list_rate': price_list_rate,
            'currency': currency,
            'actual_qty': item_stock_qty
        })

        return {'items': [item_info]}

@frappe.whitelist()
def get_conditions(search_term):
    condition = "("
    condition += """item.name like {search_term}
		or item.item_name like {search_term}""".format(search_term=frappe.db.escape('%' + search_term + '%'))
    condition += add_search_fields_condition(search_term)
    condition += ")"

    return condition

@frappe.whitelist()
def add_search_fields_condition(search_term):
    condition = ''
    search_fields = frappe.get_all('POS Search Fields', fields = ['fieldname'])
    if search_fields:
        for field in search_fields:
            condition += " or item.`{0}` like {1}".format(field['fieldname'], frappe.db.escape('%' + search_term + '%'))
    return condition

@frappe.whitelist()
def get_item_group_condition(pos_profile):
    cond = "and 1=1"
    item_groups = get_item_groups(pos_profile)
    if item_groups:
        cond = "and item.item_group in (%s)"%(', '.join(['%s']*len(item_groups)))

    return cond % tuple(item_groups)

@frappe.whitelist()
def filter_service_items(items):
    for item in items:
        if not item['is_stock_item']:
            if not frappe.db.exists('Product Bundle', item['item_code']):
                items.remove(item)

    return items

@frappe.whitelist()
def get_items():

    start = 0
    page_length = 40
    price_list = "Venta estándar"
    item_group = "Todos los grupos de artículos"
    pos_profile = "JAUJA"
    packaging = "true"
    search_term = ""

    warehouse, hide_unavailable_items = frappe.db.get_value(
        'POS Profile', pos_profile, ['warehouse', 'hide_unavailable_items'])

    result = []

    if search_term:
        result = search_by_term(search_term, warehouse, price_list) or []
        if result:
            return result

    if not frappe.db.exists('Item Group', item_group):
        item_group = get_root_of('Item Group')

    condition = get_conditions(search_term)
    condition += get_item_group_condition(pos_profile)

    lft, rgt = frappe.db.get_value('Item Group', item_group, ['lft', 'rgt'])

    bin_join_selection, bin_join_condition, packaging_condition = "", "", ""
    if hide_unavailable_items:
        bin_join_selection = ", `tabBin` bin"
        bin_join_condition = "AND bin.warehouse = %(warehouse)s AND bin.item_code = item.name AND bin.actual_qty > 0 "
    if packaging == "true":
        items_data = frappe.db.sql("""
		SELECT
			item.name AS item_code,
			item.item_name,
			item.description,
			item.stock_uom,
			item.image AS item_image,
			item.embalaje AS item_embalaje,
			substring(item.item_code,1,6) AS substring_embalaje,
			item.is_stock_item
		FROM
			`tabItem` item
		WHERE
			substring(item.item_code,1,6) = 'SEREMB'
		"""
                                   , {'warehouse': warehouse}, as_dict=1)
    else:
        items_data = frappe.db.sql("""
		SELECT
			item.name AS item_code,
			item.item_name,
			item.description,
			item.stock_uom,
			item.image AS item_image,
			item.embalaje AS item_embalaje,
			substring(item.item_code,1,6) AS substring_embalaje,
			item.is_stock_item
		FROM
			`tabItem` item {bin_join_selection}
		WHERE
			item.disabled = 0
			AND item.has_variants = 0
			AND item.is_sales_item = 1
			AND item.is_fixed_asset = 0
			AND substring(item.item_code,1,6) != 'SEREMB'
			AND item.item_group in (SELECT name FROM `tabItem Group` WHERE lft >= {lft} AND rgt <= {rgt})
			AND {condition}
			{bin_join_condition}
		ORDER BY
			item.name asc
		LIMIT
				{start}, {page_length}"""
            .format(
            start=start,
            page_length=page_length,
            lft=lft,
            rgt=rgt,
            condition=condition,
            bin_join_selection=bin_join_selection,
            bin_join_condition=bin_join_condition
        ), {'warehouse': warehouse}, as_dict=1)

    if items_data:
        items_data = filter_service_items(items_data)
        items = [d.item_code for d in items_data]
        item_prices_data = frappe.get_all("Item Price",
                                          fields = ["item_code", "price_list_rate", "currency"],
                                          filters = {'price_list': price_list, 'item_code': ['in', items]})

        item_prices = {}
        for d in item_prices_data:
            item_prices[d.item_code] = d

        for item in items_data:
            item_code = item.item_code
            item_price = item_prices.get(item_code) or {}
            item_stock_qty = get_stock_availability(item_code, warehouse)

            row = {}
            row.update(item)
            row.update({
                'price_list_rate': item_price.get('price_list_rate'),
                'currency': item_price.get('currency'),
                'actual_qty': item_stock_qty,
            })
            result.append(row)

    sorted_data = sorted(result, key=lambda x: x["price_list_rate"])

    return {'items': sorted_data}

@frappe.whitelist()
def download_excel_attendance(head=[], only_data=[], month="", year=""):
    from frappe.utils.xlsxutils import build_xlsx_response

    data_head = [head]
    data_values = only_data
    data = data_head + data_values

    title = "Asistencia "+month+" "+year
    build_xlsx_response(data, title)

@frappe.whitelist(allow_guest=True)
def excel_attendance_cloud(year=None, month=None):
    import calendar
    import datetime
    myobj = {'month': month}
    cortes = requests.post("https://recursoshumanos.shalom.com.pe/api/courts-month", json = myobj)
    cortes = cortes.json()
    cortes = cortes.get("data")
    terminals_empresarial = requests.get("http://moradexx.shalomcontrol.com/query/get_terminals_app_markings")
    terminalJSON = {}
    terminals_empresarial = terminals_empresarial.json()
    for entry in terminals_empresarial:
        terminalJSON[entry['ter_id']] = entry

    branches = frappe.get_all("Branch", fields=['name', 'ideentificador'] , filters=[], as_list=False)
    branchesJSON = {}
    for branch in branches:
        branchesJSON[branch['name']] = str(branch["ideentificador"])
    month_map = get_month_map()
    month_str = str(month_map[month]).zfill(2)
    find_day_now = date.today()

    my_day_now = find_day_now.strftime("%Y-%m-%d")

    # Para fechas de este año
    # today = get_datetime()

    # Para fechas de otros años
    today = datetime.datetime.strptime(year+'-'+month_str+'-'+'01', "%Y-%m-%d")
    nxt_mnth = today.replace(day=28) + datetime.timedelta(days=4)
    res = nxt_mnth - datetime.timedelta(days=nxt_mnth.day)
    last_day = datetime.datetime.strptime(year+'-'+month_str+'-'+str(res.day), "%Y-%m-%d")

    final_range = calendar.monthrange(today.year, month_map[month])[1] + 1
    final_day_month = calendar.monthrange(today.year, month_map[month])[1]
    start_day_month = 1

    dates_of_month = ['{}-{}-{}'.format(today.year, month_str, r) for r in range(1, final_range)]

    array_heads_dates = []
    for day in range(1, final_range):
        daystr = str(day).zfill(2)
        timestamp = datetime.datetime.strptime(year+'-'+month_str+'-'+daystr, "%Y-%m-%d").timestamp()
        date_from_time = datetime.date.fromtimestamp(timestamp)
        d = date_from_time.strftime('%d-%b')
        array_heads_dates.append(d)

    array_head_employee = ["Codigo", "Nombre Completo", "Terminal", "Departamento", "Empresa","Calificación","Tipo Documento","N° Documento","Fecha de Ingreso Real","Fecha de Relevo","Zona","Estado"]

    final_head = array_head_employee + array_heads_dates + ["Id Sucursal"]

    length = len(dates_of_month)
    month_start, month_end = dates_of_month[0], dates_of_month[length-1]

    dates_push = []
    for k in range(start_day_month, final_day_month + 1):
        my_day = str(k).zfill(2)
        dates_push.append(year+'-'+month_str+'-'+my_day)

    holiday_sundays_list = holiday_sundays_dates()
    holiday_this_month = []
    holiday_this_month_holidays = []
    date_start_split = month_start.split('-')
    date_start_validate = date_start_split[0]+"-"+date_start_split[1]+"-0"+date_start_split[2]
    # date_start_time = datetime(int(date_start_split[0]),int(date_start_split[1]),int(date_start_split[2]))
    for this_month_holiday in holiday_sundays_list["domingos"]:
        str_holiday = str(this_month_holiday)
        if check_in_range(str_holiday, month_start, month_end):
            holiday_this_month.append(str_holiday)

    for this_month_holiday_holidays in holiday_sundays_list["feriados"]:
        str_holiday = str(this_month_holiday_holidays)
        if check_in_range(str_holiday, month_start, month_end):
            holiday_this_month_holidays.append(str_holiday)

    # doc_employees = frappe.db.get_list('Employee', fields=["name", "employee_name", "nombre_completo", "company", "branch", "department", "fecha_de_ingreso_real", "fecha_de_relevo", "status","calificacion_trabajador","place_of_issue","passport_number","zona_recursos"], as_list=False)
    doc_employees = frappe.db.sql("""
        SELECT
            emp.name, emp.employee_name, emp.nombre_completo, emp.company,
            emp.branch, emp.department, emp.fecha_de_ingreso_real, emp.fecha_de_relevo,
            emp.status, emp.calificacion_trabajador, emp.place_of_issue, emp.passport_number,
            br.zona_recursos_humanos as zona_recursos
        FROM `tabEmployee` emp
        LEFT JOIN `tabBranch` br on emp.branch = br.name
        ORDER BY name asc
    """, values={}, as_dict=1)
    json_employee = dict()
    for employee in doc_employees:
        if "PRUEBA" in employee["employee_name"]:
            continue
        if employee["status"] == "Active" and employee["branch"] != "No especificado":
            json_employee[employee["name"]] = employee
        elif  employee["branch"] != "No especificado" and str(employee["fecha_de_relevo"])>=date_start_validate and str(employee["fecha_de_relevo"])<=month_end :
            json_employee[employee["name"]] = employee
        elif employee["fecha_de_relevo"] is None and (employee["status"] == "Active" or employee["status"]== "No Reportado"):
            json_employee[employee["name"]] = employee
    # values = {'start_date': month_start, 'end_date': month_end}
    # doc_attendances = frappe.db.sql(f"""SELECT employee, employee_name, attendance_date, status, leave_type FROM `tabAttendance` where company='Shalom Empresarial' AND branch!='No especificado' AND docstatus != '2' AND attendance_date >= %(start_date)s AND attendance_date <= %(end_date)s order by attendance_date asc; """, values=values, as_dict=True)
    doc_attendances = frappe.get_all("Attendance", fields=['employee', 'employee_name', 'company', 'attendance_date', 'status','estado_reporte', 'leave_type','docstatus'] , filters=[
        ["attendance_date", ">=", month_start],
        ["attendance_date", "<=", month_end],
        ["branch", "!=", "No especificado"],
        ["docstatus", "!=", 2]
    ], order_by='attendance_date asc', as_list=False)

    groups_attendance_by_employee = dict()
    doc_attendances_copy = []
    new_group = {}

    for val_attendance in doc_attendances:
        key_employee = val_attendance["employee"]
        if key_employee in json_employee:
            doc_attendances_copy.append(val_attendance)

    for key, value in groupby(doc_attendances_copy, key = itemgetter('employee')):
        for k in value:
            new_group[k["employee"]] = [k] if k["employee"] not in new_group.keys() else new_group[k["employee"]] + [k]

    copy_new_group = copy.copy(new_group)
    keys_group_employee_attendance = new_group.keys()
    key_employee = json_employee.keys()

    for key2, val_group in new_group.items():
        for val_employee in key_employee:
            if val_employee != key2:
                if val_employee not in keys_group_employee_attendance:
                    copy_new_group[val_employee] = []

    employe_list_final_group = []
    for hr_emp, val_hr in copy_new_group.items():
        group_final = []
        for r in range(start_day_month, final_day_month + 1):
            result_search = search_for_date(dates_push[r - 1], val_hr)
            count_list_hr = len(val_hr)
            if result_search[1]:
                stat = ""
                dayInit = result_search[0]["status"] if dates_push[r - 1] in cortes and result_search[0]["status"] != "" and result_search[0]["status"] is not None else result_search[0]["status"]
                if result_search[0]["docstatus"] == 1:
                    if dayInit == "On Leave":
                        if result_search[0]["leave_type"] == "VACACIONES":
                            stat = "VAC"
                        if result_search[0]["leave_type"] == "LICENCIA SIN GOCE":
                            stat = "LSG"
                        if result_search[0]["leave_type"] == "COMPENSATORIO":
                            stat = "COM"
                        if result_search[0]["leave_type"] == "LICENCIA CON GOCE":
                            stat = "LCG"
                        if result_search[0]["leave_type"] == "DESCANSO MEDICO":
                            stat = "DME"
                        if result_search[0]["leave_type"] == "PERMISO OCACIONAL":
                            stat = "L-PO"
                        if result_search[0]["leave_type"] == "SUBSIDIO":
                            stat = "LS"
                        if result_search[0]["leave_type"] == "SUBSIDIO POR ENFERMEDAD":
                            stat = "SXE"
                        if result_search[0]["leave_type"] == "SUBSIDIO POR MATERNIDAD":
                            stat = "SXM"
                        if result_search[0]["leave_type"] == "SUBSIDIO POR ACCIDENTE":
                            stat = "SXA"
                        if result_search[0]["leave_type"] == "LICENCIA POR FALLECIMIENTO":
                            stat = "LXF"
                        if result_search[0]["leave_type"] == "LICENCIA POR PATERNIDAD":
                            stat = "LXP"
                    if dayInit == "Present":
                        stat = "P"
                    if dayInit == "Absent":
                        stat = "A"
                    if dayInit == "Half Day":
                        stat = "HD"
                    if dayInit == "Work From Home" or dayInit == "Marcacion Incompleta":
                        stat = "MI"
                    result_search[0]["terminal"] = json_employee[hr_emp]["branch"]
                    result_search[0]["department"] = json_employee[hr_emp]["department"]
                    result_search[0]["company"] = json_employee[hr_emp]["company"]
                    result_search[0]["nombre_completo"] = json_employee[hr_emp]["nombre_completo"]
                    result_search[0]["fecha_de_ingreso_real"] = json_employee[hr_emp]["fecha_de_ingreso_real"]
                    result_search[0]["fecha_de_relevo"] = json_employee[hr_emp]["fecha_de_relevo"]
                    result_search[0]["status"] = stat
                    result_search[0]["status_employee"] = "".join(json_employee[hr_emp]["status"])
                    result_search[0]["calificacion_trabajador"]="".join(json_employee[hr_emp]["calificacion_trabajador"])
                    result_search[0]["place_of_issue"]= json_employee[hr_emp]["place_of_issue"]
                    result_search[0]["passport_number"]="".join(json_employee[hr_emp]["passport_number"])
                    result_search[0]["zona_recursos"]=json_employee[hr_emp]["zona_recursos"]
                    group_final.append(result_search[0])
                elif result_search[0]["docstatus"] == 0:
                    stat = "NV"
                    result_search[0]["terminal"] = json_employee[hr_emp]["branch"]
                    result_search[0]["department"] = json_employee[hr_emp]["department"]
                    result_search[0]["company"] = json_employee[hr_emp]["company"]
                    result_search[0]["nombre_completo"] = json_employee[hr_emp]["nombre_completo"]
                    result_search[0]["fecha_de_ingreso_real"] = json_employee[hr_emp]["fecha_de_ingreso_real"]
                    result_search[0]["fecha_de_relevo"] = json_employee[hr_emp]["fecha_de_relevo"]
                    result_search[0]["status"] = stat
                    result_search[0]["status_employee"] = "".join(json_employee[hr_emp]["status"])
                    result_search[0]["calificacion_trabajador"]="".join(json_employee[hr_emp]["calificacion_trabajador"])
                    result_search[0]["place_of_issue"]= json_employee[hr_emp]["place_of_issue"]
                    result_search[0]["passport_number"]="".join(json_employee[hr_emp]["passport_number"])
                    result_search[0]["zona_recursos"]=json_employee[hr_emp]["zona_recursos"]
                    group_final.append(result_search[0])
            else:
                if str(json_employee[hr_emp]["fecha_de_ingreso_real"]) <= dates_push[r - 1]:
                    if json_employee[hr_emp]["status"] == 'Active':
                        if json_employee[hr_emp]["fecha_de_relevo"] is None:
                            if dates_push[r - 1] in holiday_this_month:
                                status_hr = "WO"
                            elif dates_push[r - 1] in holiday_this_month_holidays:
                                status_hr = "*H*"
                            else:
                                status_hr = "NM"
                        else:
                            if str(json_employee[hr_emp]["fecha_de_relevo"]) < dates_push[r - 1]:
                                status_hr = "C"
                            else:
                                if dates_push[r - 1] in holiday_this_month:
                                    status_hr = "WO"
                                elif dates_push[r - 1] in holiday_this_month_holidays:
                                    status_hr = "*H*"
                                else:
                                    status_hr = "NM"
                    else:
                        if str(json_employee[hr_emp]["fecha_de_relevo"]) < dates_push[r - 1]:
                            status_hr = "C"
                        else:
                            if dates_push[r - 1] in holiday_this_month:
                                status_hr = "WO"
                            elif dates_push[r - 1] in holiday_this_month_holidays:
                                status_hr = "*H*"
                            else:
                                status_hr = "NM"
                else:
                    status_hr = "C"

                not_mark = {
                    "employee": hr_emp,
                    "employee_name": json_employee[hr_emp]["employee_name"],
                    "attendance_date": dates_push[r - 1],
                    "status": status_hr,
                    "leave_type": "",
                    "terminal": json_employee[hr_emp]["branch"],
                    "department": json_employee[hr_emp]["department"],
                    "company": json_employee[hr_emp]["company"],
                    "nombre_completo": json_employee[hr_emp]["nombre_completo"],
                    "fecha_de_ingreso_real": json_employee[hr_emp]["fecha_de_ingreso_real"],
                    "fecha_de_relevo": json_employee[hr_emp]["fecha_de_relevo"],
                    "status_employee": json_employee[hr_emp]["status"],
                    "calificacion_trabajador": str(json_employee[hr_emp]["calificacion_trabajador"]),
                    "place_of_issue": json_employee[hr_emp]["place_of_issue"],
                    "passport_number": json_employee[hr_emp]["passport_number"],
                    "zona_recursos": json_employee[hr_emp]["zona_recursos"],
                }
                group_final.append(not_mark)

        groups_attendance_by_employee[hr_emp] = group_final
    array_data_excel = []
    for key_exc, insert_val_excel in groups_attendance_by_employee.items():
        # if key_exc == "HR-EMP-00753":
        #     return insert_val_excel
        if datetime.datetime.strptime(str(insert_val_excel[0]["fecha_de_ingreso_real"]), "%Y-%m-%d") >= last_day:
            continue
        array_data_dates_excel = []
        data_constant_employee = [key_exc, insert_val_excel[0]["nombre_completo"],
                                  terminalJSON.get(branchesJSON.get(insert_val_excel[0]["terminal"])).get("nombre") if terminalJSON.get(branchesJSON.get(insert_val_excel[0]["terminal"])) else insert_val_excel[0]["terminal"],
                                  insert_val_excel[0]["department"],
                                  insert_val_excel[0]["company"],
                                  insert_val_excel[0]["calificacion_trabajador"],
                                  insert_val_excel[0]["place_of_issue"],
                                  insert_val_excel[0]["passport_number"],
                                  insert_val_excel[0]["fecha_de_ingreso_real"],
                                  insert_val_excel[0]["fecha_de_relevo"],
                                  insert_val_excel[0]["zona_recursos"],
                                  insert_val_excel[0]["status_employee"]]
        for value_assistance in insert_val_excel:
            if str(value_assistance["attendance_date"]) <= str(my_day_now) or value_assistance["status"] != "":
                array_data_dates_excel.append(value_assistance["status"])
            else:
                array_data_dates_excel.append("")
        data_concat_register = data_constant_employee + array_data_dates_excel
        data_concat_register = data_concat_register + [terminalJSON.get(branchesJSON.get(insert_val_excel[0]["terminal"])).get("ter_id") if terminalJSON.get(branchesJSON.get(insert_val_excel[0]["terminal"])) else branchesJSON.get(insert_val_excel[0]["terminal"])]
        array_data_excel.append(data_concat_register)

    return array_data_excel, dates_push


@frappe.whitelist(allow_guest=True)
def excel_attendance(year=None, month=None):
    import calendar
    import datetime



    myobj = {'month': month}

    cortes = requests.post("https://recursoshumanos.shalom.com.pe/api/courts-month", json = myobj)
    cortes = cortes.json()
    cortes = cortes.get("data")
    # terminals_empresarial = requests.get("http://shalomcontrol.com/shalomprodapp/query/get_terminals_app_markings")
    terminalJSON = {}
    terminals_empresarial = frappe.get_all("Branch", fields=['name', 'ideentificador'] , filters=[], as_list=False)

    for entry in terminals_empresarial:
        terminalJSON[entry['ideentificador']] = entry

    branches = frappe.get_all("Branch", fields=['name', 'ideentificador'] , filters=[], as_list=False)
    branchesJSON = {}
    for branch in branches:
        branchesJSON[branch['name']] = str(branch["ideentificador"])
    month_map = get_month_map()
    month_str = str(month_map[month]).zfill(2)
    find_day_now = date.today()

    my_day_now = find_day_now.strftime("%Y-%m-%d")

    # Para fechas de este año
    # today = get_datetime()

    # Para fechas de otros años
    today = datetime.datetime.strptime(year+'-'+month_str+'-'+'01', "%Y-%m-%d")
    nxt_mnth = today.replace(day=28) + datetime.timedelta(days=4)
    res = nxt_mnth - datetime.timedelta(days=nxt_mnth.day)
    last_day = datetime.datetime.strptime(year+'-'+month_str+'-'+str(res.day), "%Y-%m-%d")

    final_range = calendar.monthrange(today.year, month_map[month])[1] + 1
    final_day_month = calendar.monthrange(today.year, month_map[month])[1]
    start_day_month = 1

    dates_of_month = ['{}-{}-{}'.format(today.year, month_str, r) for r in range(1, final_range)]

    array_heads_dates = []
    for day in range(1, final_range):
        daystr = str(day).zfill(2)
        timestamp = datetime.datetime.strptime(year+'-'+month_str+'-'+daystr, "%Y-%m-%d").timestamp()
        date_from_time = datetime.date.fromtimestamp(timestamp)
        d = date_from_time.strftime('%d-%b')
        array_heads_dates.append(d)

    array_head_employee = ["Codigo", "Nombre Completo", "Terminal", "Departamento", "Empresa","Calificación","Tipo Documento","N° Documento","Fecha de Ingreso Real","Fecha de Relevo","Zona","Estado"]

    final_head = array_head_employee + array_heads_dates + ["Id Sucursal"]

    length = len(dates_of_month)
    month_start, month_end = dates_of_month[0], dates_of_month[length-1]

    dates_push = []
    for k in range(start_day_month, final_day_month + 1):
        my_day = str(k).zfill(2)
        dates_push.append(year+'-'+month_str+'-'+my_day)

    holiday_sundays_list = holiday_sundays_dates()
    holiday_this_month = []
    holiday_this_month_holidays = []
    date_start_split = month_start.split('-')
    date_start_validate = date_start_split[0]+"-"+date_start_split[1]+"-0"+date_start_split[2]
    # date_start_time = datetime(int(date_start_split[0]),int(date_start_split[1]),int(date_start_split[2]))
    for this_month_holiday in holiday_sundays_list["domingos"]:
        str_holiday = str(this_month_holiday)
        if check_in_range(str_holiday, month_start, month_end):
            holiday_this_month.append(str_holiday)

    for this_month_holiday_holidays in holiday_sundays_list["feriados"]:
        str_holiday = str(this_month_holiday_holidays)
        if check_in_range(str_holiday, month_start, month_end):
            holiday_this_month_holidays.append(str_holiday)

    # doc_employees = frappe.db.get_list('Employee', fields=["name", "employee_name", "nombre_completo", "company", "branch", "department", "fecha_de_ingreso_real", "fecha_de_relevo", "status","calificacion_trabajador","place_of_issue","passport_number","zona_recursos"], as_list=False)
    doc_employees = frappe.db.sql("""
        SELECT
            emp.name, emp.employee_name, emp.nombre_completo, emp.company,
            emp.branch, emp.department, emp.fecha_de_ingreso_real, emp.fecha_de_relevo,
            emp.status, emp.calificacion_trabajador, emp.place_of_issue, emp.passport_number,
            br.zona_recursos_humanos as zona_recursos
        FROM `tabEmployee` emp 
        LEFT JOIN `tabBranch` br on emp.branch = br.name
        ORDER BY name asc
    """, values={}, as_dict=1)
    json_employee = dict()
    for employee in doc_employees:
        if employee["status"] == "Active" and employee["branch"] != "No especificado":
            json_employee[employee["name"]] = employee
        elif  employee["branch"] != "No especificado" and str(employee["fecha_de_relevo"])>=date_start_validate and str(employee["fecha_de_relevo"])<=month_end :
            json_employee[employee["name"]] = employee
        elif employee["fecha_de_relevo"] is None and (employee["status"] == "Active" or employee["status"]== "No Reportado"):
            json_employee[employee["name"]] = employee
    # values = {'start_date': month_start, 'end_date': month_end}
    # doc_attendances = frappe.db.sql(f"""SELECT employee, employee_name, attendance_date, status, leave_type FROM `tabAttendance` where company='Shalom Empresarial' AND branch!='No especificado' AND docstatus != '2' AND attendance_date >= %(start_date)s AND attendance_date <= %(end_date)s order by attendance_date asc; """, values=values, as_dict=True)
    doc_attendances = frappe.get_all("Attendance", fields=['employee', 'employee_name', 'company', 'attendance_date', 'status','estado_reporte', 'leave_type','docstatus'] , filters=[
        ["attendance_date", ">=", month_start],
        ["attendance_date", "<=", month_end],
        ["branch", "!=", "No especificado"],
        ["docstatus", "!=", 2]
    ], order_by='attendance_date asc', as_list=False)

    groups_attendance_by_employee = dict()
    doc_attendances_copy = []
    new_group = {}

    for val_attendance in doc_attendances:
        key_employee = val_attendance["employee"]
        if key_employee in json_employee:
            doc_attendances_copy.append(val_attendance)

    for key, value in groupby(doc_attendances_copy, key = itemgetter('employee')):
        for k in value:
            new_group[k["employee"]] = [k] if k["employee"] not in new_group.keys() else new_group[k["employee"]] + [k]

    copy_new_group = copy.copy(new_group)
    keys_group_employee_attendance = new_group.keys()
    key_employee = json_employee.keys()

    for key2, val_group in new_group.items():
        for val_employee in key_employee:
            if val_employee != key2:
                if val_employee not in keys_group_employee_attendance:
                    copy_new_group[val_employee] = []

    employe_list_final_group = []
    for hr_emp, val_hr in copy_new_group.items():
        group_final = []
        for r in range(start_day_month, final_day_month + 1):
            result_search = search_for_date(dates_push[r - 1], val_hr)
            count_list_hr = len(val_hr)
            if result_search[1]:
                stat = ""
                dayInit = result_search[0]["status"] if dates_push[r - 1] in cortes and result_search[0]["status"] != "" and result_search[0]["status"] is not None else result_search[0]["status"]
                if result_search[0]["docstatus"] == 1:
                    if dayInit == "On Leave":
                        if result_search[0]["leave_type"] == "VACACIONES":
                            stat = "VAC"
                        if result_search[0]["leave_type"] == "LICENCIA SIN GOCE":
                            stat = "LSG"
                        if result_search[0]["leave_type"] == "COMPENSATORIO":
                            stat = "COM"
                        if result_search[0]["leave_type"] == "LICENCIA CON GOCE":
                            stat = "LCG"
                        if result_search[0]["leave_type"] == "DESCANSO MEDICO":
                            stat = "DME"
                        if result_search[0]["leave_type"] == "PERMISO OCACIONAL":
                            stat = "L-PO"
                        if result_search[0]["leave_type"] == "SUBSIDIO":
                            stat = "LS"
                        if result_search[0]["leave_type"] == "SUBSIDIO POR ENFERMEDAD":
                            stat = "SXE"
                        if result_search[0]["leave_type"] == "SUBSIDIO POR MATERNIDAD":
                            stat = "SXM"
                        if result_search[0]["leave_type"] == "SUBSIDIO POR ACCIDENTE":
                            stat = "SXA"
                        if result_search[0]["leave_type"] == "LICENCIA POR FALLECIMIENTO":
                            stat = "LXF"
                        if result_search[0]["leave_type"] == "LICENCIA POR PATERNIDAD":
                            stat = "LXP"
                    if dayInit == "Present":
                        stat = "P"
                    if dayInit == "Absent":
                        stat = "A"
                    if dayInit == "Half Day":
                        stat = "HD"
                    if dayInit == "Work From Home" or dayInit == "Marcacion Incompleta":
                        stat = "MI"
                    result_search[0]["terminal"] = json_employee[hr_emp]["branch"]
                    result_search[0]["department"] = json_employee[hr_emp]["department"]
                    result_search[0]["company"] = json_employee[hr_emp]["company"]
                    result_search[0]["nombre_completo"] = json_employee[hr_emp]["nombre_completo"]
                    result_search[0]["fecha_de_ingreso_real"] = json_employee[hr_emp]["fecha_de_ingreso_real"]
                    result_search[0]["fecha_de_relevo"] = json_employee[hr_emp]["fecha_de_relevo"]
                    result_search[0]["status"] = stat
                    result_search[0]["status_employee"] = "".join(json_employee[hr_emp]["status"])
                    result_search[0]["calificacion_trabajador"]="".join(json_employee[hr_emp]["calificacion_trabajador"])
                    result_search[0]["place_of_issue"]= json_employee[hr_emp]["place_of_issue"]
                    result_search[0]["passport_number"]="".join(json_employee[hr_emp]["passport_number"])
                    result_search[0]["zona_recursos"]=json_employee[hr_emp]["zona_recursos"]
                    group_final.append(result_search[0])
                elif result_search[0]["docstatus"] == 0:
                    stat = "NV"
                    result_search[0]["terminal"] = json_employee[hr_emp]["branch"]
                    result_search[0]["department"] = json_employee[hr_emp]["department"]
                    result_search[0]["company"] = json_employee[hr_emp]["company"]
                    result_search[0]["nombre_completo"] = json_employee[hr_emp]["nombre_completo"]
                    result_search[0]["fecha_de_ingreso_real"] = json_employee[hr_emp]["fecha_de_ingreso_real"]
                    result_search[0]["fecha_de_relevo"] = json_employee[hr_emp]["fecha_de_relevo"]
                    result_search[0]["status"] = stat
                    result_search[0]["status_employee"] = "".join(json_employee[hr_emp]["status"])
                    result_search[0]["calificacion_trabajador"]="".join(json_employee[hr_emp]["calificacion_trabajador"])
                    result_search[0]["place_of_issue"]= json_employee[hr_emp]["place_of_issue"]
                    result_search[0]["passport_number"]="".join(json_employee[hr_emp]["passport_number"])
                    result_search[0]["zona_recursos"]=json_employee[hr_emp]["zona_recursos"]
                    group_final.append(result_search[0])
            else:
                if str(json_employee[hr_emp]["fecha_de_ingreso_real"]) <= dates_push[r - 1]:
                    if json_employee[hr_emp]["status"] == 'Active':
                        if json_employee[hr_emp]["fecha_de_relevo"] is None:
                            if dates_push[r - 1] in holiday_this_month:
                                status_hr = "WO"
                            elif dates_push[r - 1] in holiday_this_month_holidays:
                                status_hr = "*H*"
                            else:
                                status_hr = "NM"
                        else:
                            if str(json_employee[hr_emp]["fecha_de_relevo"]) < dates_push[r - 1]:
                                status_hr = "C"
                            else:
                                if dates_push[r - 1] in holiday_this_month:
                                    status_hr = "WO"
                                elif dates_push[r - 1] in holiday_this_month_holidays:
                                    status_hr = "*H*"
                                else:
                                    status_hr = "NM"
                    else:
                        if str(json_employee[hr_emp]["fecha_de_relevo"]) < dates_push[r - 1]:
                            status_hr = "C"
                        else:
                            if dates_push[r - 1] in holiday_this_month:
                                status_hr = "WO"
                            elif dates_push[r - 1] in holiday_this_month_holidays:
                                status_hr = "*H*"
                            else:
                                status_hr = "NM"
                else:
                    status_hr = "C"

                not_mark = {
                    "employee": hr_emp,
                    "employee_name": json_employee[hr_emp]["employee_name"],
                    "attendance_date": dates_push[r - 1],
                    "status": status_hr,
                    "leave_type": "",
                    "terminal": json_employee[hr_emp]["branch"],
                    "department": json_employee[hr_emp]["department"],
                    "company": json_employee[hr_emp]["company"],
                    "nombre_completo": json_employee[hr_emp]["nombre_completo"],
                    "fecha_de_ingreso_real": json_employee[hr_emp]["fecha_de_ingreso_real"],
                    "fecha_de_relevo": json_employee[hr_emp]["fecha_de_relevo"],
                    "status_employee": json_employee[hr_emp]["status"],
                    "calificacion_trabajador": str(json_employee[hr_emp]["calificacion_trabajador"]),
                    "place_of_issue": json_employee[hr_emp]["place_of_issue"],
                    "passport_number": json_employee[hr_emp]["passport_number"],
                    "zona_recursos": json_employee[hr_emp]["zona_recursos"],
                }
                group_final.append(not_mark)

        groups_attendance_by_employee[hr_emp] = group_final
    array_data_excel = []
    for key_exc, insert_val_excel in groups_attendance_by_employee.items():
        # if key_exc == "HR-EMP-00753":
        #     return insert_val_excel
        if datetime.datetime.strptime(str(insert_val_excel[0]["fecha_de_ingreso_real"]), "%Y-%m-%d") >= last_day:
            continue
        array_data_dates_excel = []
        data_constant_employee = [key_exc, insert_val_excel[0]["nombre_completo"],
                                  terminalJSON.get(branchesJSON.get(insert_val_excel[0]["terminal"])).get("nombre") if terminalJSON.get(branchesJSON.get(insert_val_excel[0]["terminal"])) else insert_val_excel[0]["terminal"],
                                  insert_val_excel[0]["department"],
                                  insert_val_excel[0]["company"],
                                  insert_val_excel[0]["calificacion_trabajador"],
                                  insert_val_excel[0]["place_of_issue"],
                                  insert_val_excel[0]["passport_number"],
                                  insert_val_excel[0]["fecha_de_ingreso_real"],
                                  insert_val_excel[0]["fecha_de_relevo"],
                                  insert_val_excel[0]["zona_recursos"],
                                  insert_val_excel[0]["status_employee"]]
        for value_assistance in insert_val_excel:
            if str(value_assistance["attendance_date"]) <= str(my_day_now) or value_assistance["status"] != "":
                array_data_dates_excel.append(value_assistance["status"])
            else:
                array_data_dates_excel.append("")
        data_concat_register = data_constant_employee + array_data_dates_excel
        data_concat_register = data_concat_register + [terminalJSON.get(branchesJSON.get(insert_val_excel[0]["terminal"])).get("ter_id") if terminalJSON.get(branchesJSON.get(insert_val_excel[0]["terminal"])) else branchesJSON.get(insert_val_excel[0]["terminal"])]
        array_data_excel.append(data_concat_register)


    return download_excel_attendance(final_head, array_data_excel, month, year)

@frappe.whitelist()
def excel_attendance_qa(year=None, month=None):
    import calendar
    import datetime



    myobj = {'month': month}

    cortes = requests.post("https://recursoshumanos.shalom.com.pe/api/courts-month", json = myobj)
    cortes = cortes.json()
    cortes = cortes.get("data")
    terminals_empresarial = requests.get("http://shalomcontrol.com/shalomprodapp/query/get_terminals_app_markings")
    terminalJSON = {}
    terminals_empresarial = terminals_empresarial.json()
    for entry in terminals_empresarial:
        terminalJSON[entry['ter_id']] = entry

    branches = frappe.get_all("Branch", fields=['name', 'ideentificador'] , filters=[], as_list=False)
    branchesJSON = {}
    for branch in branches:
        branchesJSON[branch['name']] = str(branch["ideentificador"])
    month_map = get_month_map()
    month_str = str(month_map[month]).zfill(2)
    find_day_now = date.today()

    my_day_now = find_day_now.strftime("%Y-%m-%d")

    # Para fechas de este año
    # today = get_datetime()

    # Para fechas de otros años
    today = datetime.datetime.strptime(year+'-'+month_str+'-'+'01', "%Y-%m-%d")
    nxt_mnth = today.replace(day=28) + datetime.timedelta(days=4)
    res = nxt_mnth - datetime.timedelta(days=nxt_mnth.day)
    last_day = datetime.datetime.strptime(year+'-'+month_str+'-'+str(res.day), "%Y-%m-%d")

    final_range = calendar.monthrange(today.year, month_map[month])[1] + 1
    final_day_month = calendar.monthrange(today.year, month_map[month])[1]
    start_day_month = 1

    dates_of_month = ['{}-{}-{}'.format(today.year, month_str, r) for r in range(1, final_range)]

    array_heads_dates = []
    for day in range(1, final_range):
        daystr = str(day).zfill(2)
        timestamp = datetime.datetime.strptime(year+'-'+month_str+'-'+daystr, "%Y-%m-%d").timestamp()
        date_from_time = datetime.date.fromtimestamp(timestamp)
        d = date_from_time.strftime('%d-%b')
        array_heads_dates.append(d)

    array_head_employee = ["Codigo", "Nombre Completo", "Terminal", "Departamento", "Empresa","Calificación","Tipo Documento","N° Documento","Fecha de Ingreso Real","Fecha de Relevo","Zona","Estado"]

    final_head = array_head_employee + array_heads_dates + ["Id Sucursal"]

    length = len(dates_of_month)
    month_start, month_end = dates_of_month[0], dates_of_month[length-1]

    dates_push = []
    for k in range(start_day_month, final_day_month + 1):
        my_day = str(k).zfill(2)
        dates_push.append(year+'-'+month_str+'-'+my_day)

    holiday_sundays_list = holiday_sundays_dates()
    holiday_this_month = []
    holiday_this_month_holidays = []
    date_start_split = month_start.split('-')
    date_start_validate = date_start_split[0]+"-"+date_start_split[1]+"-0"+date_start_split[2]
    # date_start_time = datetime(int(date_start_split[0]),int(date_start_split[1]),int(date_start_split[2]))
    for this_month_holiday in holiday_sundays_list["domingos"]:
        str_holiday = str(this_month_holiday)
        if check_in_range(str_holiday, month_start, month_end):
            holiday_this_month.append(str_holiday)

    for this_month_holiday_holidays in holiday_sundays_list["feriados"]:
        str_holiday = str(this_month_holiday_holidays)
        if check_in_range(str_holiday, month_start, month_end):
            holiday_this_month_holidays.append(str_holiday)

    # doc_employees = frappe.db.get_list('Employee', fields=["name", "employee_name", "nombre_completo", "company", "branch", "department", "fecha_de_ingreso_real", "fecha_de_relevo", "status","calificacion_trabajador","place_of_issue","passport_number","zona_recursos"], as_list=False)
    doc_employees = frappe.db.sql("""
        SELECT
            emp.name, emp.employee_name, emp.nombre_completo, emp.company,
            emp.branch, emp.department, emp.fecha_de_ingreso_real, emp.fecha_de_relevo,
            emp.status, emp.calificacion_trabajador, emp.place_of_issue, emp.passport_number,
            br.zona_recursos_humanos as zona_recursos
        FROM `tabEmployee` emp 
        LEFT JOIN `tabBranch` br on emp.branch = br.name
        ORDER BY name asc
    """, values={}, as_dict=1)
    json_employee = dict()
    for employee in doc_employees:
        if employee["status"] == "Active" and employee["branch"] != "No especificado":
            json_employee[employee["name"]] = employee
        elif  employee["branch"] != "No especificado" and str(employee["fecha_de_relevo"])>=date_start_validate and str(employee["fecha_de_relevo"])<=month_end :
            json_employee[employee["name"]] = employee
        elif employee["fecha_de_relevo"] is None and (employee["status"] == "Active" or employee["status"]== "No Reportado"):
            json_employee[employee["name"]] = employee
    # values = {'start_date': month_start, 'end_date': month_end}
    # doc_attendances = frappe.db.sql(f"""SELECT employee, employee_name, attendance_date, status, leave_type FROM `tabAttendance` where company='Shalom Empresarial' AND branch!='No especificado' AND docstatus != '2' AND attendance_date >= %(start_date)s AND attendance_date <= %(end_date)s order by attendance_date asc; """, values=values, as_dict=True)
    doc_attendances = frappe.get_all("Attendance", fields=['employee', 'employee_name', 'company', 'attendance_date', 'status','estado_reporte', 'leave_type','docstatus'] , filters=[
        ["attendance_date", ">=", month_start],
        ["attendance_date", "<=", month_end],
        ["branch", "!=", "No especificado"],
        ["docstatus", "!=", 2]
    ], order_by='attendance_date asc', as_list=False)

    groups_attendance_by_employee = dict()
    doc_attendances_copy = []
    new_group = {}

    for val_attendance in doc_attendances:
        key_employee = val_attendance["employee"]
        if key_employee in json_employee:
            doc_attendances_copy.append(val_attendance)

    for key, value in groupby(doc_attendances_copy, key = itemgetter('employee')):
        for k in value:
            new_group[k["employee"]] = [k] if k["employee"] not in new_group.keys() else new_group[k["employee"]] + [k]

    copy_new_group = copy.copy(new_group)
    keys_group_employee_attendance = new_group.keys()
    key_employee = json_employee.keys()

    for key2, val_group in new_group.items():
        for val_employee in key_employee:
            if val_employee != key2:
                if val_employee not in keys_group_employee_attendance:
                    copy_new_group[val_employee] = []

    employe_list_final_group = []
    for hr_emp, val_hr in copy_new_group.items():
        group_final = []
        for r in range(start_day_month, final_day_month + 1):
            result_search = search_for_date(dates_push[r - 1], val_hr)
            count_list_hr = len(val_hr)
            if result_search[1]:
                stat = ""
                dayInit = result_search[0]["status"] if dates_push[r - 1] in cortes and result_search[0]["status"] != "" and result_search[0]["status"] is not None else result_search[0]["status"]
                if result_search[0]["docstatus"] == 1:
                    if dayInit == "On Leave":
                        if result_search[0]["leave_type"] == "VACACIONES":
                            stat = "VAC"
                        if result_search[0]["leave_type"] == "LICENCIA SIN GOCE":
                            stat = "LSG"
                        if result_search[0]["leave_type"] == "COMPENSATORIO":
                            stat = "COM"
                        if result_search[0]["leave_type"] == "LICENCIA CON GOCE":
                            stat = "LCG"
                        if result_search[0]["leave_type"] == "DESCANSO MEDICO":
                            stat = "DME"
                        if result_search[0]["leave_type"] == "PERMISO OCACIONAL":
                            stat = "L-PO"
                        if result_search[0]["leave_type"] == "SUBSIDIO":
                            stat = "LS"
                        if result_search[0]["leave_type"] == "SUBSIDIO POR ENFERMEDAD":
                            stat = "SXE"
                        if result_search[0]["leave_type"] == "SUBSIDIO POR MATERNIDAD":
                            stat = "SXM"
                        if result_search[0]["leave_type"] == "SUBSIDIO POR ACCIDENTE":
                            stat = "SXA"
                        if result_search[0]["leave_type"] == "LICENCIA POR FALLECIMIENTO":
                            stat = "LXF"
                        if result_search[0]["leave_type"] == "LICENCIA POR PATERNIDAD":
                            stat = "LXP"
                    if dayInit == "Present":
                        stat = "P"
                    if dayInit == "Absent":
                        stat = "A"
                    if dayInit == "Half Day":
                        stat = "HD"
                    if dayInit == "Work From Home" or dayInit == "Marcacion Incompleta":
                        stat = "MI"
                    result_search[0]["terminal"] = json_employee[hr_emp]["branch"]
                    result_search[0]["department"] = json_employee[hr_emp]["department"]
                    result_search[0]["company"] = json_employee[hr_emp]["company"]
                    result_search[0]["nombre_completo"] = json_employee[hr_emp]["nombre_completo"]
                    result_search[0]["fecha_de_ingreso_real"] = json_employee[hr_emp]["fecha_de_ingreso_real"]
                    result_search[0]["fecha_de_relevo"] = json_employee[hr_emp]["fecha_de_relevo"]
                    result_search[0]["status"] = ("P" if stat == "WFH" else stat) if dates_push[r - 1] in cortes else stat
                    result_search[0]["status_employee"] = "".join(json_employee[hr_emp]["status"])
                    result_search[0]["calificacion_trabajador"]="".join(json_employee[hr_emp]["calificacion_trabajador"])
                    result_search[0]["place_of_issue"]= json_employee[hr_emp]["place_of_issue"]
                    result_search[0]["passport_number"]="".join(json_employee[hr_emp]["passport_number"])
                    result_search[0]["zona_recursos"]=json_employee[hr_emp]["zona_recursos"]
                    group_final.append(result_search[0])
                elif result_search[0]["docstatus"] == 0:
                    stat = "NV"
                    result_search[0]["terminal"] = json_employee[hr_emp]["branch"]
                    result_search[0]["department"] = json_employee[hr_emp]["department"]
                    result_search[0]["company"] = json_employee[hr_emp]["company"]
                    result_search[0]["nombre_completo"] = json_employee[hr_emp]["nombre_completo"]
                    result_search[0]["fecha_de_ingreso_real"] = json_employee[hr_emp]["fecha_de_ingreso_real"]
                    result_search[0]["fecha_de_relevo"] = json_employee[hr_emp]["fecha_de_relevo"]
                    result_search[0]["status"] = stat
                    result_search[0]["status_employee"] = "".join(json_employee[hr_emp]["status"])
                    result_search[0]["calificacion_trabajador"]="".join(json_employee[hr_emp]["calificacion_trabajador"])
                    result_search[0]["place_of_issue"]= json_employee[hr_emp]["place_of_issue"]
                    result_search[0]["passport_number"]="".join(json_employee[hr_emp]["passport_number"])
                    result_search[0]["zona_recursos"]=json_employee[hr_emp]["zona_recursos"]
                    group_final.append(result_search[0])
            else:
                if str(json_employee[hr_emp]["fecha_de_ingreso_real"]) <= dates_push[r - 1]:
                    if json_employee[hr_emp]["status"] == 'Active':
                        if json_employee[hr_emp]["fecha_de_relevo"] is None:
                            if dates_push[r - 1] in holiday_this_month:
                                status_hr = "WO"
                            elif dates_push[r - 1] in holiday_this_month_holidays:
                                status_hr = "*H*"
                            else:
                                status_hr = "NM"
                        else:
                            if str(json_employee[hr_emp]["fecha_de_relevo"]) < dates_push[r - 1]:
                                status_hr = "C"
                            else:
                                if dates_push[r - 1] in holiday_this_month:
                                    status_hr = "WO"
                                elif dates_push[r - 1] in holiday_this_month_holidays:
                                    status_hr = "*H*"
                                else:
                                    status_hr = "NM"
                    else:
                        if str(json_employee[hr_emp]["fecha_de_relevo"]) < dates_push[r - 1]:
                            status_hr = "C"
                        else:
                            if dates_push[r - 1] in holiday_this_month:
                                status_hr = "WO"
                            elif dates_push[r - 1] in holiday_this_month_holidays:
                                status_hr = "*H*"
                            else:
                                status_hr = "NM"
                else:
                    status_hr = "C"

                not_mark = {
                    "employee": hr_emp,
                    "employee_name": json_employee[hr_emp]["employee_name"],
                    "attendance_date": dates_push[r - 1],
                    "status": status_hr,
                    "leave_type": "",
                    "terminal": json_employee[hr_emp]["branch"],
                    "department": json_employee[hr_emp]["department"],
                    "company": json_employee[hr_emp]["company"],
                    "nombre_completo": json_employee[hr_emp]["nombre_completo"],
                    "fecha_de_ingreso_real": json_employee[hr_emp]["fecha_de_ingreso_real"],
                    "fecha_de_relevo": json_employee[hr_emp]["fecha_de_relevo"],
                    "status_employee": json_employee[hr_emp]["status"],
                    "calificacion_trabajador": str(json_employee[hr_emp]["calificacion_trabajador"]),
                    "place_of_issue": json_employee[hr_emp]["place_of_issue"],
                    "passport_number": json_employee[hr_emp]["passport_number"],
                    "zona_recursos": json_employee[hr_emp]["zona_recursos"],
                }
                group_final.append(not_mark)

        groups_attendance_by_employee[hr_emp] = group_final
    array_data_excel = []
    for key_exc, insert_val_excel in groups_attendance_by_employee.items():
        # if key_exc == "HR-EMP-00753":
        #     return insert_val_excel
        if datetime.datetime.strptime(str(insert_val_excel[0]["fecha_de_ingreso_real"]), "%Y-%m-%d") >= last_day:
            continue
        array_data_dates_excel = []
        data_constant_employee = [key_exc, insert_val_excel[0]["nombre_completo"],
                                  terminalJSON.get(branchesJSON.get(insert_val_excel[0]["terminal"])).get("nombre") if terminalJSON.get(branchesJSON.get(insert_val_excel[0]["terminal"])) else insert_val_excel[0]["terminal"],
                                  insert_val_excel[0]["department"],
                                  insert_val_excel[0]["company"],
                                  insert_val_excel[0]["calificacion_trabajador"],
                                  insert_val_excel[0]["place_of_issue"],
                                  insert_val_excel[0]["passport_number"],
                                  insert_val_excel[0]["fecha_de_ingreso_real"],
                                  insert_val_excel[0]["fecha_de_relevo"],
                                  insert_val_excel[0]["zona_recursos"],
                                  insert_val_excel[0]["status_employee"]]
        for value_assistance in insert_val_excel:
            if str(value_assistance["attendance_date"]) <= str(my_day_now) or value_assistance["status"] != "":
                array_data_dates_excel.append(value_assistance["status"])
            else:
                array_data_dates_excel.append("")
        data_concat_register = data_constant_employee + array_data_dates_excel
        data_concat_register = data_concat_register + [terminalJSON.get(branchesJSON.get(insert_val_excel[0]["terminal"])).get("ter_id") if terminalJSON.get(branchesJSON.get(insert_val_excel[0]["terminal"])) else branchesJSON.get(insert_val_excel[0]["terminal"])]
        array_data_excel.append(data_concat_register)
    return download_excel_attendance(final_head, array_data_excel, month, year)

def search_for_date(date="", array=[]):
    for search_date in array:
        if str(search_date["attendance_date"]) == date:
            return [search_date, True]
    return [[], False]


def get_month_map():
    return frappe._dict({
        "Enero": 1,
        "Febrero": 2,
        "Marzo": 3,
        "Abril": 4,
        "Mayo": 5,
        "Junio": 6,
        "Julio": 7,
        "Agosto": 8,
        "Setiembre": 9,
        "Octubre": 10,
        "Noviembre": 11,
        "Diciembre": 12
    })


@frappe.whitelist()
def holiday_sundays_dates():
    doc = frappe.db.sql(f"""SELECT * FROM `tabHoliday` order by holiday_date asc; """, as_dict=True)
    array_holiday = []
    array_sundays = []
    for holiday in doc:
        if holiday["description"] != 'Sunday':
            array_holiday.append(holiday["holiday_date"])
        else:
            array_sundays.append(holiday["holiday_date"])
    return frappe._dict({
        "feriados": array_holiday,
        "domingos": array_sundays
    })


def check_in_range(date_check="", date_start="", date_end=""):
    my_date = date_check.split('-')

    my_date_start = date_start.split('-')

    my_date_end = date_end.split('-')

    date_now = datetime(int(my_date[0]), int(my_date[1]), int(my_date[2]))
    date_now1 = date_now.date()
    date_now = date_now1;

    date_start = datetime(int(my_date_start[0]), int(my_date_start[1]), int(my_date_start[2]))
    date_start1 = date_start.date()
    date_start = date_start1


    date_end = datetime(int(my_date_end[0]), int(my_date_end[1]), int(my_date_end[2]))
    date_end1 = date_end.date()
    date_end = date_end1

    result = False
    if date_start <= date_now <= date_end:
        result = True
    return result

@frappe.whitelist()
def courses_by_designation():

    user_email = frappe.db.get_value("User",{
        "name": frappe.session.user,
    },"email")
    designation = frappe.db.get_value("Employee",{
        "user_id": user_email,
        "status": "Active"
    },"designation")
    if designation is None or designation == '':
        designation = "ENCARGADO DE AGENCIA"
    courses = frappe.db.get_all("Course",
                                filters=[], as_list=False)
    courses_program = {}
    for course in courses:
        programs = frappe.db.get_all("Program",
                                    filters=[["Program Course","course","=",course.name]], as_list=False)
        if len(programs) > 0:
            courses_program[course.name] = programs[0].name
    # return courses_program
    courses_data =  [frappe.get_doc("Course", course.name) for course in courses]
    # return courses_data[0]
    courses_end = []
    for course_item in courses_data:
        if course_item.name in courses_program:
            course_end = {
                "name": course_item.name,
                "owner": course_item.owner,
                "creation": course_item.creation,
                "modified": course_item.modified,
                "modified_by": course_item.modified_by,
                "idx": course_item.idx,
                "docstatus": course_item.docstatus,
                "course_name": course_item.course_name,
                "department": course_item.department,
                "hero_image": course_item.hero_image,
                "doctype": course_item.doctype,
                "topics": course_item.topics,
                "designation": course_item.designation,
                "assessment_criteria": course_item.assessment_criteria,
                "program": courses_program[course_item.name],
            }
            courses_end.append(course_end)
    return courses_end

@frappe.whitelist()
def report_pos_register():
    terminals_empresarial = requests.get("http://shalomcontrol.com/shalomprodapp/query/get_terminals_app_markings_pos")
    terminalJSON = {}
    terminals_empresarial = terminals_empresarial.json()
    for entry in terminals_empresarial:
        terminalJSON[entry['ter_id']] = entry

    filters = {"from_date":"2023-02-17","to_date":"2023-03-17"}
    conditions = get_conditions(filters)
    order_by = "p.posting_date"
    select_mop_field, from_sales_invoice_payment, group_by_mop_condition = "", "", ""

    data_entries = frappe.db.sql(
        """
        SELECT 
            p.posting_date,p.posting_time, p.name as pos_invoice, p.pos_profile,br.zona_recursos_humanos as region, pro.branch as sucursal, br.ideentificador as idsucursal,
            br.categoria, us.full_name as owner,us.full_name as owner_name,p.status_comprobante as status_comprobante, p.base_grand_total as grand_total, p.base_grand_total as paid_amount,
            p.customer, p.is_return,p.documento, itm.description as item {select_mop_field}
        FROM
            `tabPOS Invoice Item` itm {from_sales_invoice_payment}
        LEFT JOIN `tabPOS Invoice` p on (itm.parent=p.name)
        LEFT JOIN `tabPOS Profile` pro on (p.pos_profile = pro.name)
        LEFT JOIN `tabBranch` br on (pro.branch = br.name)
        LEFT JOIN tabUser us on( us.name = p.owner )
        WHERE
            p.docstatus = 1 and
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
            "sucursal": entry.sucursal,
            "idsucursal": entry.idsucursal,
            "categoria": entry.categoria,
            "owner": entry.owner,
            "owner_name": entry.owner_name,
            "status_comprobante": "FACTURA" if entry.documento and len(entry.documento) == 11 else "BOLETA",
            "grand_total": entry.grand_total,
            "paid_amount": entry.paid_amount,
            "customer": entry.customer,
            "is_return": entry.is_return,
            "item": entry.item,
            "tipo_local": terminalJSON[str(entry.idsucursal)]["tipo_local"] if str(entry.idsucursal) in terminalJSON.keys() else "",
            "type_payment": entry.status_comprobante if entry.status_comprobante in ["Pago por PINPAD","QR","Planilla"] else "CONTADO",
        })

    return data


@frappe.whitelist(allow_guest=True)
def logueoCdTalleres():
    session = requests.Session()
    r = session.post("https://cdtalleres.shalom.com.pe/api/method/login", data={
        "usr": "administrator",
        "pwd": ".Overskull."
    })

    if r.status_code == 200:
        cookies_data = {
            "full_name": "USUARIO%20SISTEMA",
            "sid": "31fdd127df64067e70b318672a0dbc588167862819a59662a819cea0",
            "system_user": "yes",
            "user_id": "Administrator",
            "user_image": ""
        }

        if frappe.local.response.cookies is None:
            frappe.local.response.cookies = {}
        set_cookie_header = "; ".join([f"{key}={value}" for key, value in cookies_data.items()])
        frappe.local.response.cookies["Set-Cookie"] = set_cookie_header

        return {"message": "Inicio de sesión exitoso", "cookies": cookies_data}
    else:
        frappe.log_error(f"Error al iniciar sesión. Código de estado: {r.status_code}")
        frappe.local.response.http_status_code = r.status_code
        return {"message": f"Error al iniciar sesión. Código de estado: {r.status_code}"}

@frappe.whitelist(allow_guest=True)
def insertUserERP():
    try:
        request_data = frappe.request.get_data(as_text=True)
        data = json.loads(request_data)
        result_array = []
        keys = []
        fieldnameone = []
        for key, value in data.items():
            keys.append(value[0])
            result_array.append({key: value})
            fieldnameone.append(key)

        ##CREACION DE USUARIO
        fieldnameone = [f"{valor}" for valor in fieldnameone]
        columns = ', '.join(fieldnameone)
        placeholders = ', '.join(['%s'] * len(keys))
        sql_insert_query = f"INSERT INTO tabUser ({columns}) VALUES ({placeholders})"

        ##INSERTAR CONTRASEÑA
        update_password(keys[0],"CAPACITACION")
        data = frappe.db.sql(sql_insert_query,keys)

        ##CREACION DE NOTIFICACION PARA EL NUEVO USUARIO (OBLIGATORIO)
        sql_notification = f"""
            INSERT INTO tabNotification Settings (
            name
            )
            VALUES (
            '{keys[0]}'
            )
        """
        data = frappe.db.sql(sql_notification)

        frappe.db.commit()
        return data
    except Exception as e:
        doc = frappe.new_doc('WebhooLogs')
        doc.name_doctype = 'User'
        doc.name_error = 'insertUserERP'
        doc.msn_error = str(e)
        doc.insert(ignore_permissions=True)
        frappe.db.commit()
        return "error"

@frappe.whitelist(allow_guest=True)
def updateUserErp():
    try:
        request_data = frappe.request.get_data(as_text=True)
        data = json.loads(request_data)
        result_array = []
        keys = []
        fieldnameone = []

        for key, value in data.items():
            keys.append(value[0])
            result_array.append({key: value})
            fieldnameone.append(f"{key} = '{value[0]}'")  #

        sql_update_query = f"""
            UPDATE tabUser SET {', '.join(fieldnameone[1:])}  
            WHERE tabUser.name = '{keys[0]}'
        """

        data = frappe.db.sql(sql_update_query)
        frappe.db.commit()
        return "true"
    except Exception as e:
        doc = frappe.new_doc('WebhooLogs')
        doc.name_doctype = 'User'
        doc.name_error = 'updateUserErp'
        doc.msn_error = str(e)
        doc.insert(ignore_permissions=True)
        frappe.db.commit()
        return "error"

@frappe.whitelist(allow_guest=True)
def getRoles(user=None):
    sql_roles = f"""
                SELECT
                    emp.branch,
                    emp.designation
                FROM
                    tabEmployee as emp
                WHERE
                    emp.user_id = '{user}'
                    AND emp.designation IN ('ADMINISTRADOR DE AGENCIA', 'ENCARGADO DE AGENCIA')
            """
    data = frappe.db.sql(sql_roles, as_dict=True)
    return data
    ##return {"message": "Roles obtenidos exitosamente", "data": data}

@frappe.whitelist(allow_guest=True)
def serviceUser(user=None):
    sql = f"""
                    SELECT
                        emp.name,
                        emp.department
                    FROM
                        tabEmployee as emp
                    WHERE
                        emp.user_id = '{user}'
                """
    data = frappe.db.sql(sql, as_dict=True)
    if len(data) <= 0:
        return {"valor": False}
    if data[0]["department"] == "Operaciones - SE":
        return {"valor": True}
    return {"valor": False}

@frappe.whitelist(allow_guest=True)
def getAreaManagerData():
    sql = f"""
                    SELECT
                        tpr.name,
                        tpr.usuario_vinculado,
                        tpr.is_group
                    FROM
                        tabDepartment as tpr
                """
    data = frappe.db.sql(sql, as_dict=True)
    arrayArea = {}
    for value in data:
        if "usuario_vinculado" in value and value["usuario_vinculado"] != "" and value["usuario_vinculado"] is not None:
            arrayArea[value["usuario_vinculado"]] = value["name"]

    return arrayArea

@frappe.whitelist(allow_guest=True)
def getEmployeeNotReported(departamento=None):
    status = "No Reportado"
    branch = "MEXICO"

    sql2 = f"""
        SELECT
            tpr.name,
            tpr.usuario_vinculado,
            tpr.is_group
        FROM
            tabDepartment as tpr
        WHERE
            tpr.name = '{departamento}'
    """
    data2 = frappe.db.sql(sql2, as_dict=True)

    if len(data2) == 0:
        return []

    group = data2[0]["is_group"]

    if group == 0:
        campo_busqueda = "tpr.area"
    else:
        campo_busqueda = "tpr.department"

    sql = f"""
        SELECT
            tpr.name,
            tpr.branch,
            tpr.nombre_completo,
            tpr.fecha_de_ingreso_real,
            tpr.status
        FROM
            tabEmployee as tpr
        WHERE
            tpr.status = 'No Reportado' AND
            {campo_busqueda} = '{departamento}' AND
            tpr.branch = 'MEXICO'
    """

    data = frappe.db.sql(sql, as_dict=True)

    return data



@frappe.whitelist(allow_guest=True)
def getAttendanceRecords(employee=None, date=None):
    sql = f"""
        SELECT
            tpr.time,
            tpr.name,
            tpr.log_type
        FROM
            `tabEmployee Checkin` as tpr
        WHERE
            tpr.employee = '{employee}' and tpr.fecha_de_consolidado = '{date}'
    """
    data = frappe.db.sql(sql, as_dict=True)

    if len(data)==0:
        return { "status" : False,"msn" : "Sin marcaciones"}
    return { "status" : True,"msn" : data}

@frappe.whitelist(allow_guest=True)
def checkStorageSupervisionsStore(branch=None):

    if branch == "MEXICO":
        return { "status" : True, "msn" : "No hay restricciones"}

    typesOfWarehouse = [
        "Tienda",
        "EMBALAJE"
    ]

    sql = f"""
            SELECT
                tpr.warehouse_type,
                tpr.name
            FROM
                `tabWarehouse` as tpr
            WHERE
                tpr.sucursal = '{branch}' and tpr.warehouse_type IN {tuple(typesOfWarehouse)}
        """

    data = frappe.db.sql(sql, as_dict=True)
    if len(data) == 0:
        return {"status" : True, "msn" :"Not restriction"}

    today = date.today()
    date_format = today.strftime('%Y-%m-%d')
    dtObj = datetime.strptime(date_format, '%Y-%m-%d')
    n = 1
    past_date = dtObj - relativedelta(months=n)
    almacen = []
    warehouseOfRestriction = {}
    for value in data:
        warehouseOfRestriction[value["name"]] = value
        almacen.append(value["name"])

    almacen = tuple(almacen)
    date_format = date_format + " 00:00:00"
    sqlSupervision = f"""
        SELECT
            name,
            almacen,
            tipo_de_almacen,
            fecha
        FROM
            `tabSupervicion Almacen`
        WHERE
            almacen IN {almacen} and (fecha
            BETWEEN '{past_date}' AND '{date_format}')
    """
    dataSupervision = frappe.db.sql(sqlSupervision, as_dict=True)
    if len(dataSupervision) == 0:
        return {"status" : False,"msn" : "No ha realizado sus supervisiones","warehouses" : warehouseOfRestriction}

    arrayVerified = {}

    for element in dataSupervision:
        arrayVerified[element["tipo_de_almacen"]] = element

    if len(arrayVerified) == 2 :
        return {"status" : True,"msn" : "Si realizo sus supervisiones"}

    arrayUncompleted = {}

    for value in data:
        warehouse_type = value["warehouse_type"]

        if warehouse_type in globals():
            continue
        else:
            arrayUncompleted = value

    return { "status" : False, "msn" : "Supervisiones Incompletas","warehouses" : arrayUncompleted}

@frappe.whitelist(allow_guest=True)
def updateAssistanceOfEmployee():
    # se le pasa employee, date y state
    employee = "HR-EMP-04162"
    date = "2024-02-26"
    state = "Present"
    docstatus = 1

    sqlUlti = f"""
            SELECT
                tpr.name
            FROM
                tabAttendance as tpr
            ORDER BY creation ASC
            LIMIT 1
        """
    dataUlti = frappe.db.sql(sqlUlti, as_dict=True)
    newName = int(dataUlti[0]["name"].split("-")[3]) +1
    nameE = "HR-ATT-" + dataUlti[0]["name"].split("-")[2]
    newName = nameE + "-" + str(newName)
    dataResponse = {}
    sql = f"""
        SELECT
            tpr.name
        FROM
            tabAttendance as tpr
        WHERE
            tpr.employee = '{employee}' and tpr.attendance_date = '{date}' and tpr.docstatus = '{docstatus}'
    """
    dataAssistanceErp = frappe.db.sql(sql, as_dict=True)

    if len(dataAssistanceErp) > 0:
        sqlUpdate = f"""
            UPDATE tabAttendance SET docstatus = 2
            WHERE tabAttendance.name = '{dataAssistanceErp[0]["name"]}'
        """
        frappe.db.sql(sqlUpdate)
        frappe.db.commit()

        sqlCreate = f"""
            INSERT INTO tabAttendance (
                name,
                employee,
                attendance_date,
                status,
                docstatus
            )
            VALUES (
                '{newName}',
                '{employee}',
                '{date}',
                '{state}',
                '{docstatus}'
            )
        """

        respuesta = frappe.db.sql(sqlCreate)
        frappe.db.commit()
        nuevo_registro = frappe.get_doc("Attendance", newName)
    else:
        sqlCreate = f"""
            INSERT INTO tabAttendance (
                name,
                employee,
                attendance_date,
                status,
                docstatus
            )
            VALUES (
                '{newName}',
                '{employee}',
                '{date}',
                '{state}',
                '{docstatus}'
            )
        """

        respuesta = frappe.db.sql(sqlCreate)
        frappe.db.commit()
        nuevo_registro = frappe.get_doc("Attendance", newName)

    return nuevo_registro

@frappe.whitelist(allow_guest=True)
def checkStorageSupervisions():
    branch = "PUNO"
    if branch == "MEXICO":
        return {"status" :True,"msn" : "Not restriction"}
    typesOfWarehouse = [
        "EQUIPOS COMP",
        "HERRAMIENTAS",
        "INMOBILIARIO",
        "EQUIPAMIENTO"
    ]

    sql = f"""
            SELECT
                tpr.warehouse_type,
                tpr.name
            FROM
                tabWarehouse as tpr
            WHERE
                tpr.sucursal = '{branch}' and tpr.warehouse_type IN {tuple(typesOfWarehouse)}
        """

    data = frappe.db.sql(sql, as_dict=True)
    if len(data) == 0:
        return {"status" : False, "msn" :"Sucursal sin Almacenes, contacte con soporte"}

    if len(data) > 0 and len(data) < 4:
        return {"status" : False, "msn" :"Sucursal con Almacenes Incompletos, contacte con soporte"}

    today = date.today()
    date_format = today.strftime('%Y-%m-%d')
    currentDate = datetime.strptime(date_format, '%Y-%m-%d')
    n = 1
    dateAux = currentDate - relativedelta(months=n)
    warehouseOfRestriction = {}
    almacen = []

    for value in data:
        warehouseOfRestriction[value["name"]] = value
        almacen.append(value["name"])

    almacen = tuple(almacen)

    date_format = date_format + " 00:00:00"
    sqlSupervision = f"""
        SELECT
            tpr.name,
            tpr.almacen,
            tpr.tipo_de_almacen,
            tpr.fecha
        FROM
            tabSupervicion Almacen as tpr
        WHERE
            tpr.almacen IN {almacen} and tpr.fecha
            BETWEEN '{dateAux}' AND '{date_format}'
    """

    dataSupervision = frappe.db.sql(sqlSupervision, as_dict=True)
    arrayVerified = {};
    if len(dataSupervision) == 0:
        return {"status" : False,"msn" : "No ha realizado sus supervisiones","warehouses" : warehouseOfRestriction}

    arrayUncompleted = {}
    for element in dataSupervision:
        arrayVerified[element["tipo_de_almacen"]] = element

    if len(arrayVerified) == 4 :
        return {"status" : True,"msn" : "Si realizo sus supervisiones"}

    arrayUncompleted = {}

    for value in data:
        warehouse_type = value["warehouse_type"]
        if warehouse_type in globals():
            continue
        else:
            arrayUncompleted = value

    return { "status" : False, "msn" : "Supervisiones Incompletas","warehouses" : arrayUncompleted}

@frappe.whitelist(allow_guest=True)
def checkPayrollDownloadStatus(department=None):
    sql = f"""
        SELECT
            dep.name,
            dep.is_group
        FROM
            tabDepartment as dep
        WHERE
            dep.name = '{department}' 
    """

    dataDepartment = frappe.db.sql(sql, as_dict=True)

    if len(dataDepartment) == 0:
        return {"status" : False,"msn" : "No existe departamento",}

    today = date.today()
    dateInitActually = today.strftime('%Y-%m-01')

    if dataDepartment[0]["is_group"] == 1:
        sql = f"""
        SELECT
            tpr.name,
            tpr.branch,
            tpr.department,
            tpr.nombre_completo
        FROM
            tabEmployee as tpr
        WHERE
            tpr.department = '{department}' and tpr.status = 'Active' and tpr.branch = 'MEXICO' and  tpr.fecha_de_ingreso_real < '{dateInitActually}' 
        """
    else:
        sql = f"""
        SELECT
            tpr.name,
            tpr.branch,
            tpr.department,
            tpr.nombre_completo
        FROM
            tabEmployee as tpr
        WHERE
            tpr.area = '{department}' and tpr.status = 'Active' and tpr.branch = 'MEXICO' and  tpr.fecha_de_ingreso_real < '{dateInitActually}' 
        """

    dataEmployee = frappe.db.sql(sql, as_dict=True)
    if len(dataEmployee) == 0:
        return {"status": False,"msn" : "No hay empleados vinculados al departamento o área",}

    employees = []
    for element in dataEmployee:
        employees.append(element["name"])

    today = date.today()
    date_format = today.strftime('%Y-%m-%d')
    currentDate = datetime.strptime(date_format, '%Y-%m-%d')
    n = 1
    dateAux = currentDate - relativedelta(months=n)
    datePas = dateAux.strftime('%Y-%m-%d ')
    datePas = datePas.split('-')

    monthPast = datePas[1]
    yearPast = datePas[0]


    employees = json.dumps(employees)
    datos = {
        "yearPast": yearPast,
        "monthPast": monthPast,
        "employees": employees
    }

    response = requests.post("https://horario-salida-qa-erpwin.shalom.com.pe//module/human/historial_proceso", json=datos)
    response = response.json()

    descargaron = []
    for valProc in response:
        if valProc['empleado'] not in descargaron:
            descargaron.append(valProc['empleado'])

    no_descargaron = []
    for valEmp in dataEmployee:
        if valEmp['name'] not in descargaron:
            no_descargaron.append(valEmp)


    today = today.strftime('%Y-%m-%d ')
    today = today.split('-')
    # date_format = date_format.strftime("%Y-%m-%d")
    numberDay = today[2]
    numberDay = int(numberDay)

    return {
        "status": True,
        "restriction": not (numberDay >= 1 and numberDay <= 4 ),
        "employees": no_descargaron
    }

@frappe.whitelist(allow_guest=True)
def getEmployeeNotAssistance(department=None):
    holidayList = {};
    daysJson = [];
    currentDate = date.today()
    yesterdayDate = currentDate.strftime('%Y-%m-01')
    yesterdayAux = currentDate + relativedelta(months=1)
    yesterdayAuxString = yesterdayAux.strftime('%Y-%m-01')

    # Resta un día a yesterdayAux
    finalDate = yesterdayAux.replace(day=1) - timedelta(days=1)
    finalDate = finalDate.strftime('%Y-%m-%d')
    arrayEmployees = {};
    arrayAssistance = {};

    ####formate date
    date1 = currentDate
    date2 = datetime.strptime(yesterdayDate, '%Y-%m-%d').date()
    days = (date1 - date2).days
    days = abs((date1 - date2).days)

    yesterdayDateTypeDate = datetime.strptime(yesterdayDate, '%Y-%m-%d')
    for i in range(days):
        dates = (yesterdayDateTypeDate + timedelta(days=i)).strftime('%Y-%m-%d')
        daysJson.append(dates)

    sql = f"""
        SELECT
            holiday_date
        FROM
            tabHoliday as tpr
        WHERE
            tpr.parent = 'FERIADOS 2022' and tpr.parentfield  = 'holidays' and tpr.parenttype = 'Holiday List' and holiday_date >= '2023-01-01 order by holiday_date desc'
        """

    dataHolidaysErp = frappe.db.sql(sql, as_dict=True)

    holidayList = [item["holiday_date"] for item in dataHolidaysErp]

    sqlDepartament = f"""
        SELECT
            name, usuario_vinculado, is_group
        FROM
            tabDepartment as tpr
        WHERE
            tpr.name = '{department}' 
        """

    departamentResult = frappe.db.sql(sqlDepartament, as_dict=True)

    if departamentResult[0]["is_group"] == 1:
        sqlAssistance = f"""
            SELECT
                name, branch, nombre_completo, fecha_de_ingreso_real, status, employment_type, tipo_de_jornada
            FROM
                tabEmployee as tpr
            WHERE
                tpr.status IN ('Active', 'No Reportado')  and tpr.department = '{department}'  and tpr.branch = 'MEXICO'
        """
    else:
        sqlAssistance = f"""
            SELECT
                name, branch, nombre_completo, fecha_de_ingreso_real, status, employment_type, tipo_de_jornada
            FROM
                tabEmployee as tpr
            WHERE
                tpr.status IN ('Active', 'No Reportado')  and tpr.area = '{department}'  and tpr.branch = 'MEXICO'
        """

    dataAssistanceErp = frappe.db.sql(sqlAssistance, as_dict=True)
    if len(dataAssistanceErp) != 0:
        for value2 in dataAssistanceErp:
            arrayEmployees[value2["name"]] = value2
    arrayEmployeesKeys = list(arrayEmployees.keys())
    arrayEmployeesKeysTuple = tuple(arrayEmployeesKeys)
    ##eddy
    ##arrayEmployeesKeysTuple = ', '.join(['%s'] * len(arrayEmployees))

    sqlAttendance = f"""
            SELECT
                name, department, status, docstatus, employee, attendance_date
            FROM
                tabAttendance
            WHERE
                employee IN {arrayEmployeesKeysTuple}  and docstatus != '2'and attendance_date BETWEEN '{yesterdayDate}' AND '{currentDate}'
        """
    #                employee IN {arrayEmployeesKeysTuple}  and docstatus != '2'and attendance_date BETWEEN {currentDate} AND {yesterdayDate}

    attendancess = frappe.db.sql(sqlAttendance, as_dict=True)
    array_assistance = {}
    attendances_nm = {}
    employees_final = []

    for value10 in attendancess:
        array_assistance[value10["employee"]] = value10

    attendances_nm = {}

    for value in attendancess:
        employee_key = str(value["employee"])
        date_key = str(value["attendance_date"])
        if employee_key not in attendances_nm:
            attendances_nm[employee_key] = {}
        attendances_nm[employee_key][date_key] = value
    employees_final = []

    for dia in daysJson:
        for employee in dataAssistanceErp:
            if dia in holidayList:
                continue

            if datetime.strptime(str(dia), "%Y-%m-%d").date() < employee["fecha_de_ingreso_real"]:
                continue

            if employee["name"] in attendances_nm and dia in attendances_nm[employee["name"]]:
                if attendances_nm[employee["name"]][dia]["status"] in ["Marcacion Incompleta", "Marcacion Incompleta"]:
                    arrayEmployees[employee["name"]]['date_correction']= dia
                    arrayEmployees[employee["name"]]['correction']= 1
                    employees_final.append(arrayEmployees[employee["name"]])

                continue

            arrayEmployees[employee["name"]]['date_correction']= dia
            arrayEmployees[employee["name"]]['correction']= 1
            employees_final.append(arrayEmployees[employee["name"]])


    return employees_final

@frappe.whitelist(allow_guest=True)
def checkContractDownloadStatus(department=None):
    sql = f"""
        SELECT
            name, is_group
        FROM
            `tabDepartment` as tpr
        WHERE
            tpr.name = '{department}'
        """

    dataDepartment = frappe.db.sql(sql, as_dict=True)

    if len(dataDepartment) == 0:
        return {"status" : False,"msn" : "No existe departamento",}

    if dataDepartment[0]["is_group"] == 1:
        sql = f"""
        SELECT
            tpr.name,
            tpr.branch,
            tpr.department,
            tpr.nombre_completo
        FROM
            `tabEmployee` as tpr
        WHERE
            tpr.department = '{department}' and tpr.status = 'Active' and tpr.branch = 'MEXICO'
        """
    else:
        sql = f"""
        SELECT
            tpr.name,
            tpr.branch,
            tpr.department,
            tpr.nombre_completo
        FROM
            `tabEmployee` as tpr
        WHERE
            tpr.area = '{department}' and tpr.status = 'Active' and tpr.branch = 'MEXICO'
        """

    dataEmployee = frappe.db.sql(sql, as_dict=True)
    if len(dataEmployee) == 0:
        return {"status": False,"msn" : "No hay empleados vinculados al departamento o área",}

    employees = []

    for element in dataEmployee:
        employees.append(element["name"])

    currentDate = date.today()
    currentDateString = str(date.today())
    numberDay=currentDateString.split('-')[2]
    monthPasado = currentDate - relativedelta(months=1)
    monthPasadoString = str(monthPasado)
    yearPast = monthPasadoString.split('-')[0]
    monthPast = monthPasadoString.split('-')[1]
    indexMonthPast = int(monthPast) - 1
    monthPast = str(monthPast)

    ##
    months = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Setiembre', 'Octubre', 'Noviembre', 'Diciembre'];

    employees_quoted = [f"'{employee}'" for employee in employees]
    employees2 = ','.join(employees_quoted)

    try:
        sqlSolicitud = f"""
        SELECT
            tsr.name, tsr.data_12, tsr.año, tpr.codigo, tpr.renueva, temp.tipo_de_documento, temp.passport_number,
            tpr.codigo, tpr.tiempo_renovacion, tpr.tipo_de_contraro, temp.nombre_completo, temp.designation,
            temp.fecha_de_ingreso_real, temp.branch, temp.id_sucursal, temp.department
        FROM
            `tabSolicitud de Renovaciones` as tsr
            LEFT JOIN `tabTrabajadores pendiete de renovar` as tpr ON (tpr.parent = tsr.name)
            LEFT JOIN `tabEmployee` as temp ON (temp.name = tpr.codigo)
        WHERE
            tsr.data_12 = '{months[indexMonthPast]}' AND tsr.año = '{yearPast}' AND tsr.docstatus = 1 AND tpr.renueva = 'Si'
            AND tpr.codigo IN ({employees2})
        """
        dataSolicitud = frappe.db.sql(sqlSolicitud, as_dict=True)
    except Exception:
        return {
            "status" : False,
            "restriction" : False,
            "employees" : [],
            "msn" : "Error al obtener los datos de renovación"
        };
    if len(dataSolicitud) > 0:
        employeesRenovation = []
        for value in dataSolicitud:
            if value['codigo'] not in employeesRenovation:
                employeesRenovation.append(value['codigo'])

        if len(employeesRenovation) > 0:
            dateStarProcess = datetime.strptime(f"{yearPast}-{monthPast}-01", '%Y-%m-%d').date()
            dateEndProcess = dateStarProcess  + relativedelta(months=1)
            dateEndProcess = dateEndProcess + timedelta(days=30)
            dateStarProcess = str(dateStarProcess) + " 00:00:00"
            dateEndProcess = str(dateEndProcess) + " 00:00:00"

            employeesRenovation = json.dumps(employeesRenovation)

            datos = {
                "dateStarProcess": dateStarProcess,
                "dateEndProcess": dateEndProcess,
                "employeesRenovation": employeesRenovation
            }

            data = requests.post("https://horario-salida-qa-erpwin.shalom.com.pe/module/human/historial_procesos_app", json=datos)
            data = data.json()
            employeesDownloaded = []
            for value in data:
                employeesDownloaded.append(value['empleado'])

            employeesNotDownloaded = []
            for v in dataEmployee:
                if v['name'] in employeesRenovation and v['name'] not in employeesDownloaded:
                    employeesNotDownloaded.append(v)

            return {
                "status": True,
                "restriction": not (1 <= int(numberDay) <= 4),
                "employees": employeesNotDownloaded
            }
    return {
        "status": True,
        "restriction": not (1 <= int(numberDay) <= 4),
        "employees": []
    }

@frappe.whitelist(allow_guest=True)
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
    # if anio is not None and mes is None:
    #     where += f"AND emp.fecha_de_consolidado BETWEEN '{anio}-01-01' AND '{anio}-12-{ultimo_dia}' "
    #     whereHoraExtra += f"AND hr.año = '{anio}' "
    #
    # if mes is not None and anio is None:
    #     where += f"AND emp.fecha_de_consolidado BETWEEN '2019-{mes}-01' AND '2024-{mes}-{ultimo_dia}' "
    #     whereHoraExtra += f"AND hr.mes = '{mesString}' "

    if anio is not None and mes is not None:
        whereHoraExtra += f"AND hr.año = '{anio}' AND hr.mes = '{mesString}' "

    if empleadito is not None:
        where += f"AND emp.employee = '{empleadito}' "

    if sucursal is not None:
        where += f"AND emp.sucursal = '{sucursal}' "

    if department is not None:
        where += f"AND emp.departamento = '{department}' "

    # where += f"AND (emp.late_time IS NOT NULL OR emp.overtime_time IS NOT NULL AND emp.fecha_de_consolidado > '2024-03-19')"

    sqlConsulta = f"""
        SELECT
            emp.employee, emp.late_time, emp.overtime_time, emp.employee_name, emp.creation, emp.fecha_de_consolidado
        FROM
            `tabEmployee Checkin` as emp
        WHERE (emp.fecha_de_consolidado BETWEEN '{anio}-{mes}-01' AND '{anio}-{mes}-{ultimo_dia}')
        AND (emp.late_time != "" OR emp.overtime_time != "")
        AND (emp.creation > '2024-03-20 23:59:00') {where}
    """



    dataCheckin = frappe.db.sql(sqlConsulta, as_dict=True)
    if dataCheckin is None or len(dataCheckin) == 0:
        return []
    empleado = []
    empleadoArray = {}
    hora = 0
    minuto = 0
    hora2 = 0
    minuto2= 0
    total = 0
    prueba = []
    for element in dataCheckin:

        if element["overtime_time"] is None or element["overtime_time"] == "":
            element["overtime_time"] = "0"

        if element["late_time"] is None or element["late_time"] == "":
            element["late_time"] = "0"

        late_time = element["late_time"]

        if ":" in late_time:
            h, m = map(int, element["late_time"].split(':'))
            hora = h
            minuto = m
            hora += minuto // 60
            minuto %= 60
        else:
            hora = int(late_time) // 60
            minuto = 9
        minutos_total = hora * 60 + minuto
        hora_final = '{:02d}:{:02d}'.format(hora, minuto)
        element["late_time"] = hora_final if element["late_time"] else 0
        element["overtime_time"] = int(element["overtime_time"])

        if element["employee"] not in empleado:
            empleado.append(element["employee"])
            empleadoArray[element["employee"]] = element

        else:

            if ":" in late_time:
                h, m = map(int, empleadoArray[element["employee"]]["late_time"].split(':'))
                hora2 = h
                minuto2 = m

                hora2 += minuto2 // 60
                minuto2 %= 60
            else:
                hora = int(late_time) // 60
                minuto = 9
            hora_final2 = '{:02d}:{:02d}'.format(hora2, minuto2)

            hora_final_minutos = int(hora_final.split(':')[0]) * 60 + int(hora_final.split(':')[1])
            hora_final2_minutos = int(hora_final2.split(':')[0]) * 60 + int(hora_final2.split(':')[1])

            suma_minutos = hora_final_minutos + hora_final2_minutos

            suma_horas = suma_minutos // 60
            suma_minutos = suma_minutos % 60
            hora_final_sumada = '{:02d}:{:02d}'.format(suma_horas, suma_minutos)

            empleadoArray[element["employee"]]["late_time"] = hora_final_sumada
            empleadoArray[element["employee"]]["overtime_time"] += int(element["overtime_time"])

    if len(empleado) >0:
        empleado = "(" + ", ".join(["'" + e + "'" for e in empleado]) + ")"
    else:
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


@frappe.whitelist(allow_guest=True)
def resumenHorariosDiario(fecha="", empleado=None, sucursal=None, department=None):
    # fecha = datetime.strptime(fecha, "%Y-%m-%d")

    # fechanew = datetime.strptime(fecha, "%d-%m-%Y")
    # fecha = fechanew.strftime("%Y-%m-%d")
    where = ""
    if fecha is None:
        return []

    if fecha is not None:
        where += f"AND emp.fecha_de_consolidado = '{fecha}'"


    if empleado is not None:
        where += f"AND emp.employee = '{empleado}' "
    #
    if sucursal is not None:
        where += f"AND emp.sucursal = '{sucursal}' "

    if department is not None:
        where += f"AND emp.departamento = '{department}' "

    # where += f"AND (emp.late_time IS NOT NULL OR emp.overtime_time IS NOT NULL )"

    sqlConsulta = f"""
        SELECT
            emp.employee, emp.late_time, emp.overtime_time, emp.employee_name, emp.fecha_de_consolidado, emp.time, emp.log_type
        FROM
            `tabEmployee Checkin` as emp
        WHERE 1=1 {where}
    """


    dataCheckin = frappe.db.sql(sqlConsulta, as_dict=True)
    if len(dataCheckin) == 0:
        return []

    empleado = []
    empleadoArray = {}


    for element in dataCheckin:
        if element["overtime_time"] is None:
            element["overtime_time"] = 0
        if element["late_time"] is None:
            element["late_time"] = 0
        plantilla = {
            "employee": "",
            "employee_name": "",
            "entrada": "",
            "inicio_almuerzo": "",
            "fin_almuerzo": "",
            "salida":"",
            "tardanza": 0,
            "horasExtrasReal": 0
        }
        if element["employee"] not in empleadoArray:
            empleado.append(element["employee"])
            plantilla["employee"] = element["employee"]
            plantilla["employee_name"] = element["employee_name"]
            if element["log_type"] == "Entrada":
                plantilla["entrada"] = element["time"]
                plantilla["tardanza"] = element["late_time"]
            if element["log_type"] == "Salida Refrigerio":
                plantilla["inicio_almuerzo"] = element["time"]
            if element["log_type"] == "Llegada Refrigerio":
                plantilla["fin_almuerzo"] = element["time"]
            if element["log_type"] == "Salida":
                plantilla["salida"] = element["time"]
                plantilla["horasExtrasReal"] = element["overtime_time"]

            empleadoArray[element["employee"]] = plantilla
        else:
            if element["log_type"] == "Entrada":
                empleadoArray[element["employee"]]["entrada"] = element["time"]
                empleadoArray[element["employee"]]["tardanza"] = element["late_time"]
            if element["log_type"] == "Salida Refrigerio":
                empleadoArray[element["employee"]]["inicio_almuerzo"] = element["time"]
            if element["log_type"] == "Llegada Refrigerio":
                empleadoArray[element["employee"]]["fin_almuerzo"] = element["time"]
            if element["log_type"] == "Salida":
                empleadoArray[element["employee"]]["salida"] = element["time"]
                empleadoArray[element["employee"]]["horasExtrasReal"] = element["overtime_time"]

    parametros_sql = ', '.join(['%s'] * len(empleado))

    consultaEmployee = f"""
        SELECT
            hr.name, hr.employment_type, hr.default_shift, br.start_time, br.end_time
        FROM
            `tabEmployee` as hr
        LEFT JOIN `tabShift Type` br on hr.default_shift = br.name
        WHERE hr.name IN ({parametros_sql}) 
    """

    dataEmployee = frappe.db.sql(consultaEmployee, tuple(empleado), as_dict=True)
    for element in dataEmployee:
        turnoEntrada = ""
        turnoSalida = ""
        if element["name"] in empleadoArray:
            if element["default_shift"] is not None:
                turnoEntrada = element["start_time"]
                turnoSalida = element["end_time"]

            empleadoArray[element["name"]]["employment_type"] = element["employment_type"]
            empleadoArray[element["name"]]["turnoEntrada"] = turnoEntrada
            empleadoArray[element["name"]]["turnoSalida"] = turnoSalida

    empleadoArray = empleadoArray.values()
    return empleadoArray

def validate_data_format(data):
    for row in data:
        if not isinstance(row, (list, tuple)):
            raise TypeError(f"Invalid row type: {type(row)}. Each row must be a list or tuple.")

@frappe.whitelist()
def download_excel_attendance_sebas(month="", year="", branch=""):
    from frappe.utils.xlsxutils import build_xlsx_response_sebas

    months = {"Enero": "01","Febrero": "02","Marzo": "03","Abril": "04","Mayo": "05", "Junio": "06","Julio": "07","Agosto": "08","Setiembre": "09","Octubre": "10","Noviembre": "11","Diciembre": "12"}
    current_date = date.today()
    current_month_number = current_date.month
    current_year_number = current_date.year
    current_day_number = current_date.day
    month_number_selected = int(months[month])
    year_number_selected = int(year)

    if month_number_selected == current_month_number and year_number_selected == current_year_number:
        date_selected = datetime(year_number_selected, month_number_selected, 1)
        date_aux = datetime(year_number_selected, month_number_selected, current_day_number)
        date_init = date_selected.strftime('%Y-%m-%d')
        date_end = date_aux
    else:
        date_selected = datetime(year_number_selected, month_number_selected, 1)
        date_aux = datetime(year_number_selected, month_number_selected, 1) + relativedelta(months=1)
        date_init = date_selected.strftime('%Y-%m-%d')
        date_end = date_aux - relativedelta(days=1)

    values_employee_active = {
        'branch': branch,
        'status': 'Inactive'
    }
    list_employee_active = frappe.db.sql("""
		SELECT
			st.name,
			st.nombre_completo,
			st.branch,
			st.department,
			st.fecha_de_ingreso_real,
			st.fecha_de_relevo,
			st.status
		FROM
			`tabEmployee` AS st
		WHERE
			st.branch = %(branch)s AND st.status != %(status)s
	""", values=values_employee_active, as_dict=True)

    values_employee_inactive = {
        'branch': branch,
        'date_init': date_init,
        'date_end': date_end.strftime('%Y-%m-%d'),
        'status': 'Inactive'
    }
    list_employee_inactive = frappe.db.sql("""
		SELECT
			st.name,
			st.nombre_completo,
			st.branch,
			st.department,
			st.fecha_de_ingreso_real,
			st.fecha_de_relevo,
			st.status
		FROM
			`tabEmployee` AS st
		WHERE
			st.branch = %(branch)s AND st.status = %(status)s AND st.fecha_de_relevo BETWEEN %(date_init)s AND %(date_end)s
	""", values=values_employee_inactive, as_dict=True)

    list_all_employee = list_employee_inactive + list_employee_active

    if len(list_all_employee) == 0:
        return {
            'status': False,
            'message': 'No hay empleados para esta agencia'
        }

    array_name_employee = []

    for employee in list_all_employee:
        array_name_employee.append(employee.name)

    values_attendance = {
        'employee': array_name_employee,
        'docstatus': 1,
        'date_init': date_init,
        'date_end': date_end.strftime('%Y-%m-%d')
    }
    list_attendance = frappe.db.sql("""
		SELECT
			st.name,
			st.employee,
			st.attendance_date,
			st.status,
			st.leave_type
		FROM
			`tabAttendance` AS st
		WHERE
			st.employee IN %(employee)s AND st.docstatus = %(docstatus)s AND
            st.attendance_date Between %(date_init)s and %(date_end)s
	""", values=values_attendance, as_dict=True)

    values_checking = {
        'employee': array_name_employee,
        'date_init': date_init,
        'date_end': date_end
    }
    list_checking = frappe.db.sql("""
		SELECT
			st.name,
			st.employee,
			st.log_type,
			st.time,
			st.fecha_de_consolidado
		FROM
			`tabEmployee Checkin` AS st
		WHERE
			st.employee IN %(employee)s AND
            st.fecha_de_consolidado Between %(date_init)s and %(date_end)s
	""", values=values_checking, as_dict=True)

    values_hours = {
        'user_id': array_name_employee,
        'date_init': date_init,
        'date_end': date_end
    }
    list_hours = frappe.db.sql("""
		SELECT
			st.name,
			st.user_id,
			st.hours,
			st.date
		FROM
			`tabMarcaciones` AS st
		WHERE
			st.user_id IN %(user_id)s AND
            st.date Between %(date_init)s and %(date_end)s
	""", values=values_hours, as_dict=True)

    values_sunday_and_holidays = {
        'parent': 'FERIADOS 2022',
        'date_init': date_init,
        'date_end': date_end
    }
    list_sunday_and_holidays = frappe.db.sql("""
		SELECT
			st.holiday_date,
			st.description
		FROM
			`tabHoliday` AS st
		WHERE
			st.parent = %(parent)s AND
            st.holiday_date Between %(date_init)s and %(date_end)s
	""", values=values_sunday_and_holidays, as_dict=True)

    grouped_sunday = []
    grouped_holidays = []

    for value in list_sunday_and_holidays:
        if value['description'] == 'Sunday':
            if value['holiday_date'] not in grouped_sunday:
                grouped_sunday.append(value['holiday_date'])
        else:
            if value['holiday_date'] not in grouped_holidays:
                grouped_holidays.append(value['holiday_date'])

    grouped_checking = {}
    for entry in list_checking:
        fecha = str(entry["fecha_de_consolidado"])
        employee = entry["employee"]
        log_type = entry["log_type"]

        if fecha not in grouped_checking:
            grouped_checking[fecha] = {}

        if employee not in grouped_checking[fecha]:
            grouped_checking[fecha][employee] = {}

        if log_type not in grouped_checking[fecha][employee]:
            grouped_checking[fecha][employee][log_type] = []

        grouped_checking[fecha][employee][log_type] = entry

    grouped_attendance = {}
    for attendance in list_attendance:
        fecha = str(attendance["attendance_date"])
        employee = attendance["employee"]

        if fecha not in grouped_attendance:
            grouped_attendance[fecha] = {}

        if employee not in grouped_attendance[fecha]:
            grouped_attendance[fecha][employee] = []

        grouped_attendance[fecha][employee] = attendance

    grouped_hours = {}
    for hour in list_hours:
        fecha = str(hour["date"])
        employee = hour["user_id"]

        if fecha not in grouped_hours:
            grouped_hours[fecha] = {}

        if employee not in grouped_hours[fecha]:
            grouped_hours[fecha][employee] = []

        grouped_hours[fecha][employee] = hour

    days_list = []
    data_count = 1

    while date_selected <= date_end:
        days_list.append(date_selected.strftime('%Y-%m-%d'))
        date_selected += timedelta(days=1)

    dic_status = {
        "Holidays": "H",
        "Sunday": "WO",
        "On Leave": "VACACIONES",
        "DM Observado": "DMO",
        'VACACIONES': 'VAC',
        'LICENCIA SIN GOCE': 'LSG',
        'COMPENSATORIO': 'COM',
        'LICENCIA CON GOCE': 'LCG',
        'DESCANSO MEDICO': 'DME',
        'PERMISO OCACIONAL': 'L-PO',
        'SUBSIDIO': 'LS',
        'SUBSIDIO POR ENFERMEDAD': 'SXE',
        'SUBSIDIO POR MATERNIDAD': 'SXM',
        'SUBSIDIO POR ACCIDENTE': 'SXA',
        'LICENCIA POR FALLECIMIENTO': 'LXF',
        'LICENCIA POR PATERNIDAD': 'LXP',
        'Present': 'P',
        'Absent': 'A',
        'Half Day': 'HD',
        'Work From Home': 'MI',
        'Marcacion Incompleta': 'MI'

    }

    data_values = []
    for employee in list_all_employee:
        fecha_relevo = None
        if employee['fecha_de_relevo'] is not None:
            fecha_relevo = employee['fecha_de_relevo']

        for day in days_list:
            day_format = datetime.strptime(day, '%Y-%m-%d')

            if employee['fecha_de_relevo'] is not None and day_format.date() <= fecha_relevo:
                break

            join = ''
            join_lunch = ''
            leave_lunch = ''
            leave = ''
            status_attendance = 'NM'
            extra_hours = '0'

            if day in grouped_checking and employee['name'] in grouped_checking[day]:
                if 'Entrada' in grouped_checking[day][employee['name']]:
                    join = grouped_checking[day][employee['name']]['Entrada']['time']

            if day in grouped_checking and employee['name'] in grouped_checking[day]:
                if 'Salida Refrigerio' in grouped_checking[day][employee['name']]:
                    join_lunch = grouped_checking[day][employee['name']]['Salida Refrigerio']['time']

            if day in grouped_checking and employee['name'] in grouped_checking[day]:
                if 'Llegada Refrigerio' in grouped_checking[day][employee['name']]:
                    leave_lunch = grouped_checking[day][employee['name']]['Llegada Refrigerio']['time']

            if day in grouped_checking and employee['name'] in grouped_checking[day]:
                if 'Salida' in grouped_checking[day][employee['name']]:
                    leave = grouped_checking[day][employee['name']]['Salida']['time']

            if day in grouped_attendance and employee['name'] in grouped_attendance[day]:
                status_attendance = grouped_attendance[day][employee['name']]['status']

                if status_attendance in dic_status:
                    if status_attendance == 'On Leave':
                        status_attendance = dic_status[grouped_attendance[day][employee['name']]['leave_type']]

                    else:
                        status_attendance = dic_status[status_attendance]

            if day in grouped_hours and employee['name'] in grouped_hours[day]:
                extra_hours = grouped_hours[day][employee['name']]['hours']

            if day_format.date() in grouped_holidays:
                status_attendance = '*H*'
            elif day_format.date() in grouped_sunday:
                status_attendance = 'WO'

            data_employee = []
            data_employee.append(data_count)
            data_employee.append(employee['name'])
            data_employee.append(employee['nombre_completo'])
            data_employee.append(employee['branch'])
            data_employee.append(employee['department'])
            data_employee.append(employee['fecha_de_ingreso_real'])
            data_employee.append(fecha_relevo if fecha_relevo is not None else '')
            data_employee.append(day)
            data_employee.append(join)
            data_employee.append(join_lunch)
            data_employee.append(leave_lunch)
            data_employee.append(leave)
            data_employee.append(status_attendance)
            data_employee.append(extra_hours)
            data_values.append(data_employee)
            data_count += 1

    data_head = ['NRO','IDENTIFICADOR','APELLIDOS Y NOMBRES','AGENCIA','DEPARTAMENTO','FECHA DE INGRESO REAL','FECHA DE CESE O RELEVO','DIA','H. INGRESO','H. SALIDA REFRIGERIO','H. INGRESO REFRIGERIO','H. SALIDA','TIPO DE ASISTENCIA O LICENCIA','HORAS EXTRAS']
    data = [data_head] + data_values

    # Validar formato de datos
    validate_data_format(data)

    title = "Asistencia " + month + " " + year
    build_xlsx_response_sebas(data, title)