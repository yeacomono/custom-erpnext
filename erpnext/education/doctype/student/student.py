# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals

import frappe

import datetime

from frappe.model.document import Document
from frappe.utils import getdate,today
from frappe import _
from frappe.desk.form.linked_with import get_linked_doctypes
from erpnext.education.utils import check_content_completion, check_quiz_completion
class Student(Document):
	def validate(self):
		self.title = " ".join(filter(None, [self.apellido_paterno_es, self.apellido_materno_es, self.primer_nombre_es, self.segundo_nombre_es]))
		self.validate_dates()

		if self.student_applicant:
			self.check_unique()
			self.update_applicant_status()

		if frappe.get_value("Student", self.name, "title") != self.title:
			self.update_student_name_in_linked_doctype()

	def validate_dates(self):
		for sibling in self.siblings:
			if sibling.date_of_birth and getdate(sibling.date_of_birth) > getdate():
				frappe.throw(_("Row {0}:Sibling Date of Birth cannot be greater than today.").format(sibling.idx))

		if self.date_of_birth and getdate(self.date_of_birth) >= getdate(today()):
			frappe.throw(_("Date of Birth cannot be greater than today."))

		if self.date_of_birth and getdate(self.date_of_birth) >= getdate(self.joining_date):
			frappe.throw(_("Date of Birth cannot be greater than Joining Date."))

		if self.joining_date and self.date_of_leaving and getdate(self.joining_date) > getdate(self.date_of_leaving):
			frappe.throw(_("Joining Date can not be greater than Leaving Date"))

	def update_student_name_in_linked_doctype(self):
		linked_doctypes = get_linked_doctypes("Student")
		for d in linked_doctypes:
			meta = frappe.get_meta(d)
			if not meta.issingle:
				if "student_name" in [f.fieldname for f in meta.fields]:
					frappe.db.sql("""UPDATE `tab{0}` set student_name = %s where {1} = %s"""
						.format(d, linked_doctypes[d]["fieldname"][0]),(self.title, self.name))

				if "child_doctype" in linked_doctypes[d].keys() and "student_name" in \
					[f.fieldname for f in frappe.get_meta(linked_doctypes[d]["child_doctype"]).fields]:
					frappe.db.sql("""UPDATE `tab{0}` set student_name = %s where {1} = %s"""
						.format(linked_doctypes[d]["child_doctype"], linked_doctypes[d]["fieldname"][0]),(self.title, self.name))

	def check_unique(self):
		"""Validates if the Student Applicant is Unique"""
		student = frappe.db.sql("select name from `tabStudent` where student_applicant=%s and name!=%s", (self.student_applicant, self.name))
		if student:
			frappe.throw(_("Student {0} exist against student applicant {1}").format(student[0][0], self.student_applicant))

	def after_insert(self):
		if not frappe.get_single('Education Settings').get('user_creation_skip'):
			self.create_student_user()

	def create_student_user(self):
		"""Create a website user for student creation if not already exists"""
		if not frappe.db.exists("User", self.student_email_id):
			student_user = frappe.get_doc({
				'doctype':'User',
				'first_name': self.first_name,
				'last_name': self.last_name,
				'email': self.student_email_id,
				'gender': self.gender,
				'send_welcome_email': 0,
				'user_type': 'Website User'
				})
			""" antiguo valor cambiado """
			# 'send_welcome_email': 1,
			student_user.flags.ignore_permissions = True
			student_user.add_roles("Student")
			student_user.save()

	def update_applicant_status(self):
		"""Updates Student Applicant status to Admitted"""
		if self.student_applicant:
			frappe.db.set_value("Student Applicant", self.student_applicant, "application_status", "Admitted")

	def get_all_course_enrollments(self):
		"""Returns a list of course enrollments linked with the current student"""
		course_enrollments = frappe.get_all("Course Enrollment", filters={"student": self.name}, fields=['course', 'name'])
		if not course_enrollments:
			return None
		else:
			enrollments = {item['course']:item['name'] for item in course_enrollments}
			return enrollments

	def get_program_enrollments(self):
		"""Returns a list of course enrollments linked with the current student"""
		program_enrollments = frappe.get_all("Program Enrollment", filters={"student": self.name}, fields=['program'])
		if not program_enrollments:
			return None
		else:
			enrollments = [item['program'] for item in program_enrollments]
			return enrollments

	def get_topic_progress(self, course_enrollment_name, topic):
		"""
		Get Progress Dictionary of a student for a particular topic
			:param self: Student Object
			:param course_enrollment_name: Name of the Course Enrollment
			:param topic: Topic DocType Object
		"""
		contents = topic.get_contents()
		progress = []
		if contents:
			for content in contents:
				if content.doctype in ('Article', 'Video'):
					status = check_content_completion(content.name, content.doctype, course_enrollment_name)
					progress.append({'content': content.name, 'content_type': content.doctype, 'is_complete': status})
				elif content.doctype == 'Quiz':
					status, score, result, time_taken = check_quiz_completion(content, course_enrollment_name)
					progress.append({'content': content.name, 'content_type': content.doctype, 'is_complete': status, 'score': score, 'result': result})
		return progress

	def enroll_in_program(self, program_name):
		try:
			enrollment = frappe.get_doc({
					"doctype": "Program Enrollment",
					"student": self.name,
					"academic_year": frappe.get_last_doc("Academic Year").name,
					"program": program_name,
					"enrollment_date": frappe.utils.datetime.datetime.now()
				})
			enrollment.save(ignore_permissions=True)
		except frappe.exceptions.ValidationError:
			enrollment_name = frappe.get_list("Program Enrollment", filters={"student": self.name, "Program": program_name})[0].name
			return frappe.get_doc("Program Enrollment", enrollment_name)
		else:
			enrollment.submit()
			return enrollment

	def enroll_in_course(self, course_name, program_enrollment, enrollment_date=frappe.utils.datetime.datetime.now()):
		try:
			enrollment = frappe.get_doc({
					"doctype": "Course Enrollment",
					"student": self.name,
					"course": course_name,
					"program_enrollment": program_enrollment,
					"enrollment_date": enrollment_date
				})
			enrollment.save(ignore_permissions=True)
		except frappe.exceptions.ValidationError:
			enrollment_name = frappe.get_list("Course Enrollment", filters={"student": self.name, "course": course_name, "program_enrollment": program_enrollment})[0].name
			return frappe.get_doc("Course Enrollment", enrollment_name)
		else:
			return enrollment

def get_timeline_data(doctype, name):
	'''Return timeline for attendance'''
	return dict(frappe.db.sql('''select unix_timestamp(`date`), count(*)
		from `tabStudent Attendance` where
			student=%s
			and `date` > date_sub(curdate(), interval 1 year)
			and docstatus = 1 and status = 'Present'
			group by date''', name))


