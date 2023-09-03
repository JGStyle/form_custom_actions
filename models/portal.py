import json
import logging

from odoo import http, fields, models, api
from odoo.http import request

from odoo.addons.formio.controllers.portal import FormioCustomerPortal
from odoo.addons.portal.controllers.portal import CustomerPortal

from odoo.addons.formio.models.formio_builder import STATE_CURRENT as BUILDER_STATE_CURRENT

from odoo.addons.formio.models.formio_form import (
    STATE_DRAFT as FORM_STATE_DRAFT,
    STATE_COMPLETE as FORM_STATE_COMPLETE,
)

_logger = logging.getLogger(__name__)

# only show Form builders with the connected websites

class FormioCustomerPortalInherit(FormioCustomerPortal):

    def _formio_form_prepare_portal_layout_values(self, **kwargs):
        values = super(FormioCustomerPortalInherit, self)._formio_form_prepare_portal_layout_values(**kwargs)

        domain = [
            ('portal', '=', True),
            ('formio_res_model_id', '=', False),
            ('state', '=', BUILDER_STATE_CURRENT),
            '|', ('website_ids', '=', False), ('website_ids', 'in', request.website.id)
        ]

        builders_create_form = request.env['formio.builder'].search(domain)
        values['builders_create_form'] = builders_create_form

        return values

    @http.route(['/my/formio'], type='http', auth="user", website=True)
    def portal_forms(self, sortby=None, search=None, search_in='content',  **kwargs):
        domain = [
            ('user_id', '=', request.env.user.id),
            ('portal_share', '=', True),
            # '|', ('website_ids', '=', False), ('website_ids', 'in', request.website.id)
        ]
        res_model = kwargs.get('res_model')
        res_id = kwargs.get('res_id')
        if res_model and res_id:
            domain.append(('res_model', '=', res_model))
            domain.append(('res_id', '=', res_id))

        order = 'create_date DESC'
        forms = request.env['formio.form'].search(domain, order=order)

        values = self._formio_form_prepare_portal_layout_values(**kwargs)
        values['forms'] = forms
        return request.render("formio.portal_my_formio", values)
