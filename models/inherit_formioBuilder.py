from odoo import fields, models, api


class Form(models.Model):
    _inherit = 'formio.builder'

    # connected actions
    action_ids = fields.Many2many('form_custom_actions.action', string='Actions')

    # responsible user
    user_id = fields.Many2one('res.users', string='Responsible', default=lambda self: self.env.user)

    # connected websites
    website_ids = fields.Many2many('website', string='connected Websites')
