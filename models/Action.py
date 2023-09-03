from odoo import fields, models, api
import json

class Action(models.Model):
    _name = 'form_custom_actions.action'
    _description = 'Action to be executed after form submission'

    name = fields.Char()
    type = fields.Selection([('script', 'Script'), ('blog', 'Blog'), ('debug', 'Debug')], default='blog')

    script = fields.Text()
    blog = fields.Many2one('blog.blog')


    def execute(self, form_record):

        if self.type == 'script':
            self.execute_script(form_record)
        elif self.type == 'blog':
            self.execute_blog(form_record)
        elif self.type == 'debug':
            self.execute_debug(form_record)
        else:
            raise Exception('Unknown action type: ' + self.type)


    def execute_script(self, form_record):
        pass

    def execute_blog(self, form_record):

        form_data = json.loads(form_record.submission_data)

        attrs = ['name', 'content', 'subtitle']
        req = {}
        for attr in attrs:
            if not attr in form_data:
                raise Exception('Attribute ' + attr + ' not found in form data')
            req[attr] = form_data[attr]

        req['author_id'] = form_record.res_partner_id.id
        req['blog_id'] = self.blog.id
        req['is_published'] = False


        new_blog_post = self.env['blog.post'].create(req)

        body_message = '''A new blog post has been created. 
            <a href="#" data-oe-model="blog.post" data-oe-id="%d">Click here</a> to review.''' % new_blog_post.id

        # Notify the user
        new_blog_post.message_post(
            body=body_message,
            message_type='notification',
            subtype_id=self.env.ref('mail.mt_comment').id,
            partner_ids=[form_record.builder_id.user_id.partner_id.id]
        )

        self.env['mail.activity'].create({
            'res_id': new_blog_post.id,
            'res_model_id': self.env['ir.model']._get('blog.post').id,
            'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
            'user_id': form_record.builder_id.user_id.id if form_record.builder_id.user_id.id else self.env.user.id,
            'note': body_message,
        })

    def execute_debug(self, form_data):
        print('== DEBUG ==')
        print(form_data)
        print(form_data.name)
        print(form_data.content)
        print(form_data.author_id)
        print(self.blog.id)
        print('== DEBUG END ==')