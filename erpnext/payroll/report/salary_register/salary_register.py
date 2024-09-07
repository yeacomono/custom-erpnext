# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe, erpnext
from frappe.utils import flt
from frappe import _
from datetime import datetime
from datetime import date
from builtins import len
from builtins import float
from builtins import round

def get_columns():
	columns = [
		{
			'fieldtype': "Link",
			'options': "Salary Slip",
			'label': _("ID DE NOMINA"),
			'fieldname': "id_nomina",
			'width': 150
		},
		{
			'fieldtype': "Link",
			'options': "Employee",
			'label': _("EMPLEADO"),
			'fieldname': "id_employee",
			'width': 120
		},
		{
			'fieldtype': "Data",
			'label': _("NOMBRE DE EMPLEADO"),
			'fieldname': "nameEmployee",
			'width': 140
		},
		{
			'label': _("DNI"),
			'fieldname': 'documento_identidad',
			'fieldtype': 'Data',
			'width': 100
		},
		_("SUCURSAL") + ":Link/Branch:-1",
		{
			'label': _("ID SUCURSAL"),
			'fieldname': 'id_sucursal',
			'fieldtype': 'Data',
			'width': 100
		},
		{
			'label': _("ZONA"),
			'fieldname': 'zona',
			'fieldtype': 'Data',
			'width': 100
		},
		{
			'label': _("SNP/SPP"),
			'fieldname': 'fondo_de_pensiones',
			'fieldtype': 'Data',
			'width': 120
		},
		{
			'label': _("FECHA DE INGRESO"),
			'fieldname': 'fecha_ingreso',
			'fieldtype': 'Data',
			'width': 100
		},
		{
			'label': _("JORNAL DIARIO"),
			'fieldname': 'jornal_diario',
			'fieldtype': 'Float',
			'width': 100
		},
		{
			'label': _("DIAS DEL MES"),
			'fieldname': 'dias_del_mes',
			'fieldtype': 'Float',
			'width': 100
		},
		{
			'label': _("DIAS LABORADOS"),
			'fieldname': 'dias_laborados',
			'fieldtype': 'Float',
			'width': 100
		},
		{
			'label': _("DIAS NO LABORADOS"),
			'fieldname': 'dias_no_laborados',
			'fieldtype': 'Float',
			'width': 100
		},
		{
			'label': _("FERIADO"),
			'fieldname': 'feriados_laborados',
			'fieldtype': 'Float',
			'width': 100
		},
		{
			'label': _("VACACIONES"),
			'fieldname': 'dias_vaciones',
			'fieldtype': 'Float',
			'width': 100
		},
		{
			'label': _("CANTIDAD DESCANSO MEDICO"),
			'fieldname': 'cant_descanso_medico',
			'fieldtype': 'Float',
			'width': 100
		},
		{
			'label': _("HORAS EXTRAS 25%"),
			'fieldname': 'n_horas_extras_25',
			'fieldtype': 'Float',
			'width': 100
		},
		{
			'label': _("HORAS EXTRAS 35%"),
			'fieldname': 'n_horas_extras_35',
			'fieldtype': 'Float',
			'width': 100
		},
		{
			'label': _("HORAS EXTRAS 100%"),
			'fieldname': 'n_horas_extras_100',
			'fieldtype': 'Float',
			'width': 100
		},
		{
			'label': _("HORAS EXTRAS FERIADO"),
			'fieldname': 'horas_extras_feriado',
			'fieldtype': 'Float',
			'width': 100
		},
		{
			'label': _("HORAS NOCTURNAS"),
			'fieldname': 'n_horas_nocturnas',
			'fieldtype': 'Float',
			'width': 100
		},
		{
			'label': _("SUBSIDIO"),
			'fieldname': 'subsidio',
			'fieldtype': 'Float',
			'width': 100
		},
		{
			'label': _("HORAS TRABAJAS"),
			'fieldname': 'horas_trabajadas',
			'fieldtype': 'Float',
			'width': 100
		},
		{
			'label': _("LICENCIA CON GOCE"),
			'fieldname': 'licencia_con_goce',
			'fieldtype': 'Float',
			'width': 100
		},
		{
			'label': _("LICENCIA POR PATERNIDAD"),
			'fieldname': 'licencia_por_paternida',
			'fieldtype': 'Float',
			'width': 100
		},
		{
			'label': _("LICENCIA POR FALLECIMIENTO"),
			'fieldname': 'licencia_por_fallecimiento',
			'fieldtype': 'Float',
			'width': 100
		},
		{
			'label': _("LICENCIA SIN GOCE"),
			'fieldname': 'licencia_sin_goce',
			'fieldtype': 'Float',
			'width': 100
		},
		{
			'label': _("REMUNERACIÓN BASICA"),
			'fieldname': 'remuneracion_basica',
			'fieldtype': 'Float',
			'width': 100
		},
		{
			'label': _("VACACIONES"),
			'fieldname': 'vacaciones',
			'fieldtype': 'Float',
			'width': 100
		},
		{
			'label': _("DESCANSO MEDICO"),
			'fieldname': 'descanso_medico',
			'fieldtype': 'Float',
			'width': 100
		},
		{
			'label': _("ASIGNACION FAMILIAR"),
			'fieldname': 'asignacion_familiar',
			'fieldtype': 'Float',
			'width': 100
		},
		{
			'label': _("OTROS INGRESOS"),
			'fieldname': 'apoyos',
			'fieldtype': 'Float',
			'width': 100
		},
		{
			'label': _("HORAS EXTRAS"),
			'fieldname': 'horas_extras',
			'fieldtype': 'Float',
			'width': 100
		},
		{
			'label': _("DOMINGOS O DIAS DE DESCANSO"),
			'fieldname': 'domingos_feriados',
			'fieldtype': 'Float',
			'width': 100
		},
		{
			'label': _("FERIADOS"),
			'fieldname': 'feriados',
			'fieldtype': 'Float',
			'width': 100
		},
		{
			'label': _("HORAS NOCTURNAS"),
			'fieldname': 'horas_nocturnas',
			'fieldtype': 'Float',
			'width': 100
		},
		{
			'label': _("MOVILIDAD"),
			'fieldname': 'movilidad',
			'fieldtype': 'Float',
			'width': 100
		},
		{
			'label': _("MOVILIDAD VARIABLE"),
			'fieldname': 'movilidad_variable',
			'fieldtype': 'Float',
			'width': 100
		},
		{
			'label': _("GRATIFICACIÓN"),
			'fieldname': 'gratificacion_ear',
			'fieldtype': 'Float',
			'width': 100
		},
		{
			'label': _("BONIF. EXT 9%"),
			'fieldname': 'bonif_ext',
			'fieldtype': 'Float',
			'width': 100
		},
		{
			'label': _("VIATICOS"),
			'fieldname': 'viaticos_earn',
			'fieldtype': 'Float',
			'width': 100
		},
		{
			'label': _("VIATICOS INGRESO"),
			'fieldname': 'viaticos_entrada',
			'fieldtype': 'Float',
			'width': 100
		},
		{
			'label': _("BONIFICACION"),
			'fieldname': 'otros_ingresos',
			'fieldtype': 'Float',
			'width': 100
		},
		{
			'label': _("CONDICIONES DE TRABAJO"),
			'fieldname': 'condiciones_de_trabajo',
			'fieldtype': 'Data',
			'width': 200
		},
		{
			'label': _("TOTAL REMUNERACIÓN BRUTA"),
			'fieldname': 'total_bruta',
			'fieldtype': 'Float',
			'width': 100
		},
		{
			'label': _("SNP"),
			'fieldname': 'snp',
			'fieldtype': 'Float',
			'width': 100
		},
		{
			'label': _("AFP FONDO"),
			'fieldname': 'afp_fondo',
			'fieldtype': 'Float',
			'width': 100
		},
		{
			'label': _("AFP SEGURO"),
			'fieldname': 'afp_seguro',
			'fieldtype': 'Float',
			'width': 100
		},
		{
			'label': _("AFP COMISION"),
			'fieldname': 'afp_comision',
			'fieldtype': 'Float',
			'width': 100
		},
		{
			'label': _("TOTAL AFP"),
			'fieldname': 'total_afp',
			'fieldtype': 'Float',
			'width': 100
		},
		{
			'label': _("ADELANTO"),
			'fieldname': 'adelanto',
			'fieldtype': 'Float',
			'width': 100
		},
		{
			'label': _("RENTA 5TA"),
			'fieldname': 'renta',
			'fieldtype': 'Float',
			'width': 100
		},
		{
			'label': _("OTROS INGRESOS"),
			'fieldname': 'otros_ingresos_new',
			'fieldtype': 'Float',
			'width': 100
		},
		{
			'label': _("VIATICOS"),
			'fieldname': 'viaticos_ded',
			'fieldtype': 'Float',
			'width': 100
		},
		{
			'label': _("GRATIFICACIÓN"),
			'fieldname': 'gratificacion_ded',
			'fieldtype': 'Float',
			'width': 100
		},
		{
			'label': _("RIMAC"),
			'fieldname': 'rimac',
			'fieldtype': 'Float',
			'width': 100
		},
		{
			'label': _("RETENCIÓN JUDICIAL"),
			'fieldname': 'ret_judicial',
			'fieldtype': 'Float',
			'width': 100
		},
		{
			'label': _("E.P.P"),
			'fieldname': 'epp',
			'fieldtype': 'Float',
			'width': 100
		},
		{
			'label': _("OTROS DESCUENTOS"),
			'fieldname': 'otros_descuentos',
			'fieldtype': 'Float',
			'width': 100
		},
		{
			'label': _("TOTAL DESCUENTO"),
			'fieldname': 'total_descuento',
			'fieldtype': 'Float',
			'width': 100
		},
		{
			'label': _("REMUNERACIÓN NETA"),
			'fieldname': 'remuneracion_neta',
			'fieldtype': 'Float',
			'width': 100
		},
		{
			'label': _("ESSALUD"),
			'fieldname': 'essalud',
			'fieldtype': 'Float',
			'width': 100
		},
		{
			'label': _("VIDA LEY"),
			'fieldname': 'vida_ley',
			'fieldtype': 'Float',
			'width': 100
		},
		{
			'label': _("BANCO"),
			'fieldname': 'banco',
			'fieldtype': 'Data',
			'width': 200
		},
		{
			'label': _("CUENTA"),
			'fieldname': 'cuenta',
			'fieldtype': 'Data',
			'width': 200
		},
		{
			'label': _("FECHA DE NACIMIENTO"),
			'fieldname': 'fecha_de_nacimiento',
			'fieldtype': 'Data',
			'width': 200
		},
		{
			'label': _("SEXO"),
			'fieldname': 'sexo',
			'fieldtype': 'Data',
			'width': 200
		},
		{
			'label': _("NACIONALIDAD"),
			'fieldname': 'nacionalidad',
			'fieldtype': 'Data',
			'width': 200
		},
		{
			'label': _("ESTADO"),
			'fieldname': 'estado',
			'fieldtype': 'Data',
			'width': 200
		},
		{
			'label': _("CANASTA DE NAVIDAD"),
			'fieldname': 'canasta_de_navidad',
			'fieldtype': 'Float',
			'width': 200
		},
		{
			'label': _("BONIFICACION PERSONAL"),
			'fieldname': 'bonificacion_personal',
			'fieldtype': 'Float',
			'width': 200
		},
		{
			'label': _("CANTIDAD DE DIAS DE LICENCIA POR PATERNIDAD"),
			'fieldname': 'licencia_paternidad',
			'fieldtype': 'Int',
			'width': 200
		},
		{
			'label': _("CANTIDAD DE DIAS DE LICENCIA POR FALLECIMIENTO"),
			'fieldname': 'cantidad_licencia_por_fallecimiento',
			'fieldtype': 'Int',
			'width': 200
		},
		{
			'label': _("CANTIDAD DE DIAS DE LICENCIA CON GOCE"),
			'fieldname': 'licencia',
			'fieldtype': 'Int',
			'width': 200
		},
		{
			'label': _("CANTIDAD DE DIAS DE LICENCIA SIN GOCE"),
			'fieldname': 'es_una_licencia_sin_goce',
			'fieldtype': 'Int',
			'width': 200
		},
		{
			'label': _("TIPO DE DOCUMENTO"),
			'fieldname': 'tipo_de_documento',
			'fieldtype': 'Data',
			'width': 80
		},
		{
			'label': _("PUESTO"),
			'fieldname': 'designation',
			'fieldtype': 'Data',
			'width': 100
		},
		{
			'label': _("CANTIDAD DE DIAS DE AUSENCIA"),
			'fieldname': 'ausencias_reales',
			'fieldtype': 'Int',
			'width': 200
		},
		{
			'label': _("MONTO SUBSIDIO POR ACCIDENTE"),
			'fieldname': 'monto_subisidio_accidente',
			'fieldtype': 'Float',
			'width': 100
		},
		{
			'label': _("MONTO SUBSIDIO POR ENFERMEDAD"),
			'fieldname': 'monto_subisidio_enfermedad',
			'fieldtype': 'Float',
			'width': 100
		},
		{
			'label': _("MONTO SUBSIDIO POR MATERNIDAD"),
			'fieldname': 'monto_subisidio_maternidad',
			'fieldtype': 'Float',
			'width': 100
		},
		{
			'label': _("MONTO POR HORAS EXTRAS AL 25%"),
			'fieldname': 'h_25',
			'fieldtype': 'Float',
			'width': 100
		},
		{
			'label': _("MONTO POR HORAS EXTRAS AL 35%"),
			'fieldname': 'h_35',
			'fieldtype': 'Float',
			'width': 100
		},
		{
			'label': _("DESCUENTOS POR DIAS NO LABORADOS"),
			'fieldname': 'descuento_dias_not_working_5',
			'fieldtype': 'Float',
			'width': 200
		},
		]
	return columns

