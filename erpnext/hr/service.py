import requests
import numpy as np
import json
import frappe

@frappe.whitelist(allow_guest=True)
def get_database():
    responseData = dict()
    filters = frappe.form_dict.filters
    where = frappe.form_dict.where
    select_query = frappe.form_dict.sql_query
    tables = frappe.form_dict.tables
    values = json.loads(filters)
    try:
        where_global = "WHERE "+where

        if len(values)==0:
            where_global = where

        data = frappe.db.sql("""SELECT """+ select_query +""" FROM """+ tables +""" """+ where_global, values=values, as_dict=1)
        responseData["data"] = data
        responseData["msn"] = "Exito"
        responseData["status"] = True
        frappe.response['response'] =  responseData
    except Exception as e:
        responseData["msn"] = "Ocurrió un error en la consulta, verifique su query"
        responseData["msn2"] = e
        responseData["status"] = False
        frappe.response['response'] =  responseData