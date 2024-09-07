function searchMonth(month){
	let months = ['Enero','Febrero','Marzo','Abril','Mayo','Junio','Julio','Agosto','Setiembre','Octubre','Noviembre','Diciembre']
	let num = months.indexOf(month);
	num = num+1
	let num_month = num<10? '0'+num:num
	return num_month
}

function searchMonth2(month){
	let months = ['Enero','Febrero','Marzo','Abril','Mayo','Junio','Julio','Agosto','Setiembre','Octubre','Noviembre','Diciembre']
	let num = months.indexOf(month);
	num = num+1
	return num;
}

frappe.listview_settings['Salary Slip'] = {
	add_fields: ["employee", "employee_name"],
	onload(listview) {

		let rolesUser = frappe.user_roles;

		if( !frappe.user.has_role('HR Manager') &&
			!frappe.user.has_role('System Manager') &&
			!frappe.user.has_role('Asist. Supervicion Nacional') &&
			!frappe.user.has_role('Supervisor Nacional') ){
			window.location.href = 'https://capacitacion.shalom.com.pe/app/hr';
		}

		if (rolesUser.includes("HR Manager")) {
			listview.page.add_menu_item(__("Generar TXT"), function() {
				let d = new frappe.ui.Dialog({
					title: 'Generación de Txts',
					fields: [
						{
							label: 'Tipo de txts',
							fieldname: 'tipo_txts',
							fieldtype: 'Select',
							options:["haberes","adelantos","reintegros","gratificacion","cts","apoyo","utilidades"]
						},
						{
							label: 'Compañia',
							fieldname: 'company',
							fieldtype: 'Link',
							options:'Company'

						},
						{
							label: 'Mes',
							fieldname: 'month',
							fieldtype: 'Select',
							options:["Enero","Febrero","Marzo","Abril","Mayo","Junio","Julio","Agosto","Setiembre","Octubre","Noviembre","Diciembre"]
						},
						{
							label: 'Año',
							fieldname: 'year',
							fieldtype: 'Select',
							options:["2022","2023","2024","2025","2026"]

						},
						{
							label: 'Banco',
							fieldname: 'banco',
							fieldtype: 'Select',
							options:["BCP","BBVA"]

						},
						{
							label: 'Grupo',
							fieldname: 'grupos_nomina',
							fieldtype: 'Select',
							options:["","Grupo 1","Grupo 2"]
						},
						{
							label: 'Estado de los Trabajador',
							fieldname: 'estado_trabajadores',
							fieldtype: 'Select',
							options:["Activos","Inactivos"]
						},
					],
					primary_action_label: 'Generar',
					async primary_action(values) {

						if (values.tipo_txts && values.tipo_txts !== "utilidades") {
							if(values.month==undefined){
								frappe.throw("Digite todos los campos");
								return false;
							}
						}

						if (values.tipo_txts && values.tipo_txts == "utilidades") {
							if(values.estado_trabajadores==undefined){
								frappe.throw("Digite el estado de los trabajadores");
								return false;
							}
						}
						if(values.year==undefined){
							frappe.throw("Digite todos los campos");
							return false;
						}
						if(values.company==undefined){
							frappe.throw("Digite todos los campos");
							return false;
						}
						if(values.banco==undefined){
							frappe.throw("Digite todos los campos");
							return false;
						}
						if(values.tipo_txts==undefined){
							frappe.throw("Digite todos los campos");
							return false;
						}
						d.hide();

						let grupo_1 = values.grupos_nomina !== undefined && values.grupos_nomina == "Grupo 1" ? 1 : 0
						let grupo_2 = values.grupos_nomina !== undefined && values.grupos_nomina == "Grupo 2" ? 1 : 0
						let date2 =  values.year + "-" +searchMonth(values.month)+"-01"
						let numdias = new Date(values.year, searchMonth2(values.month), 0).getDate();
						let date3 =  values.year + "-" +searchMonth(values.month)+"-"+numdias
						let body = {}
						let url = ""
						let bodytxt = {}
						switch(values.tipo_txts){
							case "haberes":
								if(values.banco=="BCP"){
									body = {
										"fh_init": date2,
										"fh_end": date3,
										"company": values.company,
										"service":"nomina",
										"name_month":values.month,
										"grupo_1": grupo_1,
										"grupo_2": grupo_2,

									}
									url = "https://recursoshumanos.shalom.com.pe/api/get-txt-salary-slip-bcp-interbank"
									bodytxt = {type: "text/plain",endings: "native"}
								}else{
									body = {
										"fh_init": date2,
										"fh_end": date3,
										"company": values.company,
										"name_month":values.month,
										"grupo_1": grupo_1,
										"grupo_2": grupo_2,
									}
									url = "https://recursoshumanos.shalom.com.pe/api/get-txt-salary-slip-bbva"
									bodytxt = {type: "text/plain"};
								}
								break;
							case "apoyo":
								if(values.banco=="BCP"){
									body = {
										"company": values.company,
										"month":values.month,
										"year":values.year,

									}
									url = "https://recursoshumanos.shalom.com.pe/api/txt-apoyos-bcp"
									bodytxt = {type: "text/plain",endings: "native"}
								}else{
									body = {
										"company": values.company,
										"month":values.month,
										"year":values.year,
									}
									url = "https://recursoshumanos.shalom.com.pe/api/txt-apoyos-bbva"
									bodytxt = {type: "text/plain"};
								}
								break;
							case "utilidades":
								body = {
									"service": 'utilidades',
									"company":values.company,
									"year":values.year,
									"status_employee": values.estado_trabajadores
								}

								if(values.banco=="BCP") {
									url = "https://recursoshumanos.shalom.com.pe/api/erp/txt/utilidades-2"
									//url = "https://horario-salida-qa-erpwin.shalom.com.pe/api/get-txt-salary-slip-bcp-interbank-2"
								} else {
									url = "https://recursoshumanos.shalom.com.pe/api/erp/txt/utilidades-3"
									//url = "https://horario-salida-qa-erpwin.shalom.com.pe/api/get-txt-salary-slip-bbva-utilidades"
								}


								bodytxt = {type: "text/plain"};
								break;
							case "adelantos":

								url = "https://recursoshumanos.shalom.com.pe/api/get-adelantos"

								if(values.banco=="BCP"){
									body = {
										"month": values.month,
										"year": values.year,
										"company": values.company,
										"banco":"BCP",
									}
									bodytxt = {type: "text/plain",endings: "native"}
								}else{
									body = {
										"month": values.month,
										"year": values.year,
										"company": values.company,
										"banco":"BBVA"
									}
									bodytxt = {type: "text/plain"};
								}
								break;
							case "reintegros":
								if(values.banco=="BCP"){
									body = {
										"fh_init": date2,
										"fh_end": date3,
										"company": values.company,
										"service":"reintegros",
										"name_month":values.month,
										"year": values.year,
										"grupo_1": grupo_1,
										"grupo_2": grupo_2,
									}
									url = "https://recursoshumanos.shalom.com.pe/api/get-txt-salary-slip-bcp-interbank"
									bodytxt = {type: "text/plain",endings: "native"}
								}else{
									body = {
										"fh_init": date2,
										"fh_end": date3,
										"company": values.company,
										"service":"reintegros",
										"name_month":values.month,
										"year": values.year,
										"grupo_1": grupo_1,
										"grupo_2": grupo_2,
									}
									url = "https://recursoshumanos.shalom.com.pe/api/get-txt-salary-slip-bbva"
									bodytxt = {type: "text/plain"};
								}
								break;
							case "gratificacion":
								if(values.banco == "BCP"){
									url = "https://recursoshumanos.shalom.com.pe/api/get-txt-salary-slip-bcp-interbank"
									body = {
										month:values.month,
										year:values.year,
										company:values.company,
										service:"gratificaciones",
										banco : "BCP"
									}
									bodytxt = {type: "text/plain",endings: "native"}
								}else{
									url = "https://recursoshumanos.shalom.com.pe/api/get-txt-salary-slip-bcp-interbank"
									body = {
										month:values.month,
										year:values.year,
										company:values.company,
										service:"gratificaciones",
										banco : "BBVA"
									}
									bodytxt = {type: "text/plain"};
								}
								break;
							case "cts":
								if(values.banco == "BCP"){
									url = "https://recursoshumanos.shalom.com.pe/api/get-cts-bcp"
									body = {
										month:values.month,
										year:values.year,
										company:values.company
									}
									bodytxt = {type: "text/plain",endings: "native"}
								}else{
									url = "https://recursoshumanos.shalom.com.pe/api/get-cts-bbva"
									body = {
										month:values.month,
										year:values.year,
										company:values.company
									}
									bodytxt = {type: "text/plain"};
								}
								break;
						}
						frappe.require('assets/erpnext/js/fil_saver.js', async () => {
							const service = await $.ajax({
								"type":"post",
								"url":url,
								"data":body
							})
							console.log(service, 'service')
							if(service.valor){
								let message = service.txt_header+"\n"+service.txt_lines
								var blob = new Blob([message], bodytxt);
								if (!service.time) {
									saveAs(blob, values.tipo_txts.toUpperCase()+service.fecha);
								} else {
									saveAs(blob, values.tipo_txts.toUpperCase()+service.fecha+"_"+service.time);
								}

							}else{
								frappe.throw(service.msn);
								return false;
							}
						})
					}
				})
				$(d.fields_dict.grupos_nomina.wrapper).hide()
				$(d.fields_dict.month.wrapper).hide()
				$(d.fields_dict.estado_trabajadores.wrapper).hide()
				$(d.fields_dict.tipo_txts.input).click(function ( e ){
					if ( e.target.value && e.target.value !== "utilidades" ) {
						$(d.fields_dict.grupos_nomina.wrapper).show()
						$(d.fields_dict.month.wrapper).show()
						$(d.fields_dict.estado_trabajadores.wrapper).hide()
					} else if ( e.target.value && e.target.value == "utilidades" ) {
						$(d.fields_dict.grupos_nomina.wrapper).hide()
						$(d.fields_dict.month.wrapper).hide()
						$(d.fields_dict.estado_trabajadores.wrapper).show()
					}
				})
				d.show();
			})
		}

		if (rolesUser.includes("System Manager")) {
			listview.page.add_menu_item(__("Eliminar Nominas"), function () {
				let d = new frappe.ui.Dialog({
					title: 'Eliminar Nominas',
					fields: [
						{
							label: 'Mes',
							fieldname: 'month',
							fieldtype: 'Select',
							options: ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Setiembre", "Octubre", "Noviembre", "Diciembre"]
						},
						{
							label: 'Año',
							fieldname: 'year',
							fieldtype: 'Select',
							options: ["2022", "2023", "2024", "2025", "2026"]

						},
					],
					primary_action_label: 'Generar',
					async primary_action(values) {

						if (!values.year) {
							frappe.throw("Seleccione el Año");
							return false;
						}

						if (!values.month) {
							frappe.throw("Seleccione el Mes");
							return false;
						}

						frappe.call({
							type: "POST",
							method: "erpnext.payroll.doctype.salary_slip.salary_slip.delete_salary_slip_massive",
							args: {
								"month": values.month,
								"year": values.year
							},
							freeze: true,
							callback: function (r) {
								console.log(r.exc, 'r.exc')
								console.log(r, 'r')
								if (r.message.status) {
									frappe.show_alert({
										message: __(r.message.message),
										indicator: 'orange'
									});
									listview.refresh();
								}
							}
						});
						d.hide();
					}
				})
				d.show();
			})

			listview.page.add_menu_item(__("Boletas Antiguas"), function () {
				let d = new frappe.ui.Dialog({
					title: 'Eliminar Nominas',
					fields: [
						{
							label: 'Empleado',
							fieldname: 'empleado',
							fieldtype: 'Link',
							options: 'Employee'
						},
						{
							label: 'Fecha Inicio(Primer dia del mes)',
							fieldname: 'fecha_inicio',
							fieldtype: 'Date',
						},
					],
					primary_action_label: 'Generar',
					async primary_action(values) {

						if (!values.empleado) {
							frappe.throw("Seleccione un empleado");
							return false;
						}

						if (!values.fecha_inicio) {
							frappe.throw("Seleccione la fecha de inicio");
							return false;
						}

						window.open(`${frappe.boot.DOMINIOS.QA.RRHH_NIGHT}/api/test-pdf/${values.fecha_inicio}/${values.empleado}`, '_blank')

					}
				})
				d.show();
			})
		}

	},
	before_render(){
		let rolesUser = frappe.user_roles;

		if (rolesUser.includes("System Manager")) {
			if (!$('#boton_generate_app').length){
				var boton3 = document.createElement("button");
				boton3.textContent = "Actualizar Nominas";
				boton3.className = "btn btn-primary btn-sm primary-action text-center";
				boton3.id = "boton_generate_app";
				boton3.style= 'height:24px; width:139px; margin-left: 0.85%; margin-top: 0.9%;padding: inherit;';

				boton3.addEventListener("click", async () => {
					window.open('https://recursoshumanos.shalom.com.pe/procesador-async/true#/', '_blank');
				})
			}

			$(".standard-filter-section").append(boton3);

			if ($(".standard-filter-section").length == 2){
				$('#boton_generate_app')[0].remove()
			}
		}

		if (!rolesUser.includes("System Manager")) {
			$('li:has(a.grey-link.dropdown-item span.menu-item-label[data-label="Editar"])').hide();
		}

		if (rolesUser.includes("HR Manager")) {

			if (!$('#btnGenerateTxts').length){
				var boton2 = document.createElement("button");
				boton2.textContent = "Generar TXT";
				boton2.className = "btn btn-primary btn-sm primary-action text-center";
				boton2.id = "btnGenerateTxts";
				boton2.style= 'height:24px; width:139px; margin-left: 0.85%; margin-top: 0.9%;padding: inherit;';

				boton2.addEventListener("click", async () => {
					console.log("click here")
					let d = new frappe.ui.Dialog({
						title: 'Generación de Txts',
						fields: [
							{
								label: 'Compañia',
								fieldname: 'company',
								fieldtype: 'Link',
								options:'Company'

							},
							{
								label: 'Mes',
								fieldname: 'month',
								fieldtype: 'Select',
								options:["Enero","Febrero","Marzo","Abril","Mayo","Junio","Julio","Agosto","Setiembre","Octubre","Noviembre","Diciembre"]
							},
							{
								label: 'Año',
								fieldname: 'year',
								fieldtype: 'Select',
								options:["2022","2023","2024","2025","2026"]

							},
							{
								label: 'Banco',
								fieldname: 'banco',
								fieldtype: 'Select',
								options:["BCP","BBVA"]

							},
							{
								label: 'Tipo de txts',
								fieldname: 'tipo_txts',
								fieldtype: 'Select',
								options:["haberes","adelantos","reintegros","gratificacion","cts","apoyo","utilidades"]
							},
							{
								label: 'Grupo',
								fieldname: 'grupos_nomina',
								fieldtype: 'Select',
								options:["","Grupo 1","Grupo 2"]
							},
						],
						primary_action_label: 'Generar',
						async primary_action(values) {

							if(values.month==undefined){
								frappe.throw("Digite todos los campos");
								return false;
							}
							if(values.year==undefined){
								frappe.throw("Digite todos los campos");
								return false;
							}
							if(values.company==undefined){
								frappe.throw("Digite todos los campos");
								return false;
							}
							if(values.banco==undefined){
								frappe.throw("Digite todos los campos");
								return false;
							}
							if(values.tipo_txts==undefined){
								frappe.throw("Digite todos los campos");
								return false;
							}
							d.hide();

							let grupo_1 = values.grupos_nomina !== undefined && values.grupos_nomina == "Grupo 1" ? 1 : 0
							let grupo_2 = values.grupos_nomina !== undefined && values.grupos_nomina == "Grupo 2" ? 1 : 0
							console.log(grupo_1,'grupo_1')
							console.log(grupo_2,'grupo_2')
							let date2 =  values.year + "-" +searchMonth(values.month)+"-01"
							let numdias = new Date(values.year, searchMonth2(values.month), 0).getDate();
							let date3 =  values.year + "-" +searchMonth(values.month)+"-"+numdias
							let body = {}
							let url = ""
							let bodytxt = {}
							switch(values.tipo_txts){
								case "haberes":
									if(values.banco=="BCP"){
										body = {
											"fh_init": date2,
											"fh_end": date3,
											"company": values.company,
											"service":"nomina",
											"name_month":values.month,
											"grupo_1": grupo_1,
											"grupo_2": grupo_2,

										}
										url = "https://recursoshumanos.shalom.com.pe/api/get-txt-salary-slip-bcp-interbank"
										bodytxt = {type: "text/plain",endings: "native"}
									}else{
										body = {
											"fh_init": date2,
											"fh_end": date3,
											"company": values.company,
											"name_month":values.month,
											"grupo_1": grupo_1,
											"grupo_2": grupo_2,
										}
										url = "https://recursoshumanos.shalom.com.pe/api/get-txt-salary-slip-bbva"
										bodytxt = {type: "text/plain"};
									}
									break;
								case "apoyo":
									if(values.banco=="BCP"){
										body = {
											"company": values.company,
											"month":values.month,
											"year":values.year,
										}
										url = "https://recursoshumanos.shalom.com.pe/api/txt-apoyos-bcp"
										bodytxt = {type: "text/plain",endings: "native"}
									}else{
										body = {
											"company": values.company,
											"month":values.month,
											"year":values.year,
										}
										url = "https://recursoshumanos.shalom.com.pe/api/txt-apoyos-bbva"
										bodytxt = {type: "text/plain"};
									}
									break;
								case "utilidades":
									body = {
										"company": values.company,
										"banco":values.banco,
										"year":values.year,
									}
									url = "https://recursoshumanos.shalom.com.pe/api/erp/txt/utilidades"
									bodytxt = {type: "text/plain"};
									break;
								case "adelantos":

									url = "https://recursoshumanos.shalom.com.pe/api/get-adelantos"

									if(values.banco=="BCP"){
										body = {
											"month": values.month,
											"year": values.year,
											"company": values.company,
											"banco":"BCP",
										}
										bodytxt = {type: "text/plain",endings: "native"}
									}else{
										body = {
											"month": values.month,
											"year": values.year,
											"company": values.company,
											"banco":"BBVA"
										}
										bodytxt = {type: "text/plain"};
									}
									break;
								case "reintegros":
									if(values.banco=="BCP"){
										body = {
											"fh_init": date2,
											"fh_end": date3,
											"company": values.company,
											"service":"reintegros",
											"name_month":values.month,
											"year": values.year,
										}
										url = "https://recursoshumanos.shalom.com.pe/api/get-txt-salary-slip-bcp-interbank"
										bodytxt = {type: "text/plain",endings: "native"}
									}else{
										body = {
											"fh_init": date2,
											"fh_end": date3,
											"company": values.company,
											"service":"reintegros",
											"name_month":values.month,
											"year": values.year,
										}
										url = "https://recursoshumanos.shalom.com.pe/api/get-txt-salary-slip-bbva"
										bodytxt = {type: "text/plain"};
									}
									break;
								case "gratificacion":
									if(values.banco == "BCP"){
										url = "https://recursoshumanos.shalom.com.pe/api/get-txt-salary-slip-bcp-interbank"
										body = {
											month:values.month,
											year:values.year,
											company:values.company,
											service:"gratificaciones",
											banco : "BCP"
										}
										bodytxt = {type: "text/plain",endings: "native"}
									}else{
										url = "https://recursoshumanos.shalom.com.pe/api/get-txt-salary-slip-bcp-interbank"
										body = {
											month:values.month,
											year:values.year,
											company:values.company,
											service:"gratificaciones",
											banco : "BBVA"
										}
										bodytxt = {type: "text/plain"};
									}
									break;
								case "cts":
									if(values.banco == "BCP"){
										url = "https://recursoshumanos.shalom.com.pe/api/get-cts-bcp"
										body = {
											month:values.month,
											year:values.year,
											company:values.company
										}
										bodytxt = {type: "text/plain",endings: "native"}
									}else{
										url = "https://recursoshumanos.shalom.com.pe/api/get-cts-bbva"
										body = {
											month:values.month,
											year:values.year,
											company:values.company
										}
										bodytxt = {type: "text/plain"};
									}
									break;
							}
							console.log(url,'url')
							console.log(body,'body')
							frappe.require('assets/erpnext/js/fil_saver.js', async () => {
								const service = await $.ajax({
									"type":"post",
									"url":url,
									"data":body
								})
								console.log(service, 'service')
								if(service.valor){
									let message = service.txt_header+"\n"+service.txt_lines
									var blob = new Blob([message], bodytxt);
									saveAs(blob, values.tipo_txts.toUpperCase()+service.fecha);
								}else{
									frappe.throw(service.msn);
									return false;
								}
							})
						}
					})
					d.show();
				})
			}

			$(".standard-filter-section").append(boton2);
			if ($(".standard-filter-section").length == 2){
				$('#btnGenerateTxts')[0].remove()
			}
		}

	},
	refresh(listview){
		if( !frappe.user.has_role('HR Manager') &&
			!frappe.user.has_role('System Manager') &&
			!frappe.user.has_role('Asist. Supervicion Nacional') &&
			!frappe.user.has_role('Supervisor Nacional') ){

			window.location.href = 'https://capacitacion.shalom.com.pe/app/hr';
		}
	}
}

