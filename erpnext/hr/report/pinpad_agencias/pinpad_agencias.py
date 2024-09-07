# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
import requests
from requests.adapters import HTTPAdapter, Retry


def execute(filters=None):
    columns, data = [], []
    supervisor = requests.get("https://syslima.shalomcontrol.com/reports/report_pinpad_agencias")
    supervisor = supervisor.json()
    return get_columns(), supervisor


def get_columns():
    columns = [
        {
            'label': "CODIGO DE AGENCIA",
            'fieldname': 'ter_id',
            'fieldtype': 'Data',
            'width': 120
        },
        {
            'label': "AGENCIA",
            'fieldname': 'ter_nombre',
            'fieldtype': 'Data',
            'width': 300
        },
        {
            'label': "CODIGO DE COMERCIO",
            'fieldname': 'codigo_comercio',
            'fieldtype': 'Data',
            'width': 300,
        },
        {
            'label': "CANTIDAD DE PINPADS",
            'fieldname': 'qty_pinpad',
            'fieldtype': 'Data',
            'width': 120,
        },
        {
            'label': "CANTIDAD DE USUARIOS PARA PINPAD",
            'fieldname': 'qty_user_pinpad',
            'fieldtype': 'Data',
            'width': 120
        },
    ]

    return columns
