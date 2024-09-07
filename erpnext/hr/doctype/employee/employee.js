// Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

frappe.provide("erpnext.hr");
erpnext.hr.EmployeeController = frappe.ui.form.Controller.extend({
	setup: function() {
		this.frm.fields_dict.user_id.get_query = function(doc, cdt, cdn) {
			return {
				query: "frappe.core.doctype.user.user.user_query",
				filters: {ignore_user_type: 1}
			}
		}
		this.frm.fields_dict.reports_to.get_query = function(doc, cdt, cdn) {
			return { query: "erpnext.controllers.queries.employee_query"} }
	},

	refresh: function() {
		var me = this;
		erpnext.toggle_naming_series();

	},

	date_of_birth: function() {
		return cur_frm.call({
			method: "get_retirement_date",
			args: {date_of_birth: this.frm.doc.date_of_birth}
		});
	},

	salutation: function() {
		if(this.frm.doc.salutation) {
			this.frm.set_value("gender", {
				"Mr": "Male",
				"Ms": "Female"
			}[this.frm.doc.salutation]);
		}
	},

});

function alert_loading_permission(time, title = "Actualizando Permisos de Administrador..."){
	frappe.show_progress(title, time, 100, 'Espere por favor');
}

let status_before = cur_frm.doc.status

frappe.ui.form.on('Employee',{
	refresh: async function(frm) {
		status_before = frm.doc.status
	},
	setup: function(frm) {
		frm.set_query("leave_policy", function() {
			return {
				"filters": {
					"docstatus": 1
				}
			};
		});
	},
	onload:function(frm) {
		frm.set_query("department", function() {
			return {
				"filters": {
					"company": frm.doc.company,
				}
			};
		});
	},
	prefered_contact_email:function(frm){
		frm.events.update_contact(frm)
	},
	personal_email:function(frm){
		frm.events.update_contact(frm)
	},
	company_email:function(frm){
		frm.events.update_contact(frm)
	},
	user_id:function(frm){
		frm.events.update_contact(frm)
	},
	update_contact:function(frm){
		var prefered_email_fieldname = frappe.model.scrub(frm.doc.prefered_contact_email) || 'user_id';
		frm.set_value("prefered_email",
			frm.fields_dict[prefered_email_fieldname].value)
	},
	status: function(frm) {
		return frm.call({
			method: "deactivate_sales_person",
			args: {
				employee: frm.doc.employee,
				status: frm.doc.status
			}
		});
	},
	create_user: function(frm) {
		if (!frm.doc.prefered_email)
		{
			frappe.throw(__("Please enter Preferred Contact Email"))
		}
		frappe.call({
			method: "erpnext.hr.doctype.employee.employee.create_user",
			args: { employee: frm.doc.name, email: frm.doc.prefered_email },
			callback: function(r)
			{
				frm.set_value("user_id", r.message)
			}
		});
	},
	assign_permissions_administrator: async function(frm) {
		alert_loading_permission(10)
		const get_admin_branch = await frappe.db.get_list('Employee',{
			'filters':[
				['branch','=',frm.doc.branch],
				['designation','=','ENCARGADO DE AGENCIA'],
				['status','=','Active'],
				['name','!=',frm.doc.name],
			],
			'limit':'None',
			'fields': ['name']
		});

		if (get_admin_branch.length > 0) {
			alert_loading_permission(50)
			return {
				status: false,
				message: "Ya existe un encargado de agencia para " + frm.doc.branch + " ,es " + get_admin_branch[0].name
			}
		}

		const update_check_employee = await frappe.db.set_value('Employee', frm.doc.name, {
			'create_user_permission': 0
		})

		alert_loading_permission(30)
		/* ELIMINADO PERMISO EMPLOYEE, PARA QUE VEA TODOS LOS EMPLEADOS DE SU SUCURSAL */
		frappe.call({
			type: "POST",
			method: "frappe.core.doctype.user_permission.user_permission.clear_user_permissions2",
			args: {
				"user": frm.doc.user_id
			},
			callback: function(r) {
				console.log(r, 'r2')
			}
		});

		/* ASIGNANDO ROL Y MODULOS DE ADMINISTRADOR */
		const update_user = await frappe.db.set_value('User', frm.doc.user_id, {
			'role_profile_name': "Administrador de sucursal",
			'module_profile': "ADMINISTRADOR AGENCIA",
			"mobile_no": frm.doc.passport_number
		})

		alert_loading_permission(50)
		/* ASIGNANDO PERMISO DE ALMACEN */
		const search_warehouse = await frappe.db.get_list('Warehouse', {
			filters: {
				'is_group': 1,
				'sucursal': frm.doc.branch,
			},
			fields: ['name']
		})

		if (!search_warehouse.length) {
			frappe.hide_progress();
			return {
				status: false,
				message: "La " + frm.doc.branch + ", no cuenta con almacen, contacte con soporte"
			}
		}

		let warehouse_id = search_warehouse[0].name

		const search_permission_warehouse = await frappe.db.get_list('User Permission', {
			filters: {
				'user': frm.doc.user_id,
				'allow': 'Warehouse',
				'for_value': warehouse_id
			},
			fields: ['name']
		})

		if (!search_permission_warehouse.length) {
			const insert_permission_warehouse = await frappe.db.insert({
				"doctype":"User Permission",
				"user": frm.doc.user_id,
				"allow": "Warehouse",
				"for_value": warehouse_id
			})
		}

		alert_loading_permission(60)
		/* ASIGNANDO PERMISO DE PERFIL POS */
		const search_pos_profile = await frappe.db.get_list('POS Profile', {
			filters: {
				'branch': frm.doc.branch,
			},
			fields: ['name']
		})

		if (!search_pos_profile.length) {
			frappe.hide_progress();
			return {
				status: false,
				message: "La " + frm.doc.branch + ", no cuenta con perfil pos, contacte con soporte"
			}
		}

		let pos_profile_id = search_pos_profile[0].name

		const search_permission_pos_profile = await frappe.db.get_list('User Permission', {
			filters: {
				'user': frm.doc.user_id,
				'allow': 'POS Profile',
				'for_value': pos_profile_id
			},
			fields: ['name']
		})

		if (!search_permission_pos_profile.length) {
			const insert_permission_pos_profile = await frappe.db.insert({
				"doctype":"User Permission",
				"user": frm.doc.user_id,
				"allow": "POS Profile",
				"for_value": pos_profile_id
			})
		}

		alert_loading_permission(70)
		/* ASIGNANDO PERMISO DE SUCURSAL */
		const search_permission_branch = await frappe.db.get_list('User Permission', {
			filters: {
				'user': frm.doc.user_id,
				'allow': 'Branch',
				'for_value': frm.doc.branch
			},
			fields: ['name']
		})

		if (!search_permission_branch.length) {
			const insert_permission_branch = await frappe.db.insert({
				"doctype":"User Permission",
				"user": frm.doc.user_id,
				"allow": "Branch",
				"for_value": frm.doc.branch
			})
		}

		alert_loading_permission(80)
		/* ASIGNANDO PERMISO DE CLIENTE */
		const search_customer = await frappe.db.get_list('Customer', {
			filters: {
				'agencia': frm.doc.branch
			},
			fields: ['name']
		})

		if (!search_customer.length) {
			frappe.hide_progress();
			return {
				status: false,
				message: "La " + frm.doc.branch + ", no cuenta con cliente, contacte con soporte"
			}
		}

		let customer_id = search_customer[0].name

		const search_permission_customer = await frappe.db.get_list('User Permission', {
			filters: {
				'user': frm.doc.user_id,
				'allow': 'Customer',
				'for_value': customer_id
			},
			fields: ['name']
		})

		if (!search_permission_customer.length) {
			const insert_permission_customer = await frappe.db.insert({
				"doctype":"User Permission",
				"user": frm.doc.user_id,
				"allow": "Customer",
				"for_value": customer_id
			})
		}

		alert_loading_permission(90)
		/* ASIGNANDO PERMISO DE COMPAÑIA */
		const search_permission_company = await frappe.db.get_list('User Permission', {
			filters: {
				'user': frm.doc.user_id,
				'allow': 'Company',
				'for_value': frm.doc.company
			},
			fields: ['name']
		})

		if (!search_permission_company.length) {
			const insert_permission_company = await frappe.db.insert({
				"doctype":"User Permission",
				"user": frm.doc.user_id,
				"allow": "Company",
				"for_value": frm.doc.company
			})
		}

		alert_loading_permission(100)
		frappe.hide_progress();

		return {
			status: true,
			message: "Los permisos de administrador fueron asignados correctamente"
		}
	},
	after_save: async function(frm) {
		let status_after = frm.doc.status
		if (status_before == "PreActivo" && status_after == "Active" && in_list(["ENCARGADO DE AGENCIA","ADMINISTRADOR DE AGENCIA"],frm.doc.designation)) {
			let func_assign_permissions_administrator = await frm.events.assign_permissions_administrator(frm)
			if (!func_assign_permissions_administrator.status) {
				const update_status_employee = await frappe.db.set_value('Employee', frm.doc.name, {
					'status': 'PreActivo'
				})
				frappe.hide_progress();
				frm.reload_doc()
				frappe.throw(func_assign_permissions_administrator.message)
				return false
			} else {
				frm.reload_doc()
				msgprint(func_assign_permissions_administrator.message)
			}
		}
	},
});
cur_frm.cscript = new erpnext.hr.EmployeeController({frm: cur_frm});
