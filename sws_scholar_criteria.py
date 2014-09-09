from osv import osv
from osv import fields

class SWS_Scholar_Criteria(osv.osv):
 
    _name = 'sws.scholar.criteria'
    _description = 'sws.scholar.criteria'
 
    _columns = {
            'name':fields.char('Criteria Name:', required=False),
            'criteria_no':fields.integer('Criteria Number:', required=False), 
            'active_is':fields.boolean('Active',required=False),
            'date_valid':fields.date('Date valid From',required=False),
            'criteria_line_id':fields.one2many('sws.scholar.criteria.line','criteria1_id'),  
            
                }
SWS_Scholar_Criteria()

class SWS_Scholar_Criteria_line(osv.osv):
 
    _name = 'sws.scholar.criteria.line'
    _description = 'sws.scholar.criteria.line'
 
    _columns = {
            'category_course':fields.many2one('sws.scholar.criteria.course','Course', required=True), 
            'min_annual_income':fields.integer('Maximum Annual Income',required=False),
            'scholar_allowed':fields.boolean('Scholarship Allowed Course',required=False),
            'criteria1_id':fields.many2one('sws.scholar.criteria','Category', required=False),   
            
                }
SWS_Scholar_Criteria_line()

class SWS_Scholar_Cource(osv.osv):
 
    _name = 'sws.scholar.criteria.course'
    _description = 'sws.scholar.criteria.course'
 
    _columns = {
                'name':fields.char('Course Name',required=True),
                'allowed':fields.boolean('Allowed Course'),
                'course_id':fields.one2many('sws.category.education','course_name'),
                
                }
    
SWS_Scholar_Cource()

class SWS_Scholar_Qualification(osv.osv):
 
    _name = 'sws.scholar.criteria.qualification'
    _description = 'sws.scholar.criteria.qualification'
 
    _columns = {
                'name':fields.char('Qualification Name',required=True),
                'allowed':fields.boolean('Allowed Qualification'),
                'qualification_id':fields.one2many('sws.category.education','qualification'),
                }
    
SWS_Scholar_Qualification()