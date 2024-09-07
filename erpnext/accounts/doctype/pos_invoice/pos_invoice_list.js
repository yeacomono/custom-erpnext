// Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

// render
frappe.listview_settings['POS Invoice'] = {
	add_fields: ["customer", "customer_name", "base_grand_total", "outstanding_amount", "due_date", "company",
		"currency", "is_return"],
	get_indicator: function(doc) {
		var status_color = {
			"Draft": "red",
			"Unpaid": "orange",
			"Paid": "green",
			"Submitted": "blue",
			"Consolidated": "green",
			"Return": "darkgrey",
			"Unpaid and Discounted": "orange",
			"Overdue and Discounted": "red",
			"Overdue": "red"

		};
		return [__(doc.status), status_color[doc.status], "status,=,"+doc.status];
	},
	right_column: "grand_total",
	onload: function(me) {


		if(frappe.user.has_role('System User') || frappe.user.has_role('Usuario POS') || frappe.user.has_role('Administrador de agencia')
			|| frappe.user.has_role('Supervisor Nacional') || frappe.user.has_role('Asist. Supervicion Nacional')
			|| frappe.user.has_role('Encargado de Store')){
			me.page.add_menu_item(__("Consolidar Ventas"), async function() {
				if (frappe.user.has_role('Encargado de Store')) {
					const search_permission_employee = await frappe.db.get_list('User Permission',{
						'filters':[
							['user','=',frappe.user.name],
							['allow','=',"Employee"]
						],
						'limit':'None',
						'fields': ['name']
					});

					console.log(search_permission_employee, 'search_permission_employee')

					if (search_permission_employee.length) {
						frappe.throw("El usuario tiene restricciones por permisos de empleado, contactar con soporte")
						return false
					}
				}

				if (frappe.user.name === "77050071@shalomcontrol.com" || frappe.user.name === "ingaamable@gmail.com"
					|| frappe.user.name === "aldairsanchez@overskull.pe" || frappe.user.has_role('Encargado de Store')) {
					let d = new frappe.ui.Dialog({
						title: 'Consolidar Ventas',
						fields: [
							{
								fieldtype : "Link",
								options     : "Branch",
								label   : "Terminal",
								fieldname : "sucursal",
								filters: {
									estado_de_sucursal: ['=','1']
								},
								reqd: 1
							},
						],
						primary_action_label: 'Consolidar',
						async primary_action(values) {
							d.hide();
							frappe.show_progress('Consolidando ventas.....', 20, 100, 'Please wait');
							try {
								const resultado = await $.ajax({
									type: "POST",
									url: "https://recursoshumanos.shalom.com.pe/api/pos-invoice-consolidated-master",
									dataType:"JSON",
									data:{
										"user": frappe.session.user,
										"branch": values.sucursal
									}
								});
								frappe.show_progress('Consolidando ventas.....', 90, 100, 'Please wait');
								console.log(resultado, 'resultado')
								setTimeout(()=>{
									frappe.hide_progress();
								},1000)

								if (resultado.valor === true) {
									frappe.msgprint(__(resultado.msn), __('Éxito'));
								} else {
									frappe.msgprint(__(resultado.msn), __('Error'));
								}
							} catch (error) {
								setTimeout(()=>{
									frappe.hide_progress();
								},1000)
								frappe.hide_progress();
								frappe.msgprint(__('Error al procesar la solicitud'), __('Error'));
							}
						}
					});
					d.show();
					return false
				}

				const buscar_empleado = await frappe.db.get_list('Employee', {
					filters: {
						'user_id': frappe.user.name
					},
					fields: ['designation']
				})

				if (buscar_empleado.length > 0) {
					if (buscar_empleado[0].designation == "ASISTENTE DE SUPERVISION NACIONAL" || buscar_empleado[0].designation == "SUPERVISOR PROVINCIA") {
						const buscar_permiso_zona = await frappe.db.get_list('User Permission', {
							filters: {
								'user': frappe.user.name,
								'allow': "Zonas Nacional"
							},
							fields: ['for_value']
						})

						if (!buscar_permiso_zona.length) {
							frappe.throw("Su usuario no cuenta con una zona asignada, contacte con soporte");
							return false
						}

						let names_zone = []

						for (let item of buscar_permiso_zona) {
							names_zone.push(item.for_value)
						}

						const obtener_sucursales = await frappe.db.get_list('Tabla de Sucursales',{
							'filters':[
								['parentfield','=','sucursales'],
								['parenttype','=','Zonas Nacional'],
								['parent','in',names_zone],
							],
							'limit':'None',
							'fields': ['agencias']
						});

						if (!obtener_sucursales.length) {
							frappe.throw("No hay sucursales asignadas a su zona, contacte con soporte")
							return false
						}

						let names_branch = []

						for (let item2 of obtener_sucursales) {
							names_branch.push(item2.agencias)
						}

						let d = new frappe.ui.Dialog({
							title: 'Consolidar Ventas',
							fields: [
								{
									fieldtype : "Link",
									options     : "Branch",
									label   : "Terminal",
									fieldname : "sucursal",
									filters: {
										estado_de_sucursal: ['=','1'],
										name: ["in", names_branch]
									},
									reqd: 1
								},
							],
							primary_action_label: 'Consolidar',
							async primary_action(values) {
								d.hide();
								frappe.show_progress('Consolidando ventas.....', 20, 100, 'Please wait');
								try {
									const resultado = await $.ajax({
										type: "POST",
										url: "https://recursoshumanos.shalom.com.pe/api/pos-invoice-consolidated-master",
										dataType:"JSON",
										data:{
											"user": frappe.session.user,
											"branch": values.sucursal
										}
									});
									frappe.show_progress('Consolidando ventas.....', 90, 100, 'Please wait');
									console.log(resultado, 'resultado')
									setTimeout(()=>{
										frappe.hide_progress();
									},1000)

									if (resultado.valor === true) {
										frappe.msgprint(__(resultado.msn), __('Éxito'));
									} else {
										frappe.msgprint(__(resultado.msn), __('Error'));
									}
								} catch (error) {
									setTimeout(()=>{
										frappe.hide_progress();
									},1000)
									frappe.hide_progress();
									frappe.msgprint(__('Error al procesar la solicitud'), __('Error'));
								}
							}
						});
						d.show();
						return false
					}
				}


				frappe.show_progress('Consolidando ventas.....', 10, 100, 'Please wait');

				if (!navigator.onLine) {
					frappe.msgprint(__('No hay conexión a Internet'), __('Error'));
					return;
				}

				frappe.show_progress('Consolidando ventas.....', 50, 100, 'Please wait');
				try {
					const resultado = await $.ajax({
						type: "POST",
						url: "https://recursoshumanos.shalom.com.pe/api/pos-invoice-consolidated-simple",
						dataType:"JSON",
						data:{
							"user": frappe.session.user
						}
					});
					frappe.show_progress('Consolidando ventas.....', 90, 100, 'Please wait');
					frappe.hide_progress();

					if (resultado.valor === true) {
						frappe.msgprint(__(resultado.msn), __('Éxito'));
					} else {
						frappe.msgprint(__(resultado.msn), __('Error'));
					}
				} catch (error) {
					frappe.hide_progress();
					frappe.msgprint(__('Error al procesar la solicitud'), __('Error'));
				}


			});
		}

		if(frappe.user.has_role('System User') || frappe.user.has_role('Usuario POS') || frappe.user.has_role('Administrador de agencia')
			|| frappe.user.has_role('Supervisor Nacional') || frappe.user.has_role('Asist. Supervicion Nacional')
			|| frappe.user.has_role('Encargado de Store')){
			me.page.add_menu_item(__("Desconsolidar Ventas"), async function() {
				if (frappe.user.has_role('Encargado de Store')) {
					const search_permission_employee = await frappe.db.get_list('User Permission',{
						'filters':[
							['user','=',frappe.user.name],
							['allow','=',"Employee"]
						],
						'limit':'None',
						'fields': ['name']
					});

					console.log(search_permission_employee, 'search_permission_employee')

					if (search_permission_employee.length) {
						frappe.throw("El usuario tiene restricciones por permisos de empleado, contactar con soporte")
						return false
					}
				}

				if (frappe.user.name === "77050071@shalomcontrol.com" || frappe.user.name === "ingaamable@gmail.com" || frappe.user.name === "aldairsanchez@overskull.pe"
					|| frappe.user.has_role('Encargado de Store')) {
					let d = new frappe.ui.Dialog({
						title: 'Desconsolidar Ventas',
						fields: [
							{
								fieldtype : "Link",
								options     : "Branch",
								label   : "Terminal",
								fieldname : "sucursal",
								filters: {
									estado_de_sucursal: ['=','1']
								},
								reqd: 1
							},
						],
						primary_action_label: 'Desconsolidar',
						async primary_action(values) {
							d.hide();
							frappe.show_progress('Desconsolidando ventas.....', 20, 100, 'Please wait');
							try {
								const resultado = await $.ajax({
									type: "POST",
									url: "https://recursoshumanos.shalom.com.pe/api/pos-invoice-desconsolidated-master",
									dataType:"JSON",
									data:{
										"user": frappe.session.user,
										"branch": values.sucursal
									}
								});
								frappe.show_progress('Desconsolidando ventas.....', 90, 100, 'Please wait');
								console.log(resultado, 'resultado')
								setTimeout(()=>{
									frappe.hide_progress();
								},1000)

								if (resultado.valor === true) {
									frappe.msgprint(__(resultado.msn), __('Éxito'));
								} else {
									frappe.msgprint(__(resultado.msn), __('Error'));
								}
							} catch (error) {
								setTimeout(()=>{
									frappe.hide_progress();
								},1000)
								frappe.hide_progress();
								frappe.msgprint(__('Error al procesar la solicitud'), __('Error'));
							}
						}
					});
					d.show();
					return false
				}

				const buscar_empleado = await frappe.db.get_list('Employee', {
					filters: {
						'user_id': frappe.user.name
					},
					fields: ['designation']
				})

				if (buscar_empleado.length) {
					if (buscar_empleado[0].designation == "ASISTENTE DE SUPERVISION NACIONAL" || buscar_empleado[0].designation == "SUPERVISOR PROVINCIA") {
						const buscar_permiso_zona = await frappe.db.get_list('User Permission', {
							filters: {
								'user': frappe.user.name,
								'allow': "Zonas Nacional"
							},
							fields: ['for_value']
						})

						if (!buscar_permiso_zona.length) {
							frappe.throw("Su usuario no cuenta con una zona asignada, contacte con soporte");
							return false
						}

						let names_zone = []

						for (let item of buscar_permiso_zona) {
							names_zone.push(item.for_value)
						}

						const obtener_sucursales = await frappe.db.get_list('Tabla de Sucursales',{
							'filters':[
								['parentfield','=','sucursales'],
								['parenttype','=','Zonas Nacional'],
								['parent','in',names_zone],
							],
							'limit':'None',
							'fields': ['agencias']
						});

						if (!obtener_sucursales.length) {
							frappe.throw("No hay sucursales asignadas a su zona, contacte con soporte")
							return false
						}

						let names_branch = []

						for (let item2 of obtener_sucursales) {
							names_branch.push(item2.agencias)
						}

						let d = new frappe.ui.Dialog({
							title: 'Desconsolidar Ventas',
							fields: [
								{
									fieldtype : "Link",
									options     : "Branch",
									label   : "Terminal",
									fieldname : "sucursal",
									filters: {
										estado_de_sucursal: ['=','1'],
										name: ["in", names_branch]
									},
									reqd: 1
								},
							],
							primary_action_label: 'Desconsolidar',
							async primary_action(values) {
								d.hide();
								frappe.show_progress('Desconsolidando ventas.....', 20, 100, 'Please wait');
								try {
									const resultado = await $.ajax({
										type: "POST",
										url: "https://recursoshumanos.shalom.com.pe/api/pos-invoice-desconsolidated-master",
										dataType:"JSON",
										data:{
											"user": frappe.session.user,
											"branch": values.sucursal
										}
									});
									frappe.show_progress('Desconsolidando ventas.....', 90, 100, 'Please wait');
									console.log(resultado, 'resultado')
									setTimeout(()=>{
										frappe.hide_progress();
									},1000)

									if (resultado.valor === true) {
										frappe.msgprint(__(resultado.msn), __('Éxito'));
									} else {
										frappe.msgprint(__(resultado.msn), __('Error'));
									}
								} catch (error) {
									setTimeout(()=>{
										frappe.hide_progress();
									},1000)
									frappe.hide_progress();
									frappe.msgprint(__('Error al procesar la solicitud'), __('Error'));
								}
							}
						});
						d.show();
						return false
					}
				}



				frappe.show_progress('Desconsolidando ventas.....', 10, 100, 'Please wait');

				if (!navigator.onLine) {
					frappe.msgprint(__('No hay conexión a Internet'), __('Error'));
					return;
				}

				frappe.show_progress('Desconsolidando ventas.....', 50, 100, 'Please wait');
				try {
					const resultado = await $.ajax({
						type: "POST",
						url: "https://recursoshumanos.shalom.com.pe/api/pos-invoice-desconsolidated-simple",
						dataType:"JSON",
						data:{
							"user": frappe.session.user
						}
					});
					frappe.show_progress('Desconsolidando ventas.....', 90, 100, 'Please wait');
					frappe.hide_progress();

					if (resultado.valor === true) {
						frappe.msgprint(__(resultado.msn), __('Éxito'));
					} else {
						frappe.msgprint(__(resultado.msn), __('Error'));
					}
				} catch (error) {
					frappe.hide_progress();
					frappe.msgprint(__('Error al procesar la solicitud'), __('Error'));
				}

			});
		}

		me.page.add_action_item('Make Merge Log', function() {
			const invoices = me.get_checked_items();
			frappe.call({
				method: "erpnext.accounts.doctype.pos_invoice.pos_invoice.make_merge_log",
				freeze: true,
				args:{
					"invoices": invoices
				},
				callback: function (r) {
					if (r.message) {
						var doc = frappe.model.sync(r.message)[0];
						frappe.set_route("Form", doc.doctype, doc.name);
					}
				}
			});
		});
	},
};
