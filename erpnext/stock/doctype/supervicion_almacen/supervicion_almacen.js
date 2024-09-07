// Copyright (c) 2023, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

const verificarColumnaEncontradoTabla = ( frm ) => {

    if ( frm.doc.tabsupervicion.length ) {

        let estado = false

        for ( let item of frm.doc.tabsupervicion ) {
            if ( item.encontrado == undefined || item.encontrado === "" ) {
                estado = false
                break
            } else {
                estado = true
            }
        }

        return estado

    } else {
        return false
    }

}

const crear_reconocimiento_deuda = async ( id_empleado, amount, month_text, year ) => {
    frappe.show_progress('Loading..', 50, 100, 'Please wait');
    const insert = await frappe.db.insert({
        doctype: 'Reconociemientos de Deuda',
        empleado: id_empleado,
        motivo: 'FALTANTE DE CAJA DE SHALOM STORE',
        monto_total: amount,
        docstatus: 0,
        table_21: [{
            mes: month_text,
            monto: amount,
            ano: year
        }]
    })
    frappe.show_progress('Loading..', 60, 100, 'Please wait');
    return {
        status: true,
        msn: "Creado con Exito",
        name: insert.name
    }
}

const crear_factura_pos_concesionario = async ( customer, branch, curren_date, warehouse, table_data, type_warehouse ) => {
    const obtener_data_perfil_pos = await frappe.db.get_list('POS Profile', {
        filters: {
            'branch': branch
        },
        fields:['name', 'company']
    })

    if ( obtener_data_perfil_pos.length === 0 ) {
        return {
            status: false,
            msn: "Almacen no vinculado a perfil de pos"
        }
    }

    const obtener_data_branch = await frappe.db.get_list('Branch', {
        filters: {
            'name': branch
        },
        fields:['name', 'ruc']
    })

    if ( obtener_data_branch.length === 0 ) {
        return {
            status: false,
            msn: "Sucursal no encontrado"
        }
    }

    let array_products = []
    let qty_total = 0
    let amount_general = 0

    for ( let item of table_data ) {

        let diferencia = parseInt(item.cantidad) - parseInt(item.encontrado)

        if ( diferencia > 0 ) {
            array_products.push({
                item_code: item.codigoproducto,
                qty: diferencia,
            })
            qty_total += diferencia
            amount_general+= (item.valor_esperado_venta / item.cantidad) * diferencia
        }

    }
    frappe.show_progress('Loading..', 40, 100, 'Please wait');
    const insert = await frappe.db.insert({
        doctype: "POS Invoice",
        status: "Paid",
        customer: customer,
        sucursal: branch,
        pos_profile: obtener_data_perfil_pos[0].name,
        company: obtener_data_perfil_pos[0].company,
        posting_date: curren_date,
        posting_time: moment().format('HH:mm:ss'),
        due_date: curren_date,
        is_pos: 1,
        set_warehouse: warehouse,
        items: array_products,
        total_qty: qty_total,
        total_taxes_and_charges: 0,
        payments: [{
            mode_of_payment: "Efectivo",
            type: "Bank",
            parentfield: "payments",
            parenttype: "POS Invoice",
            account: "Efectivo - SE",
            doctype: "Sales Invoice Payment",
            amount: amount_general,
            base_amount: amount_general,
        }],
        grand_total: amount_general,
        base_change_amount: 0,
        change_amount: 0,
        account_for_change_amount: "Efectivo - SE",
        debit_to: "DEUDORES VARIOS - SE",
        status_comprobante: "Liquidaciones",
        documento: obtener_data_branch[0].ruc,
        tipo_de_venta: ( type_warehouse == "EMBALAJE" ) ? "Embalaje" : "Tienda",
        razon_social: obtener_data_perfil_pos[0].name,
        comprobante: 0,
        validacion: "No",
        docstatus: 1,
        update_stock: 1
    })
    frappe.show_progress('Loading..', 60, 100, 'Please wait');

    return {
        status: true,
        msn: "Creado con Exito",
        name: insert.name
    }
}

