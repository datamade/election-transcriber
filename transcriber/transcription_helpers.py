from flask_wtf import Form

from wtforms.fields import BooleanField, StringField

import sqlalchemy as sa

from transcriber.database import db
from transcriber.models import FormSection, FormField, FormMeta, \
    ImageTaskAssignment, DocumentCloudImage
from transcriber.dynamic_form import NullableIntegerField as IntegerField, \
    NullableDateTimeField as DateTimeField, \
    NullableDateField as DateField, validate_blank_not_legible

FORM_TYPE = {
    'boolean': BooleanField,
    'string': StringField,
    'integer': IntegerField,
    'datetime': DateTimeField,
    'date': DateField
}

class TranscriptionManager(object):
    
    def __init__(self, 
                 task_id, 
                 username=None,
                 image_id=None,
                 transcription_id=None):
        
        class DynamicForm(Form):
            pass
        
        self.task_id = task_id
        self.username = username
        self.dynamic_form = DynamicForm
        self.engine = db.session.bind
        self.old_transcription = {}
        self.bools = []
        self.image_task_assignment = None
        self.is_new = True
        self.image_id = image_id
        self.transcription_id = transcription_id

    def getFormMeta(self):
        # Get non-deleted sections
        section_sq = db.session.query(FormSection)\
                       .filter(sa.or_(FormSection.status != 'deleted', 
                                      FormSection.status == None))\
                       .order_by(FormSection.index)\
                       .subquery()

        # Join in non-deleted fields
        field_sq = db.session.query(FormField)\
                .filter(sa.or_(FormField.status != 'deleted', 
                               FormField.status == None))\
                .order_by(FormField.index)\
                .subquery()

        # Get all that stuff for a given task
        self.task = db.session.query(FormMeta)\
                      .join(section_sq)\
                      .join(field_sq)\
                      .filter(FormMeta.id == self.task_id)\
                      .first()
        
        if self.transcription_id:
            self.getOldTranscription()

        if self.username:
            
            q = ''' 
                SELECT COUNT(*) AS count 
                FROM "{0}" 
                WHERE transcriber = :username
                '''.format(self.task.table_name)
            
            user_transcriptions = self.engine.execute(sa.text(q), 
                                                      username=self.username).first().count
            
            self.user_transcriptions = user_transcriptions
    
    def getOldTranscription(self):
            q = ''' 
                    SELECT * FROM "{0}" WHERE id = :transcription_id
                '''.format(self.task.table_name)
            
            self.old_transcription = dict(self.engine.execute(sa.text(q), 
                                          transcription_id=self.transcription_id).first())
            self.is_new = False

    def setupDynamicForm(self):
        
        self.sections = []

        for section in sorted(self.task.sections, key=lambda x: x.index):
            section_dict = {'name': section.name, 'fields': []}
            
            for field in sorted(section.fields, key=lambda x: x.index):
                
                if field.data_type == 'boolean':
                    self.bools.append(field.slug)
                
                ft = FORM_TYPE[field.data_type]()
                setattr(self.dynamic_form, field.slug, ft)
                
                blank = '{0}_blank'.format(field.slug)
                not_legible = '{0}_not_legible'.format(field.slug)
                altered = '{0}_altered'.format(field.slug)
                
                setattr(self.dynamic_form, blank, BooleanField())
                setattr(self.dynamic_form, not_legible, BooleanField())
                setattr(self.dynamic_form, altered, BooleanField())
                
                self.bools.extend([blank, not_legible, altered])
                
                section_dict['fields'].append(field)
            
            self.sections.append(section_dict)
        
        # adding field for marking docs as irrelevant
        setattr(self.dynamic_form, 'flag_irrelevant', BooleanField())

        all_fields = set([f.slug for f in section_dict['fields']])
        for field in all_fields:
            setattr(self.dynamic_form, 'validate_{0}'.format(field), validate_blank_not_legible)
        
        self.form = self.dynamic_form(meta={})
    
    def prepopulateFields(self):
        meta_cols = ['transcriber', 'transcription_status', 'image_id', 'date_added', 'id']
        
        for k,v in self.old_transcription.items():
            
            if k and k not in meta_cols:
                self.form[k].data = v

    def getImageTaskAssignment(self):
        if self.image_id:
            self.image_task_assignment = db.session.query(ImageTaskAssignment)\
                                           .filter(ImageTaskAssignment.form_id == self.task_id)\
                                           .filter(ImageTaskAssignment.image_id == self.image_id)\
                                           .first()
        else:
            self.image_task_assignment = ImageTaskAssignment.get_next_image_to_transcribe(self.task_id, 
                                                                                          self.username)
        
        if self.image_task_assignment:
            self.image_id = self.image_task_assignment.image_id
            self.checkoutImage()
            self.dc_image = db.session.query(DocumentCloudImage).get(self.image_id)

    def validateTranscription(self, post_data):
        
        self.post_data = post_data
        
        self.form = self.dynamic_form(post_data)

        return self.form.validate()
    
    def saveFinal(self):
        
        min_agree = self.task.reviewer_count * 2 / 3 + 1
        
        task_table = sa.Table(self.task.table_name, 
                              sa.MetaData(), 
                              autoload=True, 
                              autoload_with=self.engine)

        final_transcription = {}
        
        for column in task_table.columns:
            
            column_name = str(column.name)
            if column_name not in ['date_added', 'transcriber', 'id', 'image_id']:
                
                count = self.engine.execute(sa.text('''
                    SELECT 
                      "{0}" AS column_value
                    FROM "{1}" 
                    WHERE image_id = :image_id 
                      AND transcription_status = 'raw' 
                    GROUP BY "{0}" 
                    HAVING (COUNT(*) > :min_agree)
                    ORDER BY COUNT(*) DESC
                    LIMIT 1
                    '''.format(column_name,
                               self.task.table_name)), 
                    image_id=self.image_id,
                    min_agree=min_agree).first()
                
                final_transcription[column_name] = None

                if count:
                    final_transcription[column_name] = count.column_value

        if not None in final_transcription.values():
            final_transcription['transcription_status'] = 'final'
            final_transcription['image_id'] = self.image_id
            self.insertTranscription(final_transcription)
    
    def saveTranscription(self):
        ins_args = {
            'transcriber': self.username,
            'image_id': self.image_id,
            'transcription_status': 'raw',
        }

        for k,v in self.post_data.items():
            
            if k != 'csrf_token':
                if v:
                    ins_args[k] = v
                else:
                    ins_args[k] = None
        
        if not set(self.bools).intersection(set(ins_args.keys())):
            for f in self.bools:
                ins_args[f] = False
        
        self.insertTranscription(ins_args)

    def insertTranscription(self, transcription):
        ins = ''' 
            INSERT INTO "{0}" ({1}) VALUES ({2})
            RETURNING id
        '''.format(self.task.table_name, 
                   ','.join(['"{}"'.format(f) for f in transcription.keys()]),
                   ','.join([':{}'.format(f) for f in transcription.keys()]))

        with self.engine.begin() as conn:
            self.transcription_id = conn.execute(sa.text(ins), **transcription)
    
    def updateImage(self):
        
        update_image = '''
            UPDATE image_task_assignment SET
              view_count = (view_count + 1)
        '''

        if self.image_task_assignment.view_count >= self.task.reviewer_count:

            self.saveFinal()
            
            update_image = '{}, is_complete = TRUE'.format(update_image)
        
        update_image = '{} WHERE image_id = :image_id'.format(update_image)
        
        with self.engine.begin() as conn:
            conn.execute(sa.text(update_image), image_id=self.image_id)
    
    def deleteOldTranscription(self):
        
        update_status = ''' 
            UPDATE "{0}" SET 
              transcription_status = 'raw_deleted'
            WHERE id = :transcription_id
            RETURNING image_id
        '''.format(self.task.table_name)
        
        with self.engine.begin() as conn:
            image_id = conn.execute(sa.text(update_status), 
                             transcription_id=self.transcription_id).first().image_id
        
        update_task_assignment = ''' 
            UPDATE image_task_assignment SET
              view_count = view_count.count,
              is_complete = FALSE
            FROM (
              SELECT COUNT(*) AS count
              FROM "{0}"
              WHERE image_id = :image_id
                AND transcription_status = 'raw'
            ) AS view_count
            WHERE form_id = :task_id
              AND image_id = :image_id
        '''.format(self.task.table_name)
        
        with self.engine.begin() as conn:
            conn.execute(sa.text(update_task_assignment), 
                         image_id=self.image_id, 
                         task_id=self.task.id)
        return image_id
    
    def checkoutImage(self):
        checkout = ''' 
            UPDATE image_task_assignment SET
              checkout_expire = NOW() + INTERVAL '5 minutes'
            WHERE image_id = :image_id
        '''

        with self.engine.begin() as conn:
            conn.execute(sa.text(checkout), 
                         image_id=self.image_id)
    
    def isTaskIncomplete(self):
        incomplete_count = ''' 
            SELECT COUNT(*) AS count
            FROM image_task_assignment
            WHERE form_id = :task_id
              AND is_complete = FALSE
        '''

        incomplete_count = self.engine.execute(sa.text(incomplete_count), 
                                               task_id=self.task_id).first().count
        
        return incomplete_count > 0

def checkinImages():
    
    update = ''' 
        UPDATE image_task_assignment SET
          checkout_expire = NULL
        WHERE checkout_expire < NOW()
    '''
    
    engine = db.session.bind

    with engine.begin() as conn:
        conn.execute(update)