def execute(filters=None):
	if not filters: filters = {}
	currency = 'PEN'
	company_currency = erpnext.get_company_currency(filters.get("company"))
	salary_slips = get_salary_slips(filters, company_currency)

	if not salary_slips: return [], []

	columns = get_columns()
	ss_earning_map = get_ss_earning_map(salary_slips, currency, company_currency)
	ss_ded_map = get_ss_ded_map(salary_slips,currency, company_currency)
	data = []
	for ss in salary_slips:

		#EARNINGS QUE SI SE USAN
		remuneracion_component = 0 if ss_earning_map.get(ss.name, {}).get("HABER MENSUAL") is None else ss_earning_map.get(ss.name, {}).get("HABER MENSUAL")
		amount_licencia = 0 if ss_earning_map.get(ss.name, {}).get("LICENCIA CON GOCE") is None else ss_earning_map.get(ss.name, {}).get("LICENCIA CON GOCE")
		amount_licencia_paternidad = 0 if ss_earning_map.get(ss.name, {}).get("LICENCIA POR PATERNIDAD") is None else ss_earning_map.get(ss.name, {}).get("LICENCIA POR PATERNIDAD")
		amount_licencia_por_fallecimiento = 0 if ss_earning_map.get(ss.name, {}).get("LICENCIA POR FALLECIMIENTO") is None else ss_earning_map.get(ss.name, {}).get("LICENCIA POR FALLECIMIENTO")
		amount_licencias_sin_goce = 0 if ss_earning_map.get(ss.name, {}).get("LICENCIA SIN GOCE") is None else ss_earning_map.get(ss.name, {}).get("LICENCIA SIN GOCE")
		vacaciones = 0 if ss_earning_map.get(ss.name, {}).get("VACACIONES") is None else ss_earning_map.get(ss.name, {}).get("VACACIONES")
		descanso_medico = 0 if ss_earning_map.get(ss.name, {}).get("DESCANSO MEDICO") is None else ss_earning_map.get(ss.name, {}).get("DESCANSO MEDICO")
		monto_subisidio_accidente = 0 if ss_earning_map.get(ss.name, {}).get("SUBSIDIO POR ACCIDENTE") is None else ss_earning_map.get(ss.name, {}).get("SUBSIDIO POR ACCIDENTE")
		monto_subisidio_enfermedad = 0 if ss_earning_map.get(ss.name, {}).get("SUBSIDIO POR ENFERMEDAD") is None else ss_earning_map.get(ss.name, {}).get("SUBSIDIO POR ENFERMEDAD")
		monto_subisidio_maternidad = 0 if ss_earning_map.get(ss.name, {}).get("SUBSIDIO POR MATERNIDAD") is None else ss_earning_map.get(ss.name, {}).get("SUBSIDIO POR MATERNIDAD")
		asigna_f = 0 if ss_earning_map.get(ss.name, {}).get("ASIGNACION FAMILIAR") is None else ss_earning_map.get(ss.name, {}).get("ASIGNACION FAMILIAR")
		apoyos = 0 if ss_earning_map.get(ss.name, {}).get("OTROS INGRESOS") is None else ss_earning_map.get(ss.name, {}).get("OTROS INGRESOS")
		h_25 =  0 if ss_earning_map.get(ss.name, {}).get("HORAS EXTRAS 25") is None else ss_earning_map.get(ss.name, {}).get("HORAS EXTRAS 25")
		h_35 =  0 if ss_earning_map.get(ss.name, {}).get("HORAS EXTRAS 35") is None else ss_earning_map.get(ss.name, {}).get("HORAS EXTRAS 35")
		h_100 =  0 if ss_earning_map.get(ss.name, {}).get("HORAS EXTRAS 100") is None else ss_earning_map.get(ss.name, {}).get("HORAS EXTRAS 100")
		h_n =  0 if ss_earning_map.get(ss.name, {}).get("HORAS NOCTURNAS") is None else ss_earning_map.get(ss.name, {}).get("HORAS NOCTURNAS")
		movilidad = 0 if ss_earning_map.get(ss.name, {}).get("MOVILIDAD") is None else ss_earning_map.get(ss.name, {}).get("MOVILIDAD")
		movilidad_variable = 0 if ss_earning_map.get(ss.name, {}).get("MOVILIDAD VARIABLE") is None else ss_earning_map.get(ss.name, {}).get("MOVILIDAD VARIABLE")
		gratificacion_earn = 0 if ss_earning_map.get(ss.name, {}).get("GRATIFICACION") is None else ss_earning_map.get(ss.name, {}).get("GRATIFICACION")
		bonif = 0 if ss_earning_map.get(ss.name, {}).get("BONIF EXT 9%") is None else ss_earning_map.get(ss.name, {}).get("BONIF EXT 9%")
		viaticos_entrada = 0 if ss_earning_map.get(ss.name, {}).get("VIATICO INGRESO") is None else ss_earning_map.get(ss.name, {}).get("VIATICO INGRESO")
		otrs_ing = 0 if ss_earning_map.get(ss.name, {}).get("BONIFICACION") is None else ss_earning_map.get(ss.name, {}).get("BONIFICACION")
		feriados = 0 if ss_earning_map.get(ss.name, {}).get("FERIADOS") is None else ss_earning_map.get(ss.name, {}).get("FERIADOS")

		#DEDUCTIONS QUE SI SE USAN
		grat_ded = 0 if ss_ded_map.get(ss.name, {}).get("GRATIFICACION / BONIF 9%") is None else ss_ded_map.get(ss.name, {}).get("GRATIFICACION / BONIF 9%")
		sg_r = 0 if ss_ded_map.get(ss.name, {}).get("SEGUROS RIMAC") is None else ss_ded_map.get(ss.name, {}).get("SEGUROS RIMAC")
		ret_judicial = 0 if ss_ded_map.get(ss.name, {}).get("DESC ALIMENTOS") is None else ss_ded_map.get(ss.name, {}).get("DESC ALIMENTOS")
		epp = 0 if ss_ded_map.get(ss.name, {}).get("EPP") is None else ss_ded_map.get(ss.name, {}).get("EPP")
		otr_desc = 0 if ss_ded_map.get(ss.name, {}).get("OTROS DESCUENTOS") is None else ss_ded_map.get(ss.name, {}).get("OTROS DESCUENTOS")
		essalud = 0 if ss_ded_map.get(ss.name, {}).get("SEGURO SALUD") is None else ss_ded_map.get(ss.name, {}).get("SEGURO SALUD")
		vida_ley = 0 if ss_ded_map.get(ss.name, {}).get("VIDA LEY") is None else ss_ded_map.get(ss.name, {}).get("VIDA LEY")
		canasta_de_navidad = 0 if ss_earning_map.get(ss.name, {}).get("CANASTA DE NAVIDAD") is None else ss_earning_map.get(ss.name, {}).get("CANASTA DE NAVIDAD")
		bonificacion_personal = 0 if ss_earning_map.get(ss.name, {}).get("BONIFICACION PERSONAL") is None else ss_earning_map.get(ss.name, {}).get("BONIFICACION PERSONAL")
		snp = 0 if ss_ded_map.get(ss.name, {}).get("SNP") is None else ss_ded_map.get(ss.name, {}).get("SNP")
		afp_fondo = 0 if ss_ded_map.get(ss.name, {}).get("AFP FONDO") is None else ss_ded_map.get(ss.name, {}).get("AFP FONDO")
		afp_seguro = 0 if ss_ded_map.get(ss.name, {}).get("AFP SEGURO") is None else ss_ded_map.get(ss.name, {}).get("AFP SEGURO")
		afp_comision = 0 if ss_ded_map.get(ss.name, {}).get("AFP COMISION ERP") is None else ss_ded_map.get(ss.name, {}).get("AFP COMISION ERP")
		adelantos = 0 if ss_ded_map.get(ss.name, {}).get("ADELANTOS") is None else ss_ded_map.get(ss.name, {}).get("ADELANTOS")
		cat = 0 if ss_ded_map.get(ss.name, {}).get("5TA CAGEGORIA") is None else ss_ded_map.get(ss.name, {}).get("5TA CAGEGORIA")
		otros_ingresos_new = 0 if ss_earning_map.get(ss.name, {}).get("OTROS INGRESOS") is None else ss_earning_map.get(ss.name, {}).get("OTROS INGRESOS")

		#FUNCION QUE TRAE INFO EXTRAS SI SE USA
		# viati = get_viaticos(ss.start_date,ss.employee)
		employees = get_employee(ss.employee)
		viat_earn = 0
		viat_ded = ss.viaticos
		hours_est = 0
		# if len(viati) > 0 :
		# 	viati = viati[0]
		# 	if viati.solo_entrada:
		# 		viat_ded = 0
		# 		viat_earn = viati.monto_total
		# 	else:
		# 		viat_earn = viati.monto_total
		# 		viat_ded = viati.monto_total

		feriados_trabajados = 0

		if employees[0].employment_type == "Jornada completa":
			hours_est = 8
			if ss.pago_por_2 != 0:
				residuo = hours_est % 8
				if residuo == 0:
					feriados_trabajados = ss.pago_por_2 // 8

		else:
			hours_est = 4
			if ss.pago_por_2 != 0:
				residuo = hours_est % 4
				if residuo == 0:
					feriados_trabajados = ss.pago_por_2 // 4

		#ESTO SI SE USA OPERACIONES CON DATA
		descuentos_dias_no_laborados = round((((employees[0].remuneracion_mensual + asigna_f ) / ss.total_working_days) * ss.ausencias_reales),2)
		days_not_worked = round((ss.total_working_days - ss.payment_days), 2) if round((ss.total_working_days - ss.payment_days), 2) > 0 else 0
		subsidy = ss.subsidio_por_maternidad + ss.subsidio_accidente + ss.subsidio_enfermedad
		hours_working = ss.payment_days * hours_est
		id_sucursal = employees[0].id_sucursal if ss.id_sucursal is None else ss.id_sucursal
		hours = h_25 + h_35
		hours = round(hours,2)
		viat_earn = viat_ded
		jornal_diary = round((float(employees[0].remuneracion_mensual) / float(ss.total_working_days)),2)
		totals_afp = afp_fondo + afp_seguro + afp_comision
		totals = epp + otr_desc + ret_judicial + sg_r + grat_ded + viat_ded + cat + otros_ingresos_new + adelantos + totals_afp + snp + canasta_de_navidad + bonificacion_personal
		totals = round(totals,2)

		row = [
			ss.name,
			ss.employee,
			ss.employee_name,
			ss.documento_identidad,
			ss.branch,
			id_sucursal,
			employees[0].zona_recursos,
			employees[0].fondo_de_pensiones,
			ss.fecha_ingreso,
			jornal_diary,
			ss.total_working_days,
			ss.payment_days,
			days_not_worked,
			feriados_trabajados,
			ss.dias_vaciones,
			ss.descanso_medico,
			ss.n_horas_extras_25,
			ss.n_horas_extras_35,
			ss.n_horas_extras_100,
			ss.pago_horas_extras_feriado,
			ss.n_horas_nocturnas,
			subsidy,
			hours_working,
			amount_licencia,
			amount_licencia_paternidad,
			amount_licencia_por_fallecimiento,
			amount_licencias_sin_goce,
			remuneracion_component,
			vacaciones,
			descanso_medico,
			asigna_f,
			apoyos,
			hours,
			h_100,
			feriados,
			h_n,
			movilidad,
			movilidad_variable,
			gratificacion_earn,
			bonif,
			viat_earn,
			viaticos_entrada,
			otrs_ing,
			employees[0].condiciones_de_trabajo if employees[0].condiciones_de_trabajo else "",
			ss.gross_pay,
			snp,
			afp_fondo,
			afp_seguro,
			afp_comision,
			totals_afp,
			adelantos,
			cat,
			otros_ingresos_new,
			viat_ded,
			grat_ded,
			sg_r,
			ret_judicial,
			epp,
			otr_desc,
			totals,
			ss.net_pay,
			essalud,
			vida_ley,
			employees[0].bank_name,
			employees[0].bank_ac_no,
			employees[0].date_of_birth,
			employees[0].gender,"PERUANA" if employees[0].tipo_de_documento == "DNI" else "EXTRANJERA",
			employees[0].status,
			canasta_de_navidad,
			bonificacion_personal,
			ss.licencia_paternidad,
			ss.licencia_por_fallecimiento,
			ss.licencia,
			ss.es_una_licencia_sin_goce,
			ss.tipo_de_documento,
			ss.designation,
			ss.ausencias_reales,
			monto_subisidio_accidente,
			monto_subisidio_enfermedad,
			monto_subisidio_maternidad,
			h_25,
			h_35,
			descuentos_dias_no_laborados
		]

		if ss.branch is not None: columns[4] = columns[4].replace('-1','121')
		data.append(row)

	return columns, data