@frappe.whitelist(allow_guest=True)
def create_student(dni_student):

	values_student = {
		'numero_de_documento': dni_student
	}
	list_student = frappe.db.sql("""
		SELECT
			st.name,
			st.puesto,
			st.sucursal,
			br.division_nacional
		FROM
			`tabStudent` as st
		LEFT JOIN
			`tabBranch` as br ON br.name = st.sucursal
		WHERE
			st.numero_de_documento = %(numero_de_documento)s
	""", values=values_student, as_dict=True)

	if len(list_student) == 0:
		return {
			'status': False,
			'message': 'No se encontro al estudiante'
		}

	if list_student[0]['division_nacional'] is None:
		return {
			'status': False,
			'message': 'No se encontro la division nacional'
		}

	division_nacional = None

	if list_student[0]['division_nacional'] == 'Provincias':
		division_nacional = 'Provincias'

	if list_student[0]['division_nacional'] == 'Lima':
		division_nacional = 'Lima'

	if division_nacional is None:
		return {
			'status': False,
			'message': 'No se encontro la division nacional'
		}

	employee = None

	values_employee = {
		'passport_number': dni_student
	}
	list_employee = frappe.db.sql("""
		SELECT
			st.name,
			st.status,
			st.fecha_de_ingreso_real,
			st.user_id,
			st.department,
			st.fecha_de_relevo
		FROM
			`tabEmployee` as st
		WHERE
			st.passport_number = %(passport_number)s
	""", values=values_employee, as_dict=True)

	if len(list_employee) == 0:
		employee = {
			'student': list_student[0]['name'],
			'employee': False,
			'dni': dni_student,
			'status': None,
			'name_employee': None,
			'position': list_student[0]['puesto'],
			'branch': list_student[0]['sucursal'],
			'date_joining': None,
			'user': None,
			'department': None,
			'fecha_de_relevo': None
		}
	else:
		if list_employee[0]['status'] == 'PreActivo' or list_employee[0]['status'] == 'Active' or list_employee[0]['status'] == 'No Reportado':
			return {
				'status': False,
				'message': 'El empleado ya esta creado y se encuentra en estado ' + list_employee[0]['status']
			}

		if list_employee[0]['status'] == 'Inactive':
			employee = {
				'student': list_student[0]['name'],
				'employee': True,
				'dni': dni_student,
				'status': list_employee[0]['status'],
				'name_employee': list_employee[0]['name'],
				'position': list_student[0]['puesto'],
				'branch': list_student[0]['sucursal'],
				'date_joining': list_employee[0]['fecha_de_ingreso_real'],
				'user': list_employee[0]['user_id'],
				'department': list_employee[0]['department'],
				'fecha_de_relevo': list_employee[0]['fecha_de_relevo']
			}

	if employee is None:
		return {
			'status': False,
			'message': 'Error al buscar informacion, contacte con soporte'
		}

	values_salary_table_designation = {}
	list_salary_table_designation = frappe.db.sql("""
		SELECT
			st.sueldo,
			st.bono_nocturno,
			st.movilidad,
			st.parent,
			st.sucursal
		FROM
			`tabSueldos por Agencia` as st
	""", values=values_salary_table_designation, as_dict=True)

	array_salary_table_designation = {}

	if len(list_salary_table_designation) > 0:
		for salary_table in list_salary_table_designation:
			branch = salary_table['sucursal']
			designation = salary_table['parent']
			if branch not in array_salary_table_designation:
				array_salary_table_designation[branch] = {}
			if designation not in array_salary_table_designation[branch]:
				array_salary_table_designation[branch][designation] = salary_table

	department = 'Operaciones - SE'

	if employee['branch'] == 'MEXICO':
		values_department_employee = {
			'designation': employee['position'],
			'status': 'Active',
			'branch': 'MEXICO'
		}
		list_department_employee = frappe.db.sql("""
			SELECT
				st.department
			FROM
				`tabEmployee` as st
			WHERE
				st.designation = %(designation)s and st.status = %(status)s and st.branch = %(branch)s LIMIT 1
		""", values=values_department_employee, as_dict=True)

		if len(list_department_employee) == 0:
			department = 'Operaciones - SE'
		else:
			department = list_department_employee[0]['department']

	values_branch = {
		'name': employee['branch']
	}
	list_branch = frappe.db.sql("""
		SELECT
			st.zona_nacional,
			st.ideentificador,
			st.categoria,
			st.zona_recursos_humanos
		FROM
			`tabBranch` as st
		WHERE
			st.name = %(name)s
	""", values=values_branch, as_dict=True)

	data_branch = list_branch[0]

	fecha_actual = datetime.date.today()
	months = ["ENERO", "FEBRERO", "MARZO", "ABRIL", "MAYO", "JUNIO", "JULIO", "AGOSTO", "SETIEMBRE", "OCTUBRE", "NOVIEMBRE", "DICIEMBRE"];
	branchs = ['CHICLAYO PRINCIPAL','CUSCO PRINCIPAL','HUANCAYO PRINCIPAL','AREQUIPA PRINCIPAL','PIURA PRINCIPAL']
	numero_dia = fecha_actual.day
	numero_mes = fecha_actual.month
	numero_year = fecha_actual.year
	date_text = str(numero_dia) + " DE " + months[numero_mes-1] + " " + str(numero_year)

	if division_nacional == 'Provincias':
		create_employee = create_employee_province(employee, array_salary_table_designation, department, data_branch, date_text, fecha_actual, branchs)
		return create_employee
	else:
		create_employee = create_employee_lima(employee, array_salary_table_designation, department, data_branch, date_text, fecha_actual, branchs)
		return create_employee

def get_salary_from_db(posicion):
	values_salary = {"name": posicion}
	list_salary = frappe.db.sql("""
        SELECT
            st.sueldo,
            st.bono_nocturno,
            st.movilidad
        FROM
            `tabDesignation` as st
        WHERE
            st.name = %(name)s
    """, values=values_salary, as_dict=True)
	return list_salary

