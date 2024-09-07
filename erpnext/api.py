
import requests
import json
import datetime
import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime


@frappe.whitelist(allow_guest=True)
def list():
    filters = frappe.form_dict.filters
    where = frappe.form_dict.where
    select_query = frappe.form_dict.sql_query
    tables = frappe.form_dict.tables
    values = json.loads(filters)

    responseData = dict()
    where_global = f"WHERE {where}" if where else ""

    try:
        data = frappe.db.sql("""SELECT """ + select_query + """ FROM """ + tables + """ """ + where_global, values=values, as_dict=1)
        responseData["data"] = data
        responseData["msn"] = "Exito"
        responseData["status"] = True
    except frappe.db.Error as e:
        responseData["msn"] = "Database error occurred."
        responseData["msn2"] = str(e)  # Consider providing more specific error details
        responseData["status"] = False
    except Exception as e:  # Catch other potential exceptions
        responseData["msn"] = "An unexpected error occurred."
        responseData["msn2"] = str(e)
        responseData["status"] = False

    frappe.response['response'] = responseData

def searchDoctype(data=None):

    responseData = dict()

    try:
        if data is None or data== "":
            responseData["msn"] = 'Error. ingresar data.'
            responseData["status"] = False
            return responseData

        data_search = frappe.db.sql("select * from `tabDriver` where docstatus!=2",as_dict=True)

        if len(data_search)>0:
            responseData["msn"] = 'Driver.'
            responseData["data"] = data_search
            responseData["status"] = True
        else:
            responseData["msn"] = 'No hay registros.'
            responseData["status"] = False

        return responseData

    except Exception as e:
        responseData["msn"] = e
        responseData["status"] = False
        return responseData