@frappe.whitelist(allow_guest=True)
def salary_register_cloud():
	filters = frappe.form_dict.filters
	if not filters: filters = {}
	currency = 'PEN'
	company_currency = erpnext.get_company_currency(filters.get("company"))
	salary_slips = get_salary_slips(filters, company_currency)

	if not salary_slips: return [], []

	columns = get_columns()
	ss_earning_map = get_ss_earning_map(salary_slips, currency, company_currency)
	ss_ded_map = get_ss_ded_map(salary_slips,currency, company_currency)
	data = []
	for ss in salary_slips:

		#EARNINGS QUE SI SE USAN
		remuneracion_component = 0 if ss_earning_map.get(ss.name, {}).get("HABER MENSUAL") is None else ss_earning_map.get(ss.name, {}).get("HABER MENSUAL")
		amount_licencia = 0 if ss_earning_map.get(ss.name, {}).get("LICENCIA CON GOCE") is None else ss_earning_map.get(ss.name, {}).get("LICENCIA CON GOCE")
		amount_licencia_paternidad = 0 if ss_earning_map.get(ss.name, {}).get("LICENCIA POR PATERNIDAD") is None else ss_earning_map.get(ss.name, {}).get("LICENCIA POR PATERNIDAD")
		amount_licencia_por_fallecimiento = 0 if ss_earning_map.get(ss.name, {}).get("LICENCIA POR FALLECIMIENTO") is None else ss_earning_map.get(ss.name, {}).get("LICENCIA POR FALLECIMIENTO")
		amount_licencias_sin_goce = 0 if ss_earning_map.get(ss.name, {}).get("LICENCIA SIN GOCE") is None else ss_earning_map.get(ss.name, {}).get("LICENCIA SIN GOCE")
		vacaciones = 0 if ss_earning_map.get(ss.name, {}).get("VACACIONES") is None else ss_earning_map.get(ss.name, {}).get("VACACIONES")
		descanso_medico = 0 if ss_earning_map.get(ss.name, {}).get("DESCANSO MEDICO") is None else ss_earning_map.get(ss.name, {}).get("DESCANSO MEDICO")
		monto_subisidio_accidente = 0 if ss_earning_map.get(ss.name, {}).get("SUBSIDIO POR ACCIDENTE") is None else ss_earning_map.get(ss.name, {}).get("SUBSIDIO POR ACCIDENTE")
		monto_subisidio_enfermedad = 0 if ss_earning_map.get(ss.name, {}).get("SUBSIDIO POR ENFERMEDAD") is None else ss_earning_map.get(ss.name, {}).get("SUBSIDIO POR ENFERMEDAD")
		monto_subisidio_maternidad = 0 if ss_earning_map.get(ss.name, {}).get("SUBSIDIO POR MATERNIDAD") is None else ss_earning_map.get(ss.name, {}).get("SUBSIDIO POR MATERNIDAD")
		asigna_f = 0 if ss_earning_map.get(ss.name, {}).get("ASIGNACION FAMILIAR") is None else ss_earning_map.get(ss.name, {}).get("ASIGNACION FAMILIAR")
		apoyos = 0 if ss_earning_map.get(ss.name, {}).get("OTROS INGRESOS") is None else ss_earning_map.get(ss.name, {}).get("OTROS INGRESOS")
		h_25 =  0 if ss_earning_map.get(ss.name, {}).get("HORAS EXTRAS 25") is None else ss_earning_map.get(ss.name, {}).get("HORAS EXTRAS 25")
		h_35 =  0 if ss_earning_map.get(ss.name, {}).get("HORAS EXTRAS 35") is None else ss_earning_map.get(ss.name, {}).get("HORAS EXTRAS 35")
		h_100 =  0 if ss_earning_map.get(ss.name, {}).get("HORAS EXTRAS 100") is None else ss_earning_map.get(ss.name, {}).get("HORAS EXTRAS 100")
		h_n =  0 if ss_earning_map.get(ss.name, {}).get("HORAS NOCTURNAS") is None else ss_earning_map.get(ss.name, {}).get("HORAS NOCTURNAS")
		movilidad = 0 if ss_earning_map.get(ss.name, {}).get("MOVILIDAD") is None else ss_earning_map.get(ss.name, {}).get("MOVILIDAD")
		movilidad_variable = 0 if ss_earning_map.get(ss.name, {}).get("MOVILIDAD VARIABLE") is None else ss_earning_map.get(ss.name, {}).get("MOVILIDAD VARIABLE")
		gratificacion_earn = 0 if ss_earning_map.get(ss.name, {}).get("GRATIFICACION") is None else ss_earning_map.get(ss.name, {}).get("GRATIFICACION")
		bonif = 0 if ss_earning_map.get(ss.name, {}).get("BONIF EXT 9%") is None else ss_earning_map.get(ss.name, {}).get("BONIF EXT 9%")
		viaticos_entrada = 0 if ss_earning_map.get(ss.name, {}).get("VIATICO INGRESO") is None else ss_earning_map.get(ss.name, {}).get("VIATICO INGRESO")
		otrs_ing = 0 if ss_earning_map.get(ss.name, {}).get("BONIFICACION") is None else ss_earning_map.get(ss.name, {}).get("BONIFICACION")
		feriados = 0 if ss_earning_map.get(ss.name, {}).get("FERIADOS") is None else ss_earning_map.get(ss.name, {}).get("FERIADOS")

		#DEDUCTIONS QUE SI SE USAN
		grat_ded = 0 if ss_ded_map.get(ss.name, {}).get("GRATIFICACION / BONIF 9%") is None else ss_ded_map.get(ss.name, {}).get("GRATIFICACION / BONIF 9%")
		sg_r = 0 if ss_ded_map.get(ss.name, {}).get("SEGUROS RIMAC") is None else ss_ded_map.get(ss.name, {}).get("SEGUROS RIMAC")
		ret_judicial = 0 if ss_ded_map.get(ss.name, {}).get("DESC ALIMENTOS") is None else ss_ded_map.get(ss.name, {}).get("DESC ALIMENTOS")
		epp = 0 if ss_ded_map.get(ss.name, {}).get("EPP") is None else ss_ded_map.get(ss.name, {}).get("EPP")
		otr_desc = 0 if ss_ded_map.get(ss.name, {}).get("OTROS DESCUENTOS") is None else ss_ded_map.get(ss.name, {}).get("OTROS DESCUENTOS")
		essalud = 0 if ss_ded_map.get(ss.name, {}).get("SEGURO SALUD") is None else ss_ded_map.get(ss.name, {}).get("SEGURO SALUD")
		vida_ley = 0 if ss_ded_map.get(ss.name, {}).get("VIDA LEY") is None else ss_ded_map.get(ss.name, {}).get("VIDA LEY")
		canasta_de_navidad = 0 if ss_earning_map.get(ss.name, {}).get("CANASTA DE NAVIDAD") is None else ss_earning_map.get(ss.name, {}).get("CANASTA DE NAVIDAD")
		bonificacion_personal = 0 if ss_earning_map.get(ss.name, {}).get("BONIFICACION PERSONAL") is None else ss_earning_map.get(ss.name, {}).get("BONIFICACION PERSONAL")
		snp = 0 if ss_ded_map.get(ss.name, {}).get("SNP") is None else ss_ded_map.get(ss.name, {}).get("SNP")
		afp_fondo = 0 if ss_ded_map.get(ss.name, {}).get("AFP FONDO") is None else ss_ded_map.get(ss.name, {}).get("AFP FONDO")
		afp_seguro = 0 if ss_ded_map.get(ss.name, {}).get("AFP SEGURO") is None else ss_ded_map.get(ss.name, {}).get("AFP SEGURO")
		afp_comision = 0 if ss_ded_map.get(ss.name, {}).get("AFP COMISION ERP") is None else ss_ded_map.get(ss.name, {}).get("AFP COMISION ERP")
		adelantos = 0 if ss_ded_map.get(ss.name, {}).get("ADELANTOS") is None else ss_ded_map.get(ss.name, {}).get("ADELANTOS")
		cat = 0 if ss_ded_map.get(ss.name, {}).get("5TA CAGEGORIA") is None else ss_ded_map.get(ss.name, {}).get("5TA CAGEGORIA")
		otros_ingresos_new = 0 if ss_earning_map.get(ss.name, {}).get("OTROS INGRESOS") is None else ss_earning_map.get(ss.name, {}).get("OTROS INGRESOS")

		#FUNCION QUE TRAE INFO EXTRAS SI SE USA
		viati = get_viaticos(ss.start_date,ss.employee)
		employees = get_employee(ss.employee)
		viat_earn = 0
		viat_ded = 0
		hours_est = 0
		if len(viati) > 0 :
			viati = viati[0]
			if viati.solo_entrada:
				viat_ded = 0
				viat_earn = viati.monto_total
			else:
				viat_earn = viati.monto_total
				viat_ded = viati.monto_total

		feriados_trabajados = 0

		if employees[0].employment_type == "Jornada completa":
			hours_est = 8
			if ss.pago_por_2 != 0:
				residuo = hours_est % 8
				if residuo == 0:
					feriados_trabajados = ss.pago_por_2 // 8

		else:
			hours_est = 4
			if ss.pago_por_2 != 0:
				residuo = hours_est % 4
				if residuo == 0:
					feriados_trabajados = ss.pago_por_2 // 4

		#ESTO SI SE USA OPERACIONES CON DATA
		descuentos_dias_no_laborados = round((((employees[0].remuneracion_mensual + asigna_f ) / ss.total_working_days) * ss.ausencias_reales),2)
		days_not_worked = round((ss.total_working_days - ss.payment_days), 2) if round((ss.total_working_days - ss.payment_days), 2) > 0 else 0
		subsidy = ss.subsidio_por_maternidad + ss.subsidio_accidente + ss.subsidio_enfermedad
		hours_working = ss.payment_days * hours_est
		id_sucursal = employees[0].id_sucursal if ss.id_sucursal is None else ss.id_sucursal
		hours = h_25 + h_35
		hours = round(hours,2)
		viat_earn = viat_ded
		jornal_diary = round((float(employees[0].remuneracion_mensual) / float(ss.total_working_days)),2)
		totals_afp = afp_fondo + afp_seguro + afp_comision
		totals = epp + otr_desc + ret_judicial + sg_r + grat_ded + viat_ded + cat + otros_ingresos_new + adelantos + totals_afp + snp + canasta_de_navidad + bonificacion_personal
		totals = round(totals,2)

		row = [ss.name, ss.employee, ss.employee_name,ss.documento_identidad,ss.branch, id_sucursal,employees[0].zona_recursos,employees[0].fondo_de_pensiones,
			   ss.fecha_ingreso,jornal_diary,ss.total_working_days,ss.payment_days,
			   days_not_worked, feriados_trabajados,ss.dias_vaciones, ss.descanso_medico,ss.n_horas_extras_25,ss.n_horas_extras_35,ss.n_horas_extras_100,ss.pago_horas_extras_feriado,
			   ss.n_horas_nocturnas,subsidy, hours_working, amount_licencia, amount_licencia_paternidad,
			   amount_licencia_por_fallecimiento, amount_licencias_sin_goce, remuneracion_component,
			   vacaciones,descanso_medico,asigna_f,apoyos,hours,h_100,feriados,h_n, movilidad, movilidad_variable,gratificacion_earn, bonif, viat_earn,
			   viaticos_entrada, otrs_ing,employees[0].condiciones_de_trabajo if employees[0].condiciones_de_trabajo else "",
			   ss.gross_pay,snp,afp_fondo,afp_seguro,afp_comision,totals_afp, adelantos, cat, otros_ingresos_new, viat_ded,
			   grat_ded, sg_r, ret_judicial, epp, otr_desc, totals,ss.net_pay, essalud, vida_ley, employees[0].bank_name,
			   employees[0].bank_ac_no,employees[0].date_of_birth,employees[0].gender,"PERUANA" if employees[0].tipo_de_documento == "DNI" else "EXTRANJERA",
			   employees[0].status, canasta_de_navidad, bonificacion_personal,ss.licencia_paternidad, ss.licencia_por_fallecimiento,
			   ss.licencia,ss.es_una_licencia_sin_goce, ss.tipo_de_documento, ss.designation, ss.ausencias_reales,
			   monto_subisidio_accidente,monto_subisidio_enfermedad,monto_subisidio_maternidad,h_25,h_35, descuentos_dias_no_laborados]

		if ss.branch is not None: columns[4] = columns[4].replace('-1','120')
		data.append(row)

	return data, columns

def get_attendance(start_date, end_date, employee):
	values = {'start_date': start_date, 'end_date':end_date, 'employee':employee}
	attendance = frappe.db.sql("""select count(name) as contador from `tabAttendance` where attendance_date BETWEEN %(start_date)s AND %(end_date)s  AND status NOT IN ('Present','Work From Home') AND employee = %(employee)s  AND docstatus != 2 """ ,values=values, as_dict=True)
	return attendance

def get_employee(employee):
	values = {'name': employee}
	employees = frappe.db.sql("""
		select name,fondo_de_pensiones, 
		remuneracion_mensual, bank_name, 
		bank_ac_no, zona_recursos, employment_type, 
		id_sucursal, date_of_birth, gender, 
		status, tipo_de_documento, modalidad_de_trabajo,
		condiciones_de_trabajo
		from `tabEmployee` 
		where name=%(name)s  """ ,values=values, as_dict=True)
	return employees

def get_viaticos(start_date, employee):
	meses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Setiembre', 'Octubre', 'Noviembre', 'Diciembre']
	start_date = str(start_date).split(sep='-')
	mes = meses[int(start_date[1]) - 1]
	anio = int(start_date[0])
	values = {'mes': mes, 'employee':employee,'anio': anio}
	viaticos = frappe.db.sql("""select name,monto_total, solo_entrada from `tabViaticos Nomina` where empleado=%(employee)s AND docstatus IN (0,1) AND mes = %(mes)s AND ano = %(anio)s""" ,values=values, as_dict=True)
	return viaticos

