from odoo import fields, models, api
import json

class Action(models.Model):
    _name = 'form_custom_actions.action'
    _description = 'Action to be executed after form submission'

    name = fields.Char()
    type = fields.Selection([('script', 'Script'), ('blog', 'Blog'), ('debug', 'Debug'), ('av', 'AV Kontaktdaten')], default='blog')

    script = fields.Text()
    blog = fields.Many2one('blog.blog')

    def partner_get_aussteller(self, partner_id):
        while partner_id.parent_id:
            print("-- -- --")
            print(partner_id)
            print(partner_id.name)
            print(partner_id.parent_id)
            print(partner_id.parent_id.type)
            partner_id = partner_id.parent_id

        av_child = self.env['res.partner'].search([
            ('parent_id', '=', partner_id.id),
            ('type', '=', 'av')
        ], limit=1)



        did_find_av = False

        if av_child:
            partner_id = av_child
            did_find_av = True

        print("-- -- --")
        print(partner_id)
        print(partner_id.name)
        print(partner_id.parent_id)
        print(partner_id.parent_id.type)

        return [partner_id, did_find_av]


    def execute(self, form_record):

        if self.type == 'script':
            self.execute_script(form_record)
        elif self.type == 'blog':
            self.execute_blog(form_record)
        elif self.type == 'debug':
            self.execute_debug(form_record)
        elif self.type == 'av':
            self.execute_av(form_record)
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



        if 'image' in form_data:
            # print("image found")
            list_uploads = form_data['image']
            # type(list_uploads)
            # print("list_uploads: " + str(list_uploads))
            first_upload = list_uploads[0]
            # type(first_upload)
            # print("first_upload: " + str(first_upload))
            first_upload_url = first_upload['url']
            # type(first_upload_url)
            # print("first_upload_url: " + first_upload_url)

            # remove protocol and domain
            first_upload_url = first_upload_url.replace('http://', '')
            first_upload_url = first_upload_url.replace('https://', '')
            first_upload_url = first_upload_url.split('/')[1:]
            first_upload_url = '/' + '/'.join(first_upload_url)

            req['cover_properties'] = json.dumps({
                'background-image': 'url(' + first_upload_url +')',
                'background_color_class': 'o_cc3 o_cc',
                'background_color_style': '',
                'opacity': 0.2,
                'resize_class': 'o_half_screen_height o_record_has_cover',
                'text_align_class': '',
            })

        author = self.partner_get_aussteller(form_record.res_partner_id)[0]
        req['author_id'] = author.id
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
        submission_data = json.loads(form_data.submission_data)
        print('== DEBUG ==')
        print(form_data)
        for key in submission_data:
            print(key + ': ' + str(submission_data[key]))
        print('== DEBUG END ==')

    def execute_av(self, form_record):
        submission_data = json.loads(form_record.submission_data)
        author_l = self.partner_get_aussteller(form_record.submission_partner_id)
        user_id = form_record.builder_id.user_id if form_record.builder_id.user_id else self.env.user

        author = author_l[0]
        did_find_av = author_l[1]

        print("===")
        print("===")
        print("===")
        print('did_find_av: ' + str(did_find_av))
        print(author)
        print(author.id)
        print(author.name)
        print("===")
        print("===")
        print("===")

        if not did_find_av:

            # Create AV
            av = self.env['res.partner'].create({
                'name': author.name,
                'type': 'av',
                'parent_id': author.id
            })

            author = av

        # Update AV data
        author.write({
            'name': submission_data['name'],
            'firma1': submission_data['firma1'],
            'firma2': submission_data['firma2'],
            'street': submission_data['street'],
            'street2': submission_data['street2'],
            'zip': submission_data['zip'],
            'city': submission_data['city'],
            'phone': submission_data['phone'],
            'email': submission_data['email'],
            'website': submission_data['website'],
        })

        # update parent
        author.parent_id.write({
            'firma1': submission_data['firma1'],
            'firma2': submission_data['firma2'],
            'website': submission_data['website'],
        })



        # notify user
        body_message = ''' 
Changed data due to AV Kontaktdaten action:
name: %s -> %s
firma1: %s -> %s
firma2: %s -> %s
street: %s -> %s
street2: %s -> %s
zip: %s -> %s
city: %s -> %s
phone: %s -> %s
email: %s -> %s
website: %s -> %s

@%s
        ''' % ( author.name, submission_data['name'],
                author.firma1, submission_data['firma1'],
                author.firma2, submission_data['firma2'],
                author.street, submission_data['street'],
                author.street2, submission_data['street2'],
                author.zip, submission_data['zip'],
                author.city, submission_data['city'],
                author.phone, submission_data['phone'],
                author.email, submission_data['email'],
                author.website, submission_data['website'],
                user_id.name
                )

        author.message_post(
            body=body_message,
            message_type='notification',
            subtype_id=self.env.ref('mail.mt_comment').id,
        )

















