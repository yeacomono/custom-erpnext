// Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

// var socket = io.connect("https://server.larael.com:3800",{'forceNew':true});

var socket = io.connect("https://sms.shalom.com.pe:6500",{'forceNew':true});


frappe.ui.form.on('Soporte Sistemas', {
    refresh: async function(frm) {

        /* EVENTO CUANDO GUARDAN COMENTARIO CON ATAJO */
        document.addEventListener('keydown', function(e) {
            if (e.ctrlKey && e.key === 'Enter') {
                let fun_change_status_for_comment = frm.events.change_status_for_comment(frm)
            }
        });
        /* EVENTO CUANDO GUARDAN COMENTARIO CON EL BOTON */
        $('.btn-comment').click(function() {
            let fun_change_status_for_comment = frm.events.change_status_for_comment(frm)
        });
    },
    change_status_for_comment: async function (frm) {
        if (in_list(["Pendiente de Información"],frm.doc.estado) && (frappe.user.name.includes("@shalomcontrol.com") || frappe.user.name.includes("@shalom.com.pe"))) {
            const update_status_doc = await frappe.db.set_value('Soporte Sistemas', frm.doc.name, {
                'estado': 'Revisando'
            })
            frm.reload_doc()
        }
    }
});