const crear_factura_pos = async ( customer, branch, curren_date, warehouse, table_data, document_employee, type_warehouse ,typeComprobante ) => {

    if (branch == "MEXICO") {
        var obtener_data_perfil_pos = [{
            "name": "MEXICO",
            "company": "Shalom Empresarial"
        }]

    } else {
        var obtener_data_perfil_pos = await frappe.db.get_list('POS Profile', {
            filters: {
                'branch': branch
            },
            fields:['name', 'company']
        })

        if ( obtener_data_perfil_pos.length === 0 ) {
            return {
                status: false,
                msn: "Almacen no vinculado a perfil de pos"
            }
        }
    }

    let array_products = []
    let qty_total = 0
    let amount_general = 0

    for ( let item of table_data ) {

        let diferencia = parseInt(item.cantidad) - parseInt(item.encontrado)

        if ( diferencia > 0 ) {
            array_products.push({
                item_code: item.codigoproducto,
                qty: diferencia,
            })
            qty_total += diferencia
            amount_general+= (item.valor_esperado_venta / item.cantidad) * diferencia
        }

    }
    frappe.show_progress('Loading..', 30, 100, 'Please wait');
    const insert = await frappe.db.insert({
        doctype: "POS Invoice",
        status: "Paid",
        customer: customer,
        sucursal: branch,
        pos_profile: obtener_data_perfil_pos[0].name,
        company: obtener_data_perfil_pos[0].company,
        posting_date: curren_date,
        posting_time: moment().format('HH:mm:ss'),
        due_date: curren_date,
        is_pos: 1,
        set_warehouse: warehouse,
        items: array_products,
        total_qty: qty_total,
        total_taxes_and_charges: 0,
        payments: [{
            mode_of_payment: "Efectivo",
            type: "Bank",
            parentfield: "payments",
            parenttype: "POS Invoice",
            account: "Efectivo - SE",
            doctype: "Sales Invoice Payment",
            amount: amount_general,
            base_amount: amount_general
        }],
        grand_total: amount_general,
        base_change_amount: 0,
        change_amount: 0,
        account_for_change_amount: "Efectivo - SE",
        debit_to: "DEUDORES VARIOS - SE",
        ver_boton_comprobamte: 1,
        status_comprobante: typeComprobante,
        documento: document_employee,
        tipo_de_venta: ( type_warehouse == "EMBALAJE" ) ? "Embalaje" : "Tienda",
        razon_social: obtener_data_perfil_pos[0].name,
        comprobante: 0,
        validacion: "No",
        docstatus: 1,
        update_stock: 1
    })
    frappe.show_progress('Loading..', 40, 100, 'Please wait');
    return {
        status: true,
        msn: "Creado con Exito",
        name: insert.name
    }
}

