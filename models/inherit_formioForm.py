from odoo import fields, models, api


class Form(models.Model):
    _inherit = 'formio.form'

    # related website_ids from builder
    website_ids = fields.Many2many('website', related='builder_id.website_ids', string='connected Websites')


    def after_submit(self):
        """ Function is called everytime a form is submitted. """

        for record in self:
            for action in record.builder_id.action_ids:
                action.execute(record)