def get_salary_slips(filters, company_currency):
	filters.update({"from_date": filters.get("from_date"), "to_date":filters.get("to_date")})
	conditions, filters = get_conditions(filters, company_currency)
	salary_slips = frappe.db.sql("""select * from `tabSalary Slip` where %s
		order by employee""" % conditions, filters, as_dict=1)

	return salary_slips or []

def get_conditions(filters, company_currency):
	conditions = ""
	doc_status = {"Draft": 0, "Submitted": 1, "Cancelled": 2}

	if filters.get("docstatus"):
		conditions += "docstatus = {0}".format(doc_status[filters.get("docstatus")])

	if filters.get("from_date"): conditions += " and start_date >= %(from_date)s"
	if filters.get("to_date"): conditions += " and end_date <= %(to_date)s"
	if filters.get("company"): conditions += " and company = %(company)s"
	if filters.get("employee"): conditions += " and employee = %(employee)s"
	if filters.get("branch"): conditions += " and branch = %(branch)s"
	# if filters.get("currency") and filters.get("currency") != company_currency:
	# 	conditions += " and currency = %(currency)s"

	return conditions, filters

def get_ss_earning_map(salary_slips, currency, company_currency):
	ss_earnings = frappe.db.sql("""select sd.parent, sd.salary_component, sd.amount, ss.exchange_rate, ss.name
		from `tabSalary Detail` sd, `tabSalary Slip` ss where sd.parent=ss.name and sd.parent in (%s)""" %
								(', '.join(['%s']*len(salary_slips))), tuple([d.name for d in salary_slips]), as_dict=1)

	ss_earning_map = {}
	for d in ss_earnings:
		ss_earning_map.setdefault(d.parent, frappe._dict()).setdefault(d.salary_component, [])
		if currency == company_currency:
			ss_earning_map[d.parent][d.salary_component] = flt(d.amount) * flt(d.exchange_rate if d.exchange_rate else 1)
		else:
			ss_earning_map[d.parent][d.salary_component] = flt(d.amount)

	return ss_earning_map

def get_ss_ded_map(salary_slips, currency, company_currency):
	ss_deductions = frappe.db.sql("""select sd.parent, sd.salary_component, sd.amount, ss.exchange_rate, ss.name
		from `tabSalary Detail` sd, `tabSalary Slip` ss where sd.parent=ss.name and sd.parent in (%s)""" %
								  (', '.join(['%s']*len(salary_slips))), tuple([d.name for d in salary_slips]), as_dict=1)

	ss_ded_map = {}
	for d in ss_deductions:
		ss_ded_map.setdefault(d.parent, frappe._dict()).setdefault(d.salary_component, [])
		if currency == company_currency:
			ss_ded_map[d.parent][d.salary_component] = flt(d.amount) * flt(d.exchange_rate if d.exchange_rate else 1)
		else:
			ss_ded_map[d.parent][d.salary_component] = flt(d.amount)

	return ss_ded_map

