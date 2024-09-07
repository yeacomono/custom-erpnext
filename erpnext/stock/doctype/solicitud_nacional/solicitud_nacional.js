// Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Solicitud Nacional', {
    refresh: function(frm) {
        $.each( frm.doc["table_7"] || [] , function(i, item) {
            if (item.solicitud_de_materiales) {
                cur_frm.get_field("table_7").grid.grid_rows[i].columns.solicitud_de_materiales.df.read_only = 1
            }
        })
    },
    before_save: function(frm) {
        $.each( frm.doc["table_7"] || [] , function(i, item) {
            if (item.solicitud_de_materiales) {
                cur_frm.get_field("table_7").grid.grid_rows[i].columns.solicitud_de_materiales.df.read_only = 1
            }
        })
    },
    refresh: function(frm) {
        frm.set_query("agencia", function(){
            return {
                filters : {
                    "estado_de_sucursal": ["=", 1]
                }
            };
        });
    },

});

frappe.ui.form.on('Tabla Solicitud Nacional', {
    cantidad: function (frm, cdt, cdn) {
        updateCantidadPendiente(frm, cdt, cdn);
    },
    cantidad_enviada: function (frm, cdt, cdn) {
        updateCantidadPendiente(frm, cdt, cdn);
    },
});

const updateCantidadPendiente = (frm, cdt, cdn) => {
    let item = locals[cdt][cdn];
    if ((item.cantidad != undefined && item.cantidad != null) && ( item.cantidad_enviada != undefined &&  item.cantidad_enviada != null)) {
        let result = calculateCantidadPendiente(item.cantidad, item.cantidad_enviada);
        if (!result.status) {
            item.cantidad_pendiente = result.data;
            item.cantidad_enviada = result.data;
            frm.refresh_field('table_7');
            frappe.throw(result.message);
        } else {
            item.cantidad_pendiente = result.data;
        }
        frm.refresh_field('table_7');
    }
}

const calculateCantidadPendiente = (qty, qty_enviada) => {
    if (qty_enviada > qty) {
        return {
            status: false,
            message: 'La cantidad enviada no puede ser mayor a la cantidad',
            data: 0
        }
    }
    return {
        status: true,
        message: 'Cantidad pendiente',
        data: qty - qty_enviada
    }
}