def create_employee_province(employee, salary_table, department, data_branch, date_text, fecha_actual, branchs):

	values_job_applicant = {
		'numero_de_documento': employee['dni'],
		'status': 'Accepted'
	}
	list_job_applicant = frappe.db.sql("""
		SELECT
			st.edad,
			st.estado_civil,
			st.primer_nombre,
			st.genero,
			st.segundo_nombre,
			st.apellidos,
			st.fecha_de_nacimiento,
			st.apellido_materno,
			st.nombre_completo,
			st.compania_de_trabajo,
			st.puesto_de_oportunidad,
			st.sucursal,
			st.job_title,
			st.email_id,
			st.direccion,
			st.phone_number,
			st.adjuntar_copia_de_documento,
			st.antecedentes_o_certijove,
			st.resume_attachment,
			st.carnet_3_dosis,
			st.numero_de_documento,
			st.documento,
			st.licencia_de_conducir_erp,
			st.creation
		FROM
			`tabJob Applicant` as st
		WHERE
			st.numero_de_documento = %(numero_de_documento)s and st.status = %(status)s order by creation desc
	""", values=values_job_applicant, as_dict=True)

	if len(list_job_applicant) == 0:
		return {
			'status': False,
			'message': 'No se encontro el documento del postulante registrado'
		}

	oportunidad_empleado = list_job_applicant[0]['job_title']

	values_requerimiento_personal = {
		'documento_convocatoria': oportunidad_empleado
	}

	list_requerimiento_personal = frappe.db.sql("""
		SELECT
			st.posicion_solicitada,
			st.data_16,
			st.categoria_del_puesto,
			st.tipo_de_jornada,
			st.turno,
			st.categoria,
			st.modalidad_de_trabajo,
			st.name,
			st.documento_convocatoria
		FROM
			`tabRequerimiento de Personal` as st
		WHERE
			st.documento_convocatoria = %(documento_convocatoria)s
	""", values=values_requerimiento_personal, as_dict=True)

	if len(list_requerimiento_personal) == 0:
		return {
			'status': False,
			'message': 'No se encontro el requerimiento de personal de provincia'
		}

	jornada = list_requerimiento_personal[0]['tipo_de_jornada']
	modalidad = list_requerimiento_personal[0]['data_16']
	modalidad_trabajo = list_requerimiento_personal[0]['modalidad_de_trabajo']
	categoria = list_requerimiento_personal[0]['categoria']
	categoria_puesto = list_requerimiento_personal[0]['categoria_del_puesto']
	posicion = list_requerimiento_personal[0]['posicion_solicitada']
	turno = list_requerimiento_personal[0]['turno']

	salary = 0
	mobility = 0
	night_bonus = 0
	driver_bonus = 0

	if employee['branch'] in salary_table and employee['position'] in salary_table[employee['branch']]:
		data = salary_table[employee['branch']][employee['position']]

		if jornada == 'Nocturno' and modalidad == 'JORNADA COMPLETA':
			salary = data['sueldo']
			mobility = data['movilidad']
			night_bonus = 358.75
		elif jornada == 'Nocturno' and modalidad == 'TIEMPO PARCIAL':
			salary = data['sueldo']
			mobility = data['movilidad']
			night_bonus = 179.375
		else:
			salary = data['sueldo']
			mobility = data['movilidad']
			night_bonus = data['bono_nocturno']
	else:
		array_salary_position = {
			"TIEMPO PARCIAL": {
				"ESTIBADOR XL": {
					"Diurno": {"salary": 512.50, "mov": 150, "nightBonus": 0},
					"Nocturno": {"salary": 512.50, "mov": 0, "nightBonus": 358.75}
				},
				"ESTIBADOR": {
					"Diurno": {"salary": 512.50, "mov": 150, "nightBonus": 0},
					"Nocturno": {"salary": 512.50, "mov": 0, "nightBonus": 358.75}
				},
				"ATENCION AL CLIENTE": {
					"Diurno": {"salary": 512.50, "mov": 87.50, "nightBonus": 0},
					"Nocturno": {"salary": 512.50, "mov": 87.50, "nightBonus": 0}
				},
				"ATENCION AL CLIENTE, RECLAMOS Y COT.": {
					"Diurno": {"salary": 512.50, "mov": 87.50, "nightBonus": 0},
					"Nocturno": {"salary": 512.50, "mov": 87.50, "nightBonus": 0}
				},
				"ASISTENTE ADMINISTRATIVO": {
					"Diurno": {"salary": 512.50, "mov": 150, "nightBonus": 0},
					"Nocturno": {"salary": 512.50, "mov": 150, "nightBonus": 0}
				}
			},
			"JORNADA COMPLETA": {
				"Categoría 1": {
					"CONDUCTOR DE REPARTO": {"salary": 1200, "mov": 200}
				},
				"Categoría 2": {
					"CONDUCTOR DE REPARTO": {"salary": 1100, "mov": 100}
				},
				"Categoría 3": {
					"CONDUCTOR DE REPARTO": {"salary": 1100, "mov": 100}
				},
				"Categoría 4": {
					"CONDUCTOR DE REPARTO": {"salary": 1100, "mov": 100}
				}
			}
		}
		if modalidad in array_salary_position:
			modalidad_data = array_salary_position[modalidad]
			if categoria in modalidad_data and posicion in modalidad_data[categoria]:
				data = modalidad_data[categoria][posicion]
				salary = data.get('salary', 0)
				mobility = data.get('mov', 0)
				night_bonus = data.get('nightBonus', 0)
			else:
				list_salary = get_salary_from_db(posicion)
				if list_salary:
					salary = list_salary[0]['sueldo']
					mobility = list_salary[0]['movilidad']
					night_bonus = list_salary[0]['bono_nocturno']
				else:
					return {
						'status': False,
						'message': 'No se encontró sueldo para el puesto del estudiante'
					}
		else:
			list_salary = get_salary_from_db(posicion)
			if list_salary:
				salary = list_salary[0]['sueldo']
				mobility = list_salary[0]['movilidad']
				night_bonus = list_salary[0]['bono_nocturno']
			else:
				return {
					'status': False,
					'message': 'No se encontró sueldo para el puesto del estudiante'
				}

	turn_employee = turno if turno and turno != 'SELECCIONAR' else 'TURNO 8:00AM'

	values_turn = {
		'name': turn_employee
	}
	list_turn = frappe.db.sql("""
		SELECT
			st.start_time,
			st.end_time
		FROM
			`tabShift Type` as st
		WHERE
			st.name = %(name)s
	""", values=values_turn, as_dict=True)

	data_turn = list_turn[0]

	if employee['employee']:

		update_user = frappe.db.set_value('User',  employee['user'], 'enabled', 1)
		list_user = frappe.db.get_value('User', employee['user'], 'enabled')
		list_branch = frappe.db.get_value('Employee', employee['name_employee'], 'branch')

		if list_user == 0:
			return {
				'status': False,
				'message': 'Error al actualizar el usuario'
			}

		fecha_relevo = employee['fecha_de_relevo'] if employee['fecha_de_relevo'] is not None else fecha_actual

		list_work_history = frappe.db.get_list('Employee Internal Work History',
											   filters={
												   'parent': employee['name_employee']
											   },
											   fields=['to_date']
											   )

		idx_history = len(list_work_history) + 1

		doc = frappe.get_doc({
			'doctype': 'Employee Internal Work History',
			'branch': list_branch if list_branch is not None else '',
			'designation': employee['position'],
			'parent': employee['name_employee'],
			'parentfield': 'internal_work_history',
			'parenttype': 'Employee',
			'department': employee['department'],
			'from_date': employee['date_joining'],
			'to_date': fecha_relevo,
			'idx': idx_history
		})
		doc.db_insert()

		update_employee = frappe.db.set_value('Employee', employee['name_employee'], {
			'dia_de_descanso': 'Domingo',
			'contract_end_date': '3100-12-12',
			'retencion_judicial': '--Seleccione--',
			'fecha_de_ingreso_real': fecha_actual,
			'leave_approver': 'anggisoto@shalom.com.pe',
			'holiday_list': 'FERIADOS 2022',
			'bank_name': 'Banco de Crédito del Perú',
			'salary_mode': 'Bank',
			'fondo_de_pensiones': 'INTEGRA',
			'fecha_de_afiliacion': fecha_actual,
			'cussp': 'VACIO',
			'asignacion_familiar_2': '0',
			'health_insurance_provider': 'EsSalud',
			'prefered_contact_email': 'Company Email',
			'date_of_joining': '2023-03-01',
			'documento': '',
			'estado': '',
			'empleado_desconectado': 0,
			'terminos_y_condiciones_app': 0,
			'fecha_de_relevo': None,
			'fecha_terminos_y_condiciones': None,
			'tipo_de_reelevo': '',
			'reason_for_leaving': '',
			'image': '/files/SHALOM FAMILIA_Portada2.jpg',
			'zona_nacional': data_branch['zona_nacional'] if data_branch['zona_nacional'] is not None else '',
			'zona_recursos': data_branch['zona_recursos_humanos'] if data_branch['zona_recursos_humanos'] is not None else '',
			'id_sucursal': data_branch['ideentificador'] if data_branch['ideentificador'] is not None else '',
			'categoria_sucursal': data_branch['categoria'] if data_branch['categoria'] is not None else '',
			'hora_de_inicio': data_turn['start_time'] if data_turn['start_time'] is not None else None,
			'hora_de_finalizacion': data_turn['end_time'] if data_turn['end_time'] is not None else None,
			'remuneracion_mensual': salary,
			'bono_conductor': night_bonus,
			'movilidad': mobility,
			'default_shift': turno if turno is not None and turno != 'SELECCIONAR' else 'TURNO 8:00AM',
			'employment_type': modalidad,
			'modalidad_de_trabajo': 'Teletrabajo' if modalidad_trabajo is None or modalidad_trabajo == 'Teletrabajo' else 'Presencial',
			'tipo_de_empleado': 'OPERATIVO' if categoria_puesto is None or categoria_puesto == 'SELECCIONAR' else categoria_puesto,
			'tipo_de_jornada': 'Diurno' if jornada is None or jornada == 'SELECCIONAR' else jornada,
			'estado_civil_personal': list_job_applicant[0]['estado_civil'] if list_job_applicant[0]['estado_civil'] is not None else 'Soltero/a',
			'first_name': list_job_applicant[0]['primer_nombre'].upper() if list_job_applicant[0]['primer_nombre'] is not None else '',
			'middle_name': list_job_applicant[0]['segundo_nombre'].upper() if list_job_applicant[0]['segundo_nombre'] is not None else '',
			'first_last_name': list_job_applicant[0]['apellidos'].upper() if list_job_applicant[0]['apellidos'] is not None else '',
			'second_last_name': list_job_applicant[0]['apellido_materno'].upper() if list_job_applicant[0]['apellido_materno'] is not None else '',
			'gender': list_job_applicant[0]['genero'] if list_job_applicant[0]['genero'] is not None else '',
			'nombre_completo': list_job_applicant[0]['nombre_completo'].upper() if list_job_applicant[0]['nombre_completo'] is not None else '',
			'company': list_job_applicant[0]['compania_de_trabajo'] if list_job_applicant[0]['compania_de_trabajo'] is not None else 'Shalom Empresarial',
			'date_of_birth': list_job_applicant[0]['fecha_de_nacimiento'] if list_job_applicant[0]['fecha_de_nacimiento'] is not None else '',
			'designation': list_job_applicant[0]['puesto_de_oportunidad'] if list_job_applicant[0]['puesto_de_oportunidad'] is not None else '',
			'branch': list_job_applicant[0]['sucursal'] if list_job_applicant[0]['sucursal'] is not None else '',
			'personal_email': list_job_applicant[0]['email_id'] if list_job_applicant[0]['email_id'] is not None else '',
			'passport_number': list_job_applicant[0]['numero_de_documento'] if list_job_applicant[0]['numero_de_documento'] is not None else '',
			'current_address': list_job_applicant[0]['direccion'] if list_job_applicant[0]['direccion'] is not None else '',
			'permanent_address': list_job_applicant[0]['direccion'] if list_job_applicant[0]['direccion'] is not None else '',
			'dni': list_job_applicant[0]['adjuntar_copia_de_documento'] if list_job_applicant[0]['adjuntar_copia_de_documento'] is not None else '',
			'cv': list_job_applicant[0]['resume_attachment'] if list_job_applicant[0]['resume_attachment'] is not None else '',
			'edad_del_trabajador': list_job_applicant[0]['edad'] if list_job_applicant[0]['edad'] is not None else '',
			'user_id': str(list_job_applicant[0]['numero_de_documento']) + '@shalomcontrol.com' if list_job_applicant[0]['numero_de_documento'] is not None else '',
			'company_email': str(list_job_applicant[0]['numero_de_documento']) + '@shalomcontrol.com' if list_job_applicant[0]['numero_de_documento'] is not None else '',
			'cell_number': list_job_applicant[0]['phone_number'] if list_job_applicant[0]['phone_number'] is not None else '',
			'grade': 'CONDUCTOR' if list_job_applicant[0]['puesto_de_oportunidad'] is 'CONDUCTOR INTERPROVINCIAL' or list_job_applicant[0]['puesto_de_oportunidad'] is 'CONDUCTOR REGIONAL' else 'OPERARIO',
			'status': 'Active' if list_job_applicant[0]['puesto_de_oportunidad'] is 'CONDUCTOR INTERPROVINCIAL' or list_job_applicant[0]['puesto_de_oportunidad'] is 'CONDUCTOR REGIONAL' else 'PreActivo',
			'calificacion_trabajador': 'No Sujeto a Fiscalización' if list_job_applicant[0]['puesto_de_oportunidad'] is 'CONDUCTOR INTERPROVINCIAL' or list_job_applicant[0]['puesto_de_oportunidad'] is 'CONDUCTOR REGIONAL' else 'Personal Sujeto a Fiscalización',
			'department': 'DISTRIBUCION - SE' if list_job_applicant[0]['puesto_de_oportunidad'] is 'CONDUCTOR INTERPROVINCIAL' or list_job_applicant[0]['puesto_de_oportunidad'] is 'CONDUCTOR REGIONAL' else department
		})

		update_student = frappe.db.set_value('Student',  employee['student'], {
			'empleado_creado': 1,
			'empleado': employee['name_employee']
		})

		if list_cv_filtrado[0]['sucursal'] in branchs:
			branch_employee = list_cv_filtrado[0]['sucursal'].split(" ")[0]
		else:
			branch_employee = list_cv_filtrado[0]['sucursal']

		doc = frappe.get_doc({
			'doctype': 'Convenio de Descuento',
			'empleado': employee['name_employee'],
			'fecha_inicio': fecha_actual,
			'fecha_inicio_texto': date_text,
			'sucursal_obs': branch_employee,
			'docstatus': 1,
			'empresa': list_cv_filtrado[0]['compania_trabajo'] if list_cv_filtrado[0]['compania_trabajo'] is not None else 'Shalom Empresarial'
		})
		doc.insert()

		license_categories = {
			"CONDUCTOR DE REPARTO": "A2B",
			"CONDUCTOR INTERPROVINCIAL": "A3C"
		}

		first_entry = list_job_applicant[0]

		if first_entry['licencia_de_conducir_erp'] is not None:
			license_class = license_categories.get(first_entry['puesto_de_oportunidad'])
			if license_class:
				doc_license = frappe.get_doc({
					'doctype': 'Driver',
					'employee': employee['name_employee'],
					'license_number': first_entry['licencia_de_conducir_erp'],
					'driving_license_category': {
						'parentfield': 'driving_license_category',
						'parenttype': 'Driver',
						'class': license_class
					}
				})
				doc_license.insert()

		return {
			'status': True,
			'message': 'Empleado Actualizado'
		}

	else:

		data = list_job_applicant[0]
		doc = frappe.new_doc("Employee")
		doc.dia_de_descanso = 'Domingo'
		doc.unidad_de_negocio = 'ADMINISTRATIVO'
		doc.contract_end_date = '3100-12-12'
		doc.leave_approver = 'anggisoto@shalom.com.pe'
		doc.holiday_list = 'FERIADOS 2022'
		doc.bank_name = 'Banco de Crédito del Perú'
		doc.salary_mode = 'Bank'
		doc.fondo_de_pensiones = 'INTEGRA'
		doc.cussp = 'VACIO'
		doc.asignacion_familiar_2 = '0'
		doc.health_insurance_provider = 'EsSalud'
		doc.prefered_contact_email = 'Company Email'
		doc.date_of_joining = '2023-03-01'
		doc.image = '/files/SHALOM FAMILIA_Portada2.jpg'
		doc.zona_nacional = data_branch['zona_nacional'] if data_branch['zona_nacional'] is not None else '',
		doc.zona_recursos = data_branch['zona_recursos_humanos'] if data_branch['zona_recursos_humanos'] is not None else '',
		doc.id_sucursal = data_branch['ideentificador'] if data_branch['ideentificador'] is not None else '',
		doc.categoria_sucursal = data_branch['categoria'] if data_branch['categoria'] is not None else '',
		doc.hora_de_inicio = data_turn['start_time'] if data_turn['start_time'] is not None else None,
		doc.hora_de_finalizacion = data_turn['end_time'] if data_turn['end_time'] is not None else None,
		doc.fecha_de_afiliacion = fecha_actual
		doc.fecha_de_ingreso_real = fecha_actual
		doc.remuneracion_mensual = salary
		doc.bono_conductor = night_bonus
		doc.movilidad = mobility
		doc.default_shift = turno if turno and turno != 'SELECCIONAR' else 'TURNO 8:00AM'
		doc.employment_type = modalidad
		doc.modalidad_de_trabajo = 'Teletrabajo' if modalidad_trabajo in [None, 'Teletrabajo'] else 'Presencial'
		doc.tipo_de_empleado = 'OPERATIVO' if categoria_puesto in [None, 'SELECCIONAR'] else categoria_puesto
		doc.tipo_de_jornada = 'Diurno' if jornada in [None, 'SELECCIONAR'] else jornada
		doc.estado_civil_personal = data['estado_civil'] if data.get('estado_civil') is not None else 'Soltero/a'
		doc.first_name = data['primer_nombre'].upper() if data.get('primer_nombre') is not None else ''
		doc.middle_name = data['segundo_nombre'].upper() if data.get('segundo_nombre') is not None else ''
		doc.first_last_name = data['apellidos'].upper() if data.get('apellidos') is not None else ''
		doc.second_last_name = data['apellido_materno'].upper() if data.get('apellido_materno') is not None else ''
		doc.gender = data['genero'] if data.get('genero') is not None else ''
		doc.nombre_completo = data['nombre_completo'].upper() if data.get('nombre_completo') is not None else ''
		doc.company = data['compania_de_trabajo'] if data.get('compania_de_trabajo') is not None else 'Shalom Empresarial'
		doc.date_of_birth = data['fecha_de_nacimiento'] if data.get('fecha_de_nacimiento') is not None else None
		doc.designation = data['puesto_de_oportunidad'] if data.get('puesto_de_oportunidad') is not None else ''
		doc.branch = data['sucursal'] if data.get('sucursal') is not None else ''
		doc.personal_email = data['email_id'] if data.get('email_id') is not None else ''
		doc.passport_number = data['numero_de_documento'] if data.get('numero_de_documento') is not None else ''
		doc.current_address = data['direccion'] if data.get('direccion') is not None else ''
		doc.permanent_address = data['direccion'] if data.get('direccion') is not None else ''
		doc.dni = data['adjuntar_copia_de_documento'] if data.get('adjuntar_copia_de_documento') is not None else ''
		doc.cv = data['resume_attachment'] if data.get('resume_attachment') is not None else ''
		doc.edad_del_trabajador = data['edad'] if data.get('edad') is not None else ''
		doc.user_id = f"{data['numero_de_documento']}@shalomcontrol.com" if data.get('numero_de_documento') is not None else ''
		doc.company_email = f"{data['numero_de_documento']}@shalomcontrol.com" if data.get('numero_de_documento') is not None else ''
		doc.cell_number = data['número_de_teléfono'] if data.get('número_de_teléfono') is not None else ''
		doc.grade = 'CONDUCTOR' if data.get('puesto_de_oportunidad') in ['CONDUCTOR INTERPROVINCIAL', 'CONDUCTOR REGIONAL'] else 'OPERARIO'
		doc.status = 'Active' if data.get('puesto_de_oportunidad') in ['CONDUCTOR INTERPROVINCIAL', 'CONDUCTOR REGIONAL'] else 'PreActivo'
		doc.calificacion_trabajador = 'No Sujeto a Fiscalización' if data.get('puesto_de_oportunidad') in ['CONDUCTOR INTERPROVINCIAL', 'CONDUCTOR REGIONAL'] else 'Personal Sujeto a Fiscalización'
		doc.department = 'DISTRIBUCION - SE' if data.get('puesto_de_oportunidad') in ['CONDUCTOR INTERPROVINCIAL', 'CONDUCTOR REGIONAL'] else department
		doc.db_insert()

		license_categories = {
			"CONDUCTOR DE REPARTO": "A2B",
			"CONDUCTOR INTERPROVINCIAL": "A3C"
		}

		first_entry = list_job_applicant[0]

		if first_entry['licencia_de_conducir_erp'] is not None:
			license_class = license_categories.get(first_entry['puesto_de_oportunidad'])
			if license_class:
				doc_license = frappe.get_doc({
					'doctype': 'Driver',
					'employee': doc.name,
					'license_number': first_entry['licencia_de_conducir_erp'],
					'driving_license_category': {
						'parentfield': 'driving_license_category',
						'parenttype': 'Driver',
						'class': license_class
					}
				})
				doc_license.insert()

		update_student = frappe.db.set_value('Student',  employee['student'], {
			'empleado_creado': 1,
			'empleado': doc.name
		})

		if list_job_applicant[0]['sucursal'] in branchs:
			branch_employee = list_job_applicant[0]['sucursal'].split(" ")[0]
		else:
			branch_employee = list_job_applicant[0]['sucursal']

		doc_convenio = frappe.get_doc({
			'doctype': 'Convenio de Descuento',
			'empleado': doc.name,
			'fecha_inicio': fecha_actual,
			'fecha_inicio_texto': date_text,
			'sucursal_obs': branch_employee,
			'docstatus': 1,
			'empresa': list_job_applicant[0]['compania_de_trabajo'] if list_job_applicant[0]['compania_de_trabajo'] is not None else 'Shalom Empresarial'
		})
		doc_convenio.insert()

		return {
			'status': True,
			'message': 'Empleado Creado'
		}

