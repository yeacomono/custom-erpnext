frappe.listview_settings['Liquidaciones Anual'] = {
    onload: function(listview) {

        listview.page.add_menu_item(__("Generar TXT"), function() {
            let d = new frappe.ui.Dialog({
                title: 'Generar TXT',
                fields: [
                    {
                        fieldtype : "Link",
                        options : "Company",
                        label	: "Compañia",
                        fieldname : "company",
                        reqd: 1
                    },
                    {
                        label: 'Tipo de Banco',
                        fieldname: 'banco',
                        fieldtype: 'Select',
                        options:["BCP","BBVA"],
                        reqd: 1
                    },
                ],
                primary_action_label: 'Generar',
                async primary_action(values) {
                    d.hide();

                    const get_data = await frappe.db.get_list('Liquidaciones Anual',{
                        'filters':[
                            ['pay_state','=','No Pagado'],
                            ['workflow_state','=','Validado'],
                            ['company','=',values.company]
                        ],
                        'limit':'None',
                        'fields': ['name','employee']
                    });

                    if (!get_data.length) {
                        frappe.throw("No hay documentos para generar TXT");
                        return false;
                    }

                    let array_employee = [];

                    for (let document of get_data) {
                        array_employee.push(document.employee)
                    }

                    frappe.require('assets/erpnext/js/fil_saver.js', async () => {
                        const service = await $.ajax({
                            "type": "post",
                            "url": frappe.boot.DOMINIOS.QA.RRHH_OUT + "/api/get-txt-salary-slip-bcp-interbank-3",
                            "data": {
                                "service": 'liquidaciones',
                                "employees": array_employee,
                                "company": values.company,
                                "banco": values.banco
                            }
                        })

                        console.log(service,'service')

                        if(service.valor){
                            let message = service.txt_header+"\n"+service.txt_lines
                            let opcionesBlob = values.banco === "BCP" ? {type: "text/plain",endings: "native"} : {type: "text/plain"};
                            let blob = new Blob([message], opcionesBlob);
                            saveAs(blob, "LIQUIDACION"+service.fecha);

                        } else {
                            frappe.throw(service.msn);
                            return false;
                        }

                    })

                }
            });

            d.show();
        })

    }
};