frappe.ui.form.on('Supervicion Almacen', {
    refresh: function(frm) {

        let almacenesRecFac = ["Tienda","EMBALAJE","SERVICIOS"]

        let estado_columna_encontrado = verificarColumnaEncontradoTabla( frm )

        if ( !frm.is_new() && frappe.user_roles.includes('Gestion Store') && almacenesRecFac.includes(frm.doc.tipo_de_almacen)
            && frm.doc.concesionario === 0  && frm.doc.status === "Con Errores" && frm.doc.precio_de_venta_total_del_faltante > 0 && estado_columna_encontrado ) {
            frm.set_df_property("factura_y_reconocimiento_section","hidden",0)
        }

        if (  !frm.is_new() && frappe.user_roles.includes('Gestion Store') && almacenesRecFac.includes(frm.doc.tipo_de_almacen)
            && frm.doc.concesionario === 1  && frm.doc.status === "Con Errores" && frm.doc.precio_de_venta_total_del_faltante_dos > 0
            && estado_columna_encontrado && frm.doc.total_esperado_venta && frm.doc.total_encontrado_venta ) {
            frm.set_df_property("section_break_15","hidden",0)
        }

        $('button[data-fieldname="boton_crear_factura_reconocimiento"]').css({"color":"white", "background-color": "#3399ff", "font-weight": "400", "padding":"10px 18px","margin-top":"22px"});
        $('button[data-fieldname="crear_factura_y_liquidacion"]').css({"color":"white", "background-color": "#3399ff", "font-weight": "400", "padding":"10px 18px","margin-top":"22px"});

        var $boton = $('button[data-fieldname="boton_crear_factura_reconocimiento"]')
        var $nuevoDiv = $('<svg style="margin-left:4px" xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-pencil-square" viewBox="0 0 16 16"><path d="M15.502 1.94a.5.5 0 0 1 0 .706L14.459 3.69l-2-2L13.502.646a.5.5 0 0 1 .707 0l1.293 1.293zm-1.75 2.456-2-2L4.939 9.21a.5.5 0 0 0-.121.196l-.805 2.414a.25.25 0 0 0 .316.316l2.414-.805a.5.5 0 0 0 .196-.12l6.813-6.814z"/><path fill-rule="evenodd" d="M1 13.5A1.5 1.5 0 0 0 2.5 15h11a1.5 1.5 0 0 0 1.5-1.5v-6a.5.5 0 0 0-1 0v6a.5.5 0 0 1-.5.5h-11a.5.5 0 0 1-.5-.5v-11a.5.5 0 0 1 .5-.5H9a.5.5 0 0 0 0-1H2.5A1.5 1.5 0 0 0 1 2.5v11z"/></svg>');
        $boton.append($nuevoDiv);

        var $boton2 = $('button[data-fieldname="crear_factura_y_liquidacion"]')
        var $nuevoDiv2 = $('<svg style="margin-left:4px" xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-pencil-square" viewBox="0 0 16 16"><path d="M15.502 1.94a.5.5 0 0 1 0 .706L14.459 3.69l-2-2L13.502.646a.5.5 0 0 1 .707 0l1.293 1.293zm-1.75 2.456-2-2L4.939 9.21a.5.5 0 0 0-.121.196l-.805 2.414a.25.25 0 0 0 .316.316l2.414-.805a.5.5 0 0 0 .196-.12l6.813-6.814z"/><path fill-rule="evenodd" d="M1 13.5A1.5 1.5 0 0 0 2.5 15h11a1.5 1.5 0 0 0 1.5-1.5v-6a.5.5 0 0 0-1 0v6a.5.5 0 0 1-.5.5h-11a.5.5 0 0 1-.5-.5v-11a.5.5 0 0 1 .5-.5H9a.5.5 0 0 0 0-1H2.5A1.5 1.5 0 0 0 1 2.5v11z"/></svg>');
        $boton2.append($nuevoDiv2);

        if ( frm.doc.total_esperado_venta && frm.doc.total_encontrado_venta ) {
            let diferencia = parseFloat(frm.doc.total_esperado_venta.replace(/,/g, '')) - parseFloat(frm.doc.total_encontrado_venta.replace(/,/g, ''))
            if ( frm.doc.precio_de_venta_total_del_faltante !== diferencia && !isNaN(diferencia) && cur_frm.doc.precio_de_venta_total_del_faltante != diferencia.toFixed(2)) {
                frm.set_value("precio_de_venta_total_del_faltante", diferencia.toFixed(2))
                frm.save()
            }
        }

        if ( frm.doc.total_esperado_venta && frm.doc.total_encontrado_venta ) {
            let diferencia = parseFloat(frm.doc.total_esperado_venta.replace(/,/g, '')) - parseFloat(frm.doc.total_encontrado_venta.replace(/,/g, ''))
            if ( frm.doc.precio_de_venta_total_del_faltante_dos !== diferencia && !isNaN(diferencia) && cur_frm.doc.precio_de_venta_total_del_faltante_dos != diferencia.toFixed(2)) {
                frm.set_value("precio_de_venta_total_del_faltante_dos", diferencia.toFixed(2))
                frm.save()
            }
        }

    },
    boton_crear_factura_reconocimiento(frm) {

        if ( frm.doc.factura_pos && frm.doc.reconocimiento_de_deuda ) {
            frape.throw("La factura de Venta y el reconocimiento ya fueron generados")
            return false
        }


        let mesTexto = {
            'January' : 'Enero',
            'February' : 'Febrero',
            'March' : 'Marzo',
            'April' : 'Abril',
            'May' : 'Mayo',
            'June' : 'Junio',
            'July' : 'Julio',
            'August' : 'Agosto',
            'September' : 'Setiembre',
            'October' : 'Octubre',
            'November' : 'Noviembre',
            'December' : 'Diciembre'
        }

        let mes = moment().format('MMMM')
        let ano = moment().format('YYYY')
        let fechaActual = frappe.datetime.get_today()
        let tituloDialogo = __('Creacion de Factura');
        if ( frappe.user.has_role('System Manager') || frappe.user.has_role('Gestion Store') ) {
            frappe.call({
                method: 'erpnext.stock.doctype.supervicion_almacen.supervicion_almacen.get_courts',
                args: {
                    month: mesTexto[mes],
                    year: ano,
                    current_date: fechaActual
                },
                callback: function(r) {

                    if ( r.message ) {
                        const d = new frappe.ui.Dialog({
                            title: tituloDialogo,
                            width: 400,
                            fields: [
                                {
                                    label: 'Tipo',
                                    fieldname: 'type',
                                    fieldtype: 'Select',
                                    options: ['Efectivo', 'Planilla'],
                                    reqd: 1,
                                    onchange: function(e) {
                                        if(this.value){
                                            if(this.value == 'Efectivo'){
                                                tituloDialogo = __('Creacion de Factura');
                                                $(d.fields_dict.employee.wrapper).hide()
                                                $(d.fields_dict.customer.wrapper).show()

                                                $(d.fields_dict.document_employee.wrapper).hide()
                                                $(d.fields_dict.full_name.wrapper).hide()
                                                $(d.fields_dict.branch.wrapper).hide()
                                                $(d.fields_dict.designation.wrapper).hide()
                                            }else{
                                                tituloDialogo = __('Creacion de Factura y reconocimiento de Deuda');
                                                $(d.fields_dict.employee.wrapper).show()
                                                $(d.fields_dict.customer.wrapper).show()
                                            }
                                        } else {
                                            $(d.fields_dict.employee.wrapper).hide()
                                            $(d.fields_dict.customer.wrapper).hide()
                                        }
                                        $(d.$wrapper).find('.modal-title').text(tituloDialogo);
                                    }
                                },
                                {
                                    label: 'ID Empleado',
                                    fieldname: 'employee',
                                    fieldtype: 'Link',
                                    options: 'Employee',
                                    filters: {
                                        branch: ['=',frm.doc.sucursal]
                                    },
                                    onchange: function(e) {
                                        if(this.value){
                                            frappe.call({
                                                method: 'erpnext.stock.doctype.supervicion_almacen.supervicion_almacen.get_employee',
                                                args: {
                                                    id_employee: this.value,
                                                },
                                                callback: function(r) {

                                                    if ( r.message ) {

                                                        if ( r.message.length === 0 ) {
                                                            frappe.throw('Error al obtener empleado')
                                                        }

                                                        $(d.fields_dict.document_employee.wrapper).show()
                                                        $(d.fields_dict.full_name.wrapper).show()
                                                        $(d.fields_dict.branch.wrapper).show()
                                                        $(d.fields_dict.designation.wrapper).show()

                                                        d.set_value('document_employee', r.message[0].passport_number)
                                                        d.set_value('full_name', r.message[0].name_employee)
                                                        d.set_value('branch', r.message[0].branch)
                                                        d.set_value('designation', r.message[0].designation)

                                                    }

                                                },
                                                error: function(err) {
                                                    console.log('Error en la llamada al servicio:', err);
                                                }
                                            });
                                        } else {
                                            $(d.fields_dict.document_employee.wrapper).hide()
                                            $(d.fields_dict.full_name.wrapper).hide()
                                            $(d.fields_dict.branch.wrapper).hide()
                                            $(d.fields_dict.designation.wrapper).hide()
                                        }
                                    }
                                },
                                {
                                    label: 'DNI Empleado',
                                    fieldname: 'document_employee',
                                    fieldtype: 'Data',
                                    read_only: 1,
                                },
                                {
                                    label: 'Nombre Completo',
                                    fieldname: 'full_name',
                                    fieldtype: 'Data',
                                    read_only: 1,
                                },
                                {
                                    label: 'Agencia',
                                    fieldname: 'branch',
                                    fieldtype: 'Link',
                                    options: 'Branch',
                                    read_only: 1,
                                },
                                {
                                    label: 'Puesto',
                                    fieldname: 'designation',
                                    fieldtype: 'Link',
                                    options: 'Designation',
                                    read_only: 1,
                                },
                                {
                                    label: 'Cliente',
                                    fieldname: 'customer',
                                    fieldtype: 'Link',
                                    options: 'Customer',
                                    reqd: 1,
                                }
                            ],
                            primary_action_label: 'Crear',
                            async primary_action(values) {
                                d.hide();
                                var tipo = values.type;
                                console.log(tipo)
                                if(tipo == 'Planilla'){
                                    if(values.employee == undefined || values.employee == ''){
                                        console.log(values.employee)
                                        frappe.throw('EL id empleado es obligatorio para tipo Plantilla')
                                    }
                                    let name_pos_invoice = await crear_factura_pos( values.customer, values.branch, fechaActual, frm.doc.almacen, frm.doc.tabsupervicion, values.document_employee, frm.doc.tipo_de_almacen, 'Planilla',1 )
                                    let name_reconocimiento = await crear_reconocimiento_deuda( values.employee, frm.doc.precio_de_venta_total_del_faltante, mesTexto[mes], ano )
                                    frappe.show_progress('Loading..', 70, 100, 'Please wait');
                                    if ( name_pos_invoice.status ) {
                                        frm.set_value("factura_pos", name_pos_invoice.name)
                                    }
                                    frappe.show_progress('Loading..', 90, 100, 'Please wait');
                                    if ( name_reconocimiento.status ) {
                                        frm.set_value("reconocimiento_de_deuda", name_reconocimiento.name)
                                    }
                                }else{
                                    let name_pos_invoice = await crear_factura_pos( values.customer, frm.doc.sucursal, fechaActual, frm.doc.almacen, frm.doc.tabsupervicion, '', frm.doc.tipo_de_almacen, 'Efectivo',1 )
                                    frappe.show_progress('Loading..', 70, 100, 'Please wait');
                                    if ( name_pos_invoice.status ) {
                                        frm.set_value("factura_pos", name_pos_invoice.name)
                                    }
                                }



                                frappe.show_progress('Loading..', 100, 100, 'Please wait');
                                setTimeout(()=>{

                                    if ( frm.doc.__unsaved == 1 ) {
                                        frm.save()
                                    }
                                    frappe.hide_progress();
                                    frappe.msgprint("Se creo la factura y reconocimiento de deuda correctamente.")
                                },1000)

                            }
                        });
                        d.show();
                        $(d.fields_dict.employee.wrapper).hide()
                        $(d.fields_dict.customer.wrapper).hide()
                        $(d.fields_dict.document_employee.wrapper).hide()
                        $(d.fields_dict.full_name.wrapper).hide()
                        $(d.fields_dict.branch.wrapper).hide()
                        $(d.fields_dict.designation.wrapper).hide()
                    } else {
                        frappe.throw('No puede realizar acciones fuera del corte')
                    }

                },
                error: function(err) {
                    console.log('Error en la llamada al servicio:', err);
                }
            });


        } else {
            frappe.msgprint('Boton deshabilitado')
        }


    },
    crear_factura_y_liquidacion(frm){
        if( frappe.user.has_role('System Manager') || frappe.user.has_role('Gestion Store') ){
            if ( frm.doc.factura_pos_concesionaria ) {
                frape.throw("La factura de Venta ya ha sido generada")
                return false
            }
            let fechaActual = frappe.datetime.get_today()
            let d = new frappe.ui.Dialog({
                title: 'Generar factura de venta',
                fields: [
                    {
                        label: 'Cliente',
                        fieldname: 'customer',
                        fieldtype: 'Link',
                        options: 'Customer',
                        reqd: 1,
                    }
                ],
                primary_action_label: 'Generar',
                async primary_action(values) {
                    d.hide();
                    let name_pos_invoice = await crear_factura_pos_concesionario(values.customer, frm.doc.sucursal, fechaActual, frm.doc.almacen, frm.doc.tabsupervicion, frm.doc.tipo_de_almacen, 'Planilla',1  )
                    frappe.show_progress('Loading..', 70, 100, 'Please wait');
                    if ( name_pos_invoice.status ) {
                        frm.set_value("factura_pos_concesionaria", name_pos_invoice.name)
                    }
                    frappe.show_progress('Loading..', 80, 100, 'Please wait');
                    frappe.show_progress('Loading..', 100, 100, 'Please wait');
                    setTimeout(()=>{
                        if ( frm.doc.__unsaved == 1 ) {
                            frm.save()
                        }
                        frappe.hide_progress();
                        frappe.msgprint("Se creo la factura correctamente.")
                    },1000)

                }
            });
            d.show();


        }else{
            frappe.msgprint('Boton deshabilitado')
        }


    }
});
