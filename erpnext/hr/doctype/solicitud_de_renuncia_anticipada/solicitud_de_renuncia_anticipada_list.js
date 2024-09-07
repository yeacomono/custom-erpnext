frappe.listview_settings['Solicitud de Renuncia Anticipada'] = {
    onload(listview) {
        listview.page.actions.find('[data-label="Validar"]').parent().parent().remove()

    }
}