def create_employee_lima(employee, salary_table, department, data_branch, date_text, fecha_actual, branchs):
	values_cv_filtrado = {
		'numero_documento': employee['dni'],
		'estado': 'Contratado'
	}
	list_cv_filtrado = frappe.db.sql("""
		SELECT
			st.oportunidad_empleo,
			st.estado_civil,
			st.primer_nombre,
			st.segundo_nombre,
			st.apellido_paterno,
			st.apellido_materno,
			st.genero,
			st.nombre_solicitante,
			st.compania_trabajo,
			st.fecha_de_nacimiento,
			st.puesto_oportunidad,
			st.sucursal,
			st.correo_electronico,
			st.numero_documento,
			st.direccion_postulante,
			st.número_de_teléfono,
			st.adj_copia_documento,
			st.adj_cv,
			st.edad,
			st.licencia_de_conducir
		FROM
			`tabCV Filtrado` as st
		WHERE
			st.numero_documento = %(numero_documento)s and st.estado = %(estado)s
	""", values=values_cv_filtrado, as_dict=True)

	if len(list_cv_filtrado) == 0:
		return {
			'status': False,
			'message': 'No se encontro el documento de cv filtrado'
		}

	oportunidad_empleado = list_cv_filtrado[0]['oportunidad_empleo']

	values_requerimiento_personal = {
		'documento_convocatoria': oportunidad_empleado
	}
	list_requerimiento_personal = frappe.db.sql("""
		SELECT
			st.posicion_solicitada,
			st.data_16,
			st.categoria_del_puesto,
			st.tipo_de_jornada,
			st.turno,
			st.categoria,
			st.modalidad_de_trabajo,
			st.name
		FROM
			`tabRequerimiento de Personal Lima` as st
		WHERE
			st.documento_convocatoria = %(documento_convocatoria)s
	""", values=values_requerimiento_personal, as_dict=True)

	if len(list_requerimiento_personal) == 0:
		return {
			'status': False,
			'message': 'No se encontro el requerimiento de personal de lima'
		}

	jornada = list_requerimiento_personal[0]['tipo_de_jornada']
	modalidad = list_requerimiento_personal[0]['data_16']
	modalidad_trabajo = list_requerimiento_personal[0]['modalidad_de_trabajo']
	categoria = list_requerimiento_personal[0]['categoria']
	categoria_puesto = list_requerimiento_personal[0]['categoria_del_puesto']
	posicion = list_requerimiento_personal[0]['posicion_solicitada']
	turno = list_requerimiento_personal[0]['turno']

	salary = 0
	mobility = 0
	night_bonus = 0
	driver_bonus = 0

	if employee['branch'] in salary_table and employee['position'] in salary_table[employee['branch']]:
		data = salary_table[employee['branch']][employee['position']]

		if jornada == 'Nocturno' and modalidad == 'JORNADA COMPLETA':
			salary = data['sueldo']
			mobility = data['movilidad']
			night_bonus = 358.75
		elif jornada == 'Nocturno' and modalidad == 'TIEMPO PARCIAL':
			salary = data['sueldo']
			mobility = data['movilidad']
			night_bonus = 179.375
		else:
			salary = data['sueldo']
			mobility = data['movilidad']
			night_bonus = data['bono_nocturno']
	else:
		array_salary_position = {
			"TIEMPO PARCIAL": {
				"ESTIBADOR XL": {
					"Diurno": {"salary": 512.50, "mov": 150, "nightBonus": 0},
					"Nocturno": {"salary": 512.50, "mov": 0, "nightBonus": 358.75}
				},
				"ESTIBADOR": {
					"Diurno": {"salary": 512.50, "mov": 150, "nightBonus": 0},
					"Nocturno": {"salary": 512.50, "mov": 0, "nightBonus": 358.75}
				},
				"ATENCION AL CLIENTE": {
					"Diurno": {"salary": 512.50, "mov": 87.50, "nightBonus": 0},
					"Nocturno": {"salary": 512.50, "mov": 87.50, "nightBonus": 0}
				},
				"ATENCION AL CLIENTE, RECLAMOS Y COT.": {
					"Diurno": {"salary": 512.50, "mov": 87.50, "nightBonus": 0},
					"Nocturno": {"salary": 512.50, "mov": 87.50, "nightBonus": 0}
				},
				"ASISTENTE ADMINISTRATIVO": {
					"Diurno": {"salary": 512.50, "mov": 150, "nightBonus": 0},
					"Nocturno": {"salary": 512.50, "mov": 150, "nightBonus": 0}
				}
			},
			"JORNADA COMPLETA": {
				"Categoría 1": {
					"CONDUCTOR DE REPARTO": {"salary": 1200, "mov": 200}
				},
				"Categoría 2": {
					"CONDUCTOR DE REPARTO": {"salary": 1100, "mov": 100}
				},
				"Categoría 3": {
					"CONDUCTOR DE REPARTO": {"salary": 1100, "mov": 100}
				},
				"Categoría 4": {
					"CONDUCTOR DE REPARTO": {"salary": 1100, "mov": 100}
				}
			}
		}
		if modalidad in array_salary_position:
			modalidad_data = array_salary_position[modalidad]
			if categoria in modalidad_data and posicion in modalidad_data[categoria]:
				data = modalidad_data[categoria][posicion]
				salary = data.get('salary', 0)
				mobility = data.get('mov', 0)
				night_bonus = data.get('nightBonus', 0)
			else:
				list_salary = get_salary_from_db(posicion)
				if list_salary:
					salary = list_salary[0]['sueldo']
					mobility = list_salary[0]['movilidad']
					night_bonus = list_salary[0]['bono_nocturno']
				else:
					return {
						'status': False,
						'message': 'No se encontró sueldo para el puesto del estudiante'
					}
		else:
			list_salary = get_salary_from_db(posicion)
			if list_salary:
				salary = list_salary[0]['sueldo']
				mobility = list_salary[0]['movilidad']
				night_bonus = list_salary[0]['bono_nocturno']
			else:
				return {
					'status': False,
					'message': 'No se encontró sueldo para el puesto del estudiante'
				}


	turn_employee = turno if turno and turno != 'SELECCIONAR' else 'TURNO 8:00AM'

	values_turn = {
		'name': turn_employee
	}
	list_turn = frappe.db.sql("""
		SELECT
			st.start_time,
			st.end_time
		FROM
			`tabShift Type` as st
		WHERE
			st.name = %(name)s
	""", values=values_turn, as_dict=True)

	data_turn = list_turn[0]

	if employee['employee']:
		update_user = frappe.db.set_value('User',  employee['user'], 'enabled', 1)
		list_user = frappe.db.get_value('User', employee['user'], 'enabled')
		list_branch = frappe.db.get_value('Employee', employee['name_employee'], 'branch')

		if list_user == 0:
			return {
				'status': False,
				'message': 'Error al actualizar el usuario'
			}

		fecha_relevo = employee['fecha_de_relevo'] if employee['fecha_de_relevo'] is not None else fecha_actual

		list_work_history = frappe.db.get_list('Employee Internal Work History',
											   filters={
												   'parent': employee['name_employee']
											   },
											   fields=['to_date']
											   )

		idx_history = len(list_work_history) + 1

		doc = frappe.get_doc({
			'doctype': 'Employee Internal Work History',
			'branch': list_branch if list_branch is not None else '',
			'designation': employee['position'],
			'parent': employee['name_employee'],
			'parentfield': 'internal_work_history',
			'parenttype': 'Employee',
			'department': employee['department'],
			'from_date': employee['date_joining'],
			'to_date': fecha_relevo,
			'idx': idx_history
		})
		doc.db_insert()

		if list_cv_filtrado[0]['sucursal'] in branchs:
			branch_employee = list_cv_filtrado[0]['sucursal'].split(" ")[0]
		else:
			branch_employee = list_cv_filtrado[0]['sucursal']

		doc = frappe.get_doc({
			'doctype': 'Convenio de Descuento',
			'empleado': employee['name_employee'],
			'fecha_inicio': fecha_actual,
			'fecha_inicio_texto': date_text,
			'sucursal_obs': branch_employee,
			'docstatus': 1,
			'empresa': list_cv_filtrado[0]['compania_trabajo'] if list_cv_filtrado[0]['compania_trabajo'] is not None else 'Shalom Empresarial'
		})
		doc.insert()

		license_categories = {
			"CONDUCTOR DE REPARTO": "A2B",
			"CONDUCTOR INTERPROVINCIAL": "A3C"
		}

		first_entry = list_cv_filtrado[0]

		if first_entry['licencia_de_conducir'] is not None:
			license_class = license_categories.get(first_entry['puesto_oportunidad'])
			if license_class:
				doc_license = frappe.get_doc({
					'doctype': 'Driver',
					'employee': doc.name,
					'license_number': first_entry['licencia_de_conducir'],
					'driving_license_category': {
						'parentfield': 'driving_license_category',
						'parenttype': 'Driver',
						'class': license_class
					}
				})
				doc_license.insert()

		update_employee = frappe.db.set_value('Employee', employee['name_employee'], {
			'dia_de_descanso': 'Domingo',
			'contract_end_date': '3100-12-12',
			'retencion_judicial': '--Seleccione--',
			'fecha_de_ingreso_real': fecha_actual,
			'leave_approver': 'anggisoto@shalom.com.pe',
			'holiday_list': 'FERIADOS 2022',
			'bank_name': 'Banco de Crédito del Perú',
			'salary_mode': 'Bank',
			'fondo_de_pensiones': 'INTEGRA',
			'fecha_de_afiliacion': fecha_actual,
			'cussp': 'VACIO',
			'asignacion_familiar_2': '0',
			'health_insurance_provider': 'EsSalud',
			'prefered_contact_email': 'Company Email',
			'date_of_joining': '2023-03-01',
			'documento': '',
			'estado': '',
			'empleado_desconectado': 0,
			'terminos_y_condiciones_app': 0,
			'fecha_de_relevo': None,
			'fecha_terminos_y_condiciones': None,
			'tipo_de_reelevo': '',
			'reason_for_leaving': '',
			'image': '/files/SHALOM FAMILIA_Portada2.jpg',
			'zona_nacional': data_branch['zona_nacional'] if data_branch['zona_nacional'] is not None else '',
			'zona_recursos': data_branch['zona_recursos_humanos'] if data_branch['zona_recursos_humanos'] is not None else '',
			'id_sucursal': data_branch['ideentificador'] if data_branch['ideentificador'] is not None else '',
			'categoria_sucursal': data_branch['categoria'] if data_branch['categoria'] is not None else '',
			'hora_de_inicio': data_turn['start_time'] if data_turn['start_time'] is not None else None,
			'hora_de_finalizacion': data_turn['end_time'] if data_turn['end_time'] is not None else None,
			'remuneracion_mensual': salary,
			'bono_conductor': night_bonus,
			'movilidad': mobility,
			'default_shift': turno if turno is not None and turno != 'SELECCIONAR' else 'TURNO 8:00AM',
			'employment_type': modalidad,
			'modalidad_de_trabajo': 'Teletrabajo' if modalidad_trabajo is None or modalidad_trabajo == 'Teletrabajo' else 'Presencial',
			'tipo_de_empleado': 'OPERATIVO' if categoria_puesto is None or categoria_puesto == 'SELECCIONAR' else categoria_puesto,
			'tipo_de_jornada': 'Diurno' if jornada is None or jornada == 'SELECCIONAR' else jornada,
			'estado_civil_personal': list_cv_filtrado[0]['estado_civil'] if list_cv_filtrado[0]['estado_civil'] is not None else 'Soltero/a',
			'first_name': list_cv_filtrado[0]['primer_nombre'].upper() if list_cv_filtrado[0]['primer_nombre'] is not None else '',
			'middle_name': list_cv_filtrado[0]['segundo_nombre'].upper() if list_cv_filtrado[0]['segundo_nombre'] is not None else '',
			'first_last_name': list_cv_filtrado[0]['apellido_paterno'].upper() if list_cv_filtrado[0]['apellido_paterno'] is not None else '',
			'second_last_name': list_cv_filtrado[0]['apellido_materno'].upper() if list_cv_filtrado[0]['apellido_materno'] is not None else '',
			'gender': list_cv_filtrado[0]['genero'] if list_cv_filtrado[0]['genero'] is not None else '',
			'nombre_completo': list_cv_filtrado[0]['nombre_solicitante'].upper() if list_cv_filtrado[0]['nombre_solicitante'] is not None else '',
			'company': list_cv_filtrado[0]['compania_trabajo'] if list_cv_filtrado[0]['compania_trabajo'] is not None else 'Shalom Empresarial',
			'date_of_birth': list_cv_filtrado[0]['fecha_de_nacimiento'] if list_cv_filtrado[0]['fecha_de_nacimiento'] is not None else '',
			'designation': list_cv_filtrado[0]['puesto_oportunidad'] if list_cv_filtrado[0]['puesto_oportunidad'] is not None else '',
			'branch': list_cv_filtrado[0]['sucursal'] if list_cv_filtrado[0]['sucursal'] is not None else '',
			'personal_email': list_cv_filtrado[0]['correo_electronico'] if list_cv_filtrado[0]['correo_electronico'] is not None else '',
			'passport_number': list_cv_filtrado[0]['numero_documento'] if list_cv_filtrado[0]['numero_documento'] is not None else '',
			'current_address': list_cv_filtrado[0]['direccion_postulante'] if list_cv_filtrado[0]['direccion_postulante'] is not None else '',
			'permanent_address': list_cv_filtrado[0]['direccion_postulante'] if list_cv_filtrado[0]['direccion_postulante'] is not None else '',
			'dni': list_cv_filtrado[0]['adj_copia_documento'] if list_cv_filtrado[0]['adj_copia_documento'] is not None else '',
			'cv': list_cv_filtrado[0]['adj_cv'] if list_cv_filtrado[0]['adj_cv'] is not None else '',
			'edad_del_trabajador': list_cv_filtrado[0]['edad'] if list_cv_filtrado[0]['edad'] is not None else '',
			'user_id': str(list_cv_filtrado[0]['numero_documento']) + '@shalomcontrol.com' if list_cv_filtrado[0]['numero_documento'] is not None else '',
			'company_email': str(list_cv_filtrado[0]['numero_documento']) + '@shalomcontrol.com' if list_cv_filtrado[0]['numero_documento'] is not None else '',
			'cell_number': list_cv_filtrado[0]['número_de_teléfono'] if list_cv_filtrado[0]['número_de_teléfono'] is not None else '',
			'grade': 'CONDUCTOR' if list_cv_filtrado[0]['puesto_oportunidad'] is 'CONDUCTOR INTERPROVINCIAL' or list_cv_filtrado[0]['puesto_oportunidad'] is 'CONDUCTOR REGIONAL' else 'OPERARIO',
			'status': 'Active' if list_cv_filtrado[0]['puesto_oportunidad'] is 'CONDUCTOR INTERPROVINCIAL' or list_cv_filtrado[0]['puesto_oportunidad'] is 'CONDUCTOR REGIONAL' else 'PreActivo',
			'calificacion_trabajador': 'No Sujeto a Fiscalización' if list_cv_filtrado[0]['puesto_oportunidad'] is 'CONDUCTOR INTERPROVINCIAL' or list_cv_filtrado[0]['puesto_oportunidad'] is 'CONDUCTOR REGIONAL' else 'Personal Sujeto a Fiscalización',
			'department': 'DISTRIBUCION - SE' if list_cv_filtrado[0]['puesto_oportunidad'] is 'CONDUCTOR INTERPROVINCIAL' or list_cv_filtrado[0]['puesto_oportunidad'] is 'CONDUCTOR REGIONAL' else department
		})

		update_student = frappe.db.set_value('Student',  employee['student'], {
			'empleado_creado': 1,
			'empleado': employee['name_employee']
		})

		return {
			'status': True,
			'message': 'Empleado Actualizado'
		}

	else:

		data = list_cv_filtrado[0]
		doc = frappe.new_doc("Employee")
		doc.dia_de_descanso = 'Domingo'
		doc.unidad_de_negocio = 'ADMINISTRATIVO'
		doc.contract_end_date = '3100-12-12'
		doc.leave_approver = 'anggisoto@shalom.com.pe'
		doc.holiday_list = 'FERIADOS 2022'
		doc.bank_name = 'Banco de Crédito del Perú'
		doc.salary_mode = 'Bank'
		doc.fondo_de_pensiones = 'INTEGRA'
		doc.cussp = 'VACIO'
		doc.asignacion_familiar_2 = '0'
		doc.health_insurance_provider = 'EsSalud'
		doc.prefered_contact_email = 'Company Email'
		doc.date_of_joining = '2023-03-01'
		doc.image = '/files/SHALOM FAMILIA_Portada2.jpg'
		doc.zona_nacional = data_branch['zona_nacional'] if data_branch['zona_nacional'] is not None else '',
		doc.zona_recursos = data_branch['zona_recursos_humanos'] if data_branch['zona_recursos_humanos'] is not None else '',
		doc.id_sucursal = data_branch['ideentificador'] if data_branch['ideentificador'] is not None else '',
		doc.categoria_sucursal = data_branch['categoria'] if data_branch['categoria'] is not None else '',
		doc.hora_de_inicio = data_turn['start_time'] if data_turn['start_time'] is not None else None,
		doc.hora_de_finalizacion = data_turn['end_time'] if data_turn['end_time'] is not None else None,
		doc.fecha_de_afiliacion = fecha_actual
		doc.fecha_de_ingreso_real = fecha_actual
		doc.remuneracion_mensual = salary
		doc.bono_conductor = night_bonus
		doc.movilidad = mobility
		doc.default_shift = turno if turno and turno != 'SELECCIONAR' else 'TURNO 8:00AM'
		doc.employment_type = modalidad
		doc.modalidad_de_trabajo = 'Teletrabajo' if modalidad_trabajo in [None, 'Teletrabajo'] else 'Presencial'
		doc.tipo_de_empleado = 'OPERATIVO' if categoria_puesto in [None, 'SELECCIONAR'] else categoria_puesto
		doc.tipo_de_jornada = 'Diurno' if jornada in [None, 'SELECCIONAR'] else jornada
		doc.estado_civil_personal = data['estado_civil'] if data.get('estado_civil') is not None else 'Soltero/a'
		doc.first_name = data['primer_nombre'].upper() if data.get('primer_nombre') is not None else ''
		doc.middle_name = data['segundo_nombre'].upper() if data.get('segundo_nombre') is not None else ''
		doc.first_last_name = data['apellido_paterno'].upper() if data.get('apellido_paterno') is not None else ''
		doc.second_last_name = data['apellido_materno'].upper() if data.get('apellido_materno') is not None else ''
		doc.gender = data['genero'] if data.get('genero') is not None else ''
		doc.nombre_completo = data['nombre_solicitante'].upper() if data.get('nombre_solicitante') is not None else ''
		doc.company = data['compania_trabajo'] if data.get('compania_trabajo') is not None else 'Shalom Empresarial'
		doc.date_of_birth = data['fecha_de_nacimiento'] if data.get('fecha_de_nacimiento') is not None else ''
		doc.designation = data['puesto_oportunidad'] if data.get('puesto_oportunidad') is not None else ''
		doc.branch = data['sucursal'] if data.get('sucursal') is not None else ''
		doc.personal_email = data['correo_electronico'] if data.get('correo_electronico') is not None else ''
		doc.passport_number = data['numero_documento'] if data.get('numero_documento') is not None else ''
		doc.current_address = data['direccion_postulante'] if data.get('direccion_postulante') is not None else ''
		doc.permanent_address = data['direccion_postulante'] if data.get('direccion_postulante') is not None else ''
		doc.dni = data['adj_copia_documento'] if data.get('adj_copia_documento') is not None else ''
		doc.cv = data['adj_cv'] if data.get('adj_cv') is not None else ''
		doc.edad_del_trabajador = data['edad'] if data.get('edad') is not None else ''
		doc.user_id = f"{data['numero_documento']}@shalomcontrol.com" if data.get('numero_documento') is not None else ''
		doc.company_email = f"{data['numero_documento']}@shalomcontrol.com" if data.get('numero_documento') is not None else ''
		doc.cell_number = data['número_de_teléfono'] if data.get('número_de_teléfono') is not None else ''
		doc.grade = 'CONDUCTOR' if data.get('puesto_oportunidad') in ['CONDUCTOR INTERPROVINCIAL', 'CONDUCTOR REGIONAL'] else 'OPERARIO'
		doc.status = 'Active' if data.get('puesto_oportunidad') in ['CONDUCTOR INTERPROVINCIAL', 'CONDUCTOR REGIONAL'] else 'PreActivo'
		doc.calificacion_trabajador = 'No Sujeto a Fiscalización' if data.get('puesto_oportunidad') in ['CONDUCTOR INTERPROVINCIAL', 'CONDUCTOR REGIONAL'] else 'Personal Sujeto a Fiscalización'
		doc.department = 'DISTRIBUCION - SE' if data.get('puesto_oportunidad') in ['CONDUCTOR INTERPROVINCIAL', 'CONDUCTOR REGIONAL'] else department
		doc.db_insert()

		license_categories = {
			"CONDUCTOR DE REPARTO": "A2B",
			"CONDUCTOR INTERPROVINCIAL": "A3C"
		}

		first_entry = list_cv_filtrado[0]

		if first_entry['licencia_de_conducir'] is not None:
			license_class = license_categories.get(first_entry['puesto_oportunidad'])
			if license_class:
				doc_license = frappe.get_doc({
					'doctype': 'Driver',
					'employee': doc.name,
					'license_number': first_entry['licencia_de_conducir'],
					'driving_license_category': {
						'parentfield': 'driving_license_category',
						'parenttype': 'Driver',
						'class': license_class
					}
				})
				doc_license.insert()

		update_student = frappe.db.set_value('Student',  employee['student'], {
			'empleado_creado': 1,
			'empleado': doc.name
		})

		if list_cv_filtrado[0]['sucursal'] in branchs:
			branch_employee = list_cv_filtrado[0]['sucursal'].split(" ")[0]
		else:
			branch_employee = list_cv_filtrado[0]['sucursal']

		doc_convenio = frappe.get_doc({
			'doctype': 'Convenio de Descuento',
			'empleado': doc.name,
			'fecha_inicio': fecha_actual,
			'fecha_inicio_texto': date_text,
			'sucursal_obs': branch_employee,
			'docstatus': 1,
			'empresa': list_cv_filtrado[0]['compania_trabajo'] if list_cv_filtrado[0]['compania_trabajo'] is not None else 'Shalom Empresarial'
		})
		doc_convenio.insert()

		return {
			'status': True,
			'message': 'Empleado Creado'
		}

@frappe.whitelist(allow_guest=True)
def clear_employee_exam(dni_student):

	list_student = frappe.get_all("Student", filters={"student_email_id": dni_student}, fields=['name','title'])
	if not list_student:
		return {
			'status': False,
			'message': 'No se encontro al estudiante'
		}

	student_name = list_student[0]['name']

	list_exam = frappe.get_all("Quiz Activity", filters={"student": student_name}, fields=['quiz', 'name'])
	if not list_exam:
		return {
			'status': True,
			'message': 'No hay examenes para eliminar'
		}
	else:
		for exam in list_exam:
			frappe.db.delete("Quiz Activity", {
				"name": exam['name']
			})
		verify_exam = frappe.get_all("Quiz Activity", filters={"student": student_name}, fields=['quiz', 'name'])
		if not verify_exam:
			return {
				'status': True,
				'message': 'Se eliminaron los examenes'
			}
		return {
			'status': False,
			'message': 'Error al eliminar los examenes'
		}

