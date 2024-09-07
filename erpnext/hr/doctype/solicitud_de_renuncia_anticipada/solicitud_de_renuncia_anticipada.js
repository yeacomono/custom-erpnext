var guardar = false

function alertLoading(time, title = "Actualizando Alerta..."){
    frappe.show_progress(title, time, 100, 'Espere por favor');
}

const validateEmployee = async (frm) => {
    let empleadoName = frm.doc.empleado

    const validateEmpleado = await frappe.db.get_list('Employee', {
        filters: {
            'name': empleadoName,
        },
        fields: ['status']
    })
    if(validateEmpleado[0].status !== 'Active'){
        frm.set_value('empleado', '')
        frappe.throw('El trabajador elegido no está activo, comunicarse con RRHH')
        return false
    }
}

const inactivateEmployee = async (frm,tipo_relevo) => {
    let empleadoName = frm.doc.empleado
    let fechaRenuncia = frm.doc.fecha_de_renuncia

    const verificarEmpleado = await frappe.db.get_list('Employee', {
        filters: {
            'name': empleadoName
        },
        fields: ['status']
    })

    if(verificarEmpleado[0].status === 'Inactive'){
        frappe.throw('El empleado está inactivo')
    } else {
        const actualizarEstado = await frappe.db.set_value('Employee', empleadoName, {
            'status': 'Inactive',
            'fecha_de_relevo': fechaRenuncia,
            'tipo_de_reelevo': frm.doc.termino_de_contrato == "TERMINO DE CONTRATO POR TRABAJADOR" ? "RENUNCIA VOLUNTARIA" : "TERMINO DE CONTRATO",
            'termino_de_contrato_por': frm.doc.termino_de_contrato == "TERMINO DE CONTRATO POR TRABAJADOR" ? "" : frm.doc.termino_de_contrato,
            'grado_1': frm.doc.grado_1 ? frm.doc.grado_1 : "",
            'grado_2': frm.doc.grado_2 ? frm.doc.grado_2 : "",

        })
        console.log(actualizarEstado, 'actualizarEstado')
    }

}

const disabledUser = async (frm) => {

    let usuarioId = frm.doc.usuario

    const verificarUsuario = await frappe.db.get_list('User', {
        filters: {
            'name': usuarioId
        },
        fields: ['enabled']
    })
    if(verificarUsuario[0].enabled === 0){
        frappe.throw('El usuario está deshabilitado')
        return false
    } else {
        const actualizarUsuario = await frappe.db.set_value('User', usuarioId, {
            'enabled': 0
        })
        console.log(actualizarUsuario, 'actualizarEstado')
    }

}

const generateLiquidation = async (frm) => {

    let empleadoName = frm.doc.empleado
    let response = await $.ajax({
        type:"GET",
        url:'https://recursoshumanos.shalom.com.pe/api/liquidacion/generar/'+empleadoName,
        dataType:"JSON"
    });
    console.log(response, 'response')
}

const registerBlackList = async (frm) => {

    if (frm.doc.termino_de_contrato == "TERMINO DE CONTRATO POR JEFE") {
        const registerBlackList = await frappe.db.insert({
            doctype:"Black List",
            empleado:frm.doc.empleado
        })
    }

}

const automationRequest = async (frm) => {
    alertLoading(10,"Validando renuncia...")
    await inactivateEmployee(frm)
    alertLoading(30,"Validando renuncia...")
    await disabledUser(frm)
    alertLoading(50,"Validando renuncia...")
    await generateLiquidation(frm)
    alertLoading(80,"Validando renuncia...")
    await registerBlackList(frm),
        alertLoading(100,"Validando renuncia...")
    setTimeout(()=>{
        frappe.hide_progress();
        frappe.msgprint("Validación concretada correctamente.")
    },1000)
}

const modalToSelectedGrade = async ( frm, cdt, cdn ) => {

    let row = locals[cdt][cdn];
    let d = new frappe.ui.Dialog({
        title: 'Seleccione el Grado',
        fields: [
            {
                label: 'Grado 1',
                fieldname: 'grado_1',
                fieldtype: 'Select',
                options:["","NO RENOVACION VOLUNTARIA","NO SUPERACION DE PERIODO DE PRUEBA","NO RESPETAR HORARIO DE TRABAJO","INASISTENCIAS INJUSTIFICADAS","INCUMPLIMIENTO DE FUNCIONES","INVALIDEZ ABSOLUTA (TEMPORAL)"]
            },
            {
                label: 'Grado 2',
                fieldname: 'grado_2',
                fieldtype: 'Select',
                options:["","HURTO (MERCADERIA, DINERO, EQUIPOS)","GRESCAS Y/O CAUSANTES DE LESION","ABANDONO LABORAL","NO ACEPTAR RECONOCIMIENTO DE DEUDA","FALSIFICACION DE DESCANSOS MEDICOS","MALAS PRACTICAS EN SUS FUNCIONES","ACOSO Y/O HOSTIGAMIENTO LABORAL","LLEGAR EN ESTADO ETILICO Y/O ESTUPEFACIENTES","DESACATO DE AUTORIDAD","INVALIDEZ ABSOLUTA (PERMANENTE)"]
            },
        ],
        primary_action_label: 'Submit',
        primary_action(values) {
            console.log("values", values)
            if ( values.grado_1 == undefined && values.grado_2 == undefined ) {
                frappe.throw(__('Debe seleccionar un almenos un grado.'));
                return false;
                d.show();
            }

            if ( values.grado_1 !== undefined && values.grado_2 !== undefined ) {
                frappe.throw(__('Solo debe seleccionar un grado.'));
                return false
                d.show();
            }


            if ( values.grado_1 !== undefined ) {

                frm.set_value("grado_1",values.grado_1)
                frm.set_value("grado_2","")
            } else {

                frm.set_value("grado_1","")
                frm.set_value("grado_2",values.grado_2)
            }

            d.hide();

        }
    });

    d.show()
}

const modalGradoRenuncia = async  () =>{
    let d = new frappe.ui.Dialog({
        title: 'Termino de contrato',
        fields: [

            {
                label: 'Grado 1',
                fieldname: 'grado_1',
                fieldtype: 'Select',
                options: [
                    "",
                    "NO RENOVACION VOLUNTARIA",
                    "NO SUPERACION DE PERIODO DE PRUEBA",
                    "NO RESPETAR HORARIO DE TRABAJO",
                    "INASISTENCIAS INJUSTIFICADAS",
                    "INCUMPLIMIENTO DE FUNCIONES",
                    "INVALIDEZ ABSOLUTA (TEMPORAL)"
                ]
            },
            {
                label: 'Grado 2',
                fieldname: 'grado_2',
                fieldtype: 'Select',
                options: [
                    "",
                    "HURTO (MERCADERIA, DINERO, EQUIPOS)",
                    "GRESCAS Y/O CAUSANTES DE LESION",
                    "ABANDONO LABORAL",
                    "NO ACEPTAR RECONOCIMIENTO DE DEUDA",
                    "FALSIFICACION DE DESCANSOS MEDICOS",
                    "MALAS PRACTICAS EN SUS FUNCIONES",
                    "ACOSO Y/O HOSTIGAMIENTO LABORAL",
                    "LLEGAR EN ESTADO ETILICO Y/O ESTUPEFACIENTES",
                    "DESACATO DE AUTORIDAD",
                    "INVALIDEZ ABSOLUTA (PERMANENTE)"
                ]
            }
        ],
        primary_action_label: 'Generar',

        async primary_action(values){


            if(values.grado_1){
                frappe.throw("Seleccione una opción")
            }

            alertLoading(100,"Registrando Apertura de agencia...")

            setTimeout(()=>{
                frappe.hide_progress();
                frappe.msgprint('Se registró el perfil de pos con exito!')
            },2000)
        }
    });

    $(d.fields_dict.grado_1.input).click(function (){


        if(d.fields_dict.grado_1.last_value != "" && d.fields_dict.grado_1.last_value != undefined  ){
            $(d.fields_dict.grado_2.wrapper).hide();
            console.log(d.fields_dict.grado_1.last_value);
        }else{
            $(d.fields_dict.grado_2.wrapper).show();
            console.log(d.fields_dict.grado_2.last_value);
        }

    })

    $(d.fields_dict.grado_2.input).click(function (){


        if(d.fields_dict.grado_2.last_value != "" && d.fields_dict.grado_2.last_value != undefined  ){
            $(d.fields_dict.grado_1.wrapper).hide();
            console.log(d.fields_dict.grado_1.last_value);
        }else{
            $(d.fields_dict.grado_1.wrapper).show();
            console.log(d.fields_dict.grado_1.last_value);
        }

    })

    d.show();

}


frappe.ui.form.on('Solicitud de Renuncia Anticipada', {

    async termino_de_contrato(frm, cdt, cdn){

        if ( cur_frm.doc.termino_de_contrato == "TERMINO DE CONTRATO POR TRABAJADOR"){
            frm.set_value("grado_1", "")
            frm.set_value("grado_2", "")
        }

        if ( cur_frm.doc.termino_de_contrato == "TERMINO DE CONTRATO POR JEFE"){

            await modalToSelectedGrade( frm, cdt, cdn )
        }

    },
    async before_workflow_action(frm){
        if(cur_frm.selected_workflow_action == "Validar"){
            let fechaActual = moment().format("YYYY-MM-DD")
            if(fechaActual >= cur_frm.doc.fecha_de_renuncia){
                await automationRequest(frm)
            }
        }
    },
    async empleado(frm){
        await validateEmployee(frm)
    },
    async refresh(frm){
        if(frm.is_new()){
            $('[data-label="Guardar"]').hide();
            cur_frm.add_custom_button(__('<button type="button" class="btn btn-primary btn-sm" data-toggle="dropdown" aria-expanded="false"><span class="alt-underline">G</span>uardar</span></button>'), async function () {
                console.log(frm,"gaa")
                frappe.confirm(`¿Estás seguro que la fecha de renuncia será el día ${frm.doc.fecha_de_renuncia}? Recuerda que la fecha de renuncia es el último día en que laboral el trabajador. A partir de ese día ya no tendrá acceso a ningún sistema.`,
                    () => {
                        frm.save()
                        $('[data-label="Guardar"]').show()
                    }, () => {

                    })
            })
        }
    }

})