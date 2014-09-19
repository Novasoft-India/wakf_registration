from osv import osv
from osv import fields
from datetime import datetime
from datetime import date,timedelta
from dateutil.relativedelta import relativedelta
from tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare
import time
from tools.translate import _


class sws_registration(osv.osv):
 
    _name = 'sws.registration'
    _description = 'sws.registration'
    
    def action_scheduler(self, cr, uid, automatic=False, use_new_cursor=False, context=None):
        invoice_ids = []
        for rec in self.pool.get('res.partner').browse(cr,uid,[]):
            id_rec = rec.id
            self.pool.get('res.partner').update(cr,uid,id_rec,{'state1':'re_payment'})
        return True
 
    _columns = {
            'appli_no':fields.char('Application Number:', size=64, required=True),
            'category': fields.selection([
                ('pension', 'Pension'),
                ('education', 'Education'),
                ('orphans', 'Orphans'),
                ('firms', 'Firms'),
                ('widow', 'Widow'),
                ('marriage', 'Marriage'),
                ('disease', 'Disease'),
                ('maintenance', 'Maintenance'),
                ('handicapped', 'Handicapped'),
                ('destitute', 'Destitute'),
                ], 'Category', readonly=False),
            'appli_date':fields.date('Application Date:', size=64, required=True),
            'full_name':fields.char('Full Name:', size=64, required=True),
            'address':fields.text('Address:', size=64, required=True),
            'comm_address':fields.text('Communication Address:', size=64, required=False),
            'tick_same':fields.boolean('Tick, if same as above', required=False),
            'village':fields.char('Village:', size=64, required=True),
            'panchayath':fields.char('Pan/Mun/Corp:', size=64, required=True),
            'taluk_id':fields.many2one('wakf.taluk','Taluk',ondelete='set null'),
            'district_id':fields.many2one('wakf.district','District',ondelete='set null',required=True),
            'reg_no':fields.integer('Wakf Reg No', size=8,required=True),
            'wakf_id':fields.many2one('res.partner','Wakf Name',ondelete='set null',required=True),
            'sws_pension_id':fields.one2many('sws.category.pension','sws_id','Pension Details'),
            'sws_education_id':fields.one2many('sws.category.education','sws_id','Educetion Details'),
            'sws_orphans_id':fields.one2many('sws.category.orphans','sws_id','Orphans Details'),
            'sws_firms_id':fields.one2many('sws.category.firms','sws_id','Firms Details'),
            'sws_widow_id':fields.one2many('sws.category.widow','sws_id','Widow Details'),
            'sws_marriage_id':fields.one2many('sws.category.marriage','sws_id','Marriage Details'),
            'sws_disease_id':fields.one2many('sws.category.disease','sws_id','Disease Details'),
            'sws_maintenance_id':fields.one2many('sws.category.maintenance','sws_id','Maintenance Details'),
            'sws_handicapped_id':fields.one2many('sws.category.handicaped','sws_id','Handicapped Details'),
            'sws_destitute_id':fields.one2many('sws.category.destitute','sws_id','Destitute Details'),
            'user_id':fields.char('user')
                    }
    _defaults={
        'user_id': lambda obj, cr, uid, context: uid,
     }
sws_registration()

class sws_category_pension(osv.osv):
 
    _name = 'sws.category.pension'
    _description = 'sws.category.pension'
    
    def on_change_wakf_regno_to_name(self, cr, uid, ids, reg_no, context=None):
        values = {}
        if reg_no:
            id_res_partner=self.pool.get('res.partner')
            search_condition = [('wakf_reg_no', '=', reg_no)]
            search_ids = id_res_partner.search(cr, uid, search_condition, context=context)
            similar_objs = id_res_partner.browse(cr, uid, search_ids, context=context)[0]
            if similar_objs:
                values={'partner_id':similar_objs.id,
                        }
        return {'value' :values}
    
    def on_change_DOB(self, cr, uid, ids,dob, context=None):
        age = False
        month = False
        days = False
        if dob:
            dt = datetime.strptime(dob,"%Y-%m-%d")
            r = relativedelta(datetime.now(), dt)
            age = r.years
            month = (r.years * 12 + r.months + r.days/30) - age*12
            day = r.days % 30
            #day = (r.years * 365 + r.months * 30 + r.days)-(r.years * 365 + r.months * 30)
        if age >= 0 and month >= 0 and day >= 0:
            return {'value':{'age':age,
                           'month':month,
                           'days':day,
                           }}
    def exp_year(self, cr, uid, ids,fields,arg, context=None):
        criteria_id = self.pool.get('sws.criteria')
        a = []
        exp_year = 0
        exp_month = 0
        exp_days = 0
        total_month = 0
        total_days = 0
        min_exp = 0
        min_work_gap = 0
        total_month_list = []
        total_days_list = []
        month_list = []
        day_list = []
        dicti = {}
        search_condition = [('name','in',["Graduate Arabic Teacher/Mudris","Khadim,attendar,Cleaner,Imams helper","Teachers/Imam"])]
        search_ids = self.pool.get('product.product').search(cr,uid,search_condition, context=context)
        if search_ids:
            category = self.pool.get('product.product').browse(cr,uid,search_ids)[0].id
            for rec in self.browse(cr, uid, ids, context=context):
                dicti[rec.id]={
                    'in_year': 0.0,
                    'in_month': 0.0,
                    'in_day': 0.0,
                    
                               }
                search_condition = [('active_is','=',True),]
                search_ids = criteria_id.search(cr,uid,search_condition, context=context)
                if search_ids: # active criteria
                    criteria_active = criteria_id.browse(cr, uid, search_ids, context=context)[0]
                    for items in criteria_active.criteria_line_id: # fetch from one2many list
                        if items.category.id == category:
                            lower_age = items.lower_age 
                            higher_income = items.higher_income
                            min_exp = items.min_exp or 0.0
                            min_work_gap = items.min_work_gap or 0.0
                    if min_exp and min_work_gap:
                        for point in rec.exp_line_id:
                            a.append(point.experience_from)
                            a.append(point.experience_to)
                        for values in range(len(a)-1):
                            if a[values] < a[values+1]:
                                dt_from = datetime.strptime(a[values],"%Y-%m-%d")
                                dt_to = datetime.strptime(a[values+1],"%Y-%m-%d")
                                r = relativedelta(dt_to, dt_from)
                                month_list.append(int(r.years * 12 + r.months + r.days/30))
                                day_list.append(int(r.days))
                        for index in range(len(month_list)):
                            if index % 2 == 1:  # Getting odd events
                                if month_list[index] <= min_work_gap:  # Getting Gap in Experience
                                    if index == 1:
                                        total_month = total_month + month_list[index-1] + month_list[index+1]
                                        total_days = total_days + day_list[index-1] + day_list[index+1]
                                    else:
                                        if month_list[index-2] <= min_work_gap:
                                            total_month = total_month + month_list[index+1]
                                            total_days = total_days + day_list[index+1]
                                        else:
                                            total_month = total_month + month_list[index+1]
                                            total_days = total_days + day_list[index+1]
                                            total_month = total_month + month_list[index-1]
                                            total_days = total_days + day_list[index-1]
                                            
                                else:  # Gap greater than 6 months
                                    if len(month_list) <= 3:
                                        total_month_list.append(month_list[0])
                                        total_days_list.append(day_list[0])
                                        total_month_list.append(month_list[2])
                                        total_days_list.append(day_list[2])
                                    else:
                                        total_month_list.append(total_month)
                                        total_days_list.append(total_days)
                                        if len(month_list) > 3:
                                            total_month = 0
                                            total_days = 0
                                    if index == len(month_list)-2:
                                        if len(month_list) > 3:
                                            if month_list[len(month_list)-2] <= min_work_gap:
                                                total_month = total_month + month_list[-1]
                                                total_days = total_days + day_list[-1]
                                            else:
                                                total_month_list.append(month_list[-1])
                                                total_days_list.append(day_list[-1])
                        if len(month_list) == 1:
                            total_month_list.append(month_list[0])
                            total_days_list.append(day_list[0])
                        total_month_list.append(total_month)
                        total_days_list.append(total_days)
                        final_month = max(total_month_list)
                        final_days = max(total_days_list)
                        exp_year = final_month/12
                        exp_month = final_month - exp_year * 12
                        exp_days = final_days
                #self.write(cr, uid, ids, {'in_year':exp_year,'in_month':exp_month,'in_day':exp_days})
                    dicti[rec.id]['in_year'] = exp_year
                    dicti[rec.id]['in_month'] = exp_month
                    dicti[rec.id]['in_day'] = exp_days
                    return dicti
                else:
                    return {'warning': {
                    'title': _('Warning!'),
                    'message':  _('Please set/check criteria for this category'),                 
                    }} 
                          
                
            
        else:
            return {'warning': {
                    'title': _('Warning!'),
                    'message':  _('Selected category not available'),                 
                    }}
        
 
    _columns = {
            'date_of_birth':fields.date('Date of Birth:', required=False),
            'age':fields.float('Age:', size=8, readonly=True),
            'month':fields.float('Month:', size=8, readonly=True),
            'days':fields.float('Days:', size=8, readonly=True),
            'qualification':fields.char('Qualification:',size=64, required=False),
            'job_details':fields.char('Job Details:',size=64, required=False),
            'job_income':fields.float('Present Job Income:',size=16, required=False),
            'other_income':fields.char('Other Income:',size=64, required=False),
            'total_annual_income':fields.float('Total Annual Income:', required=False),
            'experience_from':fields.date('Experience From:', required=False),
            'experience_to':fields.date('Experience To:', required=False),
            #'experience_total':fields.char('Total Experience:', required=False),
            'in_year':fields.function(exp_year,string='Exp. Year(s)',store=True,type='float',method=False,multi='all'),
            'in_month':fields.function(exp_year,string='Exp. Month(s)',store=True,type='float',method=False,multi='all'), 
            'in_day':fields.function(exp_year,string='Exp. Day(s)',store=True,type='float',method=False,multi='all'),
            'mahal_details':fields.text('Mahal Details:',size=256, required=True),
            'body_marks':fields.text('Body Marks:', required=False),
            'benefits':fields.text('Existing Wakf Benefits:',size=256, required=False),
            'sws_id':fields.many2one('sws.registration','PENSION',ondelete='set null'),
            'sws_id1':fields.many2one('res.partner','PENSION',ondelete='set null'),
            'exp_line_id':fields.one2many('sws.category.pension.line','line_id')
                }
                
sws_category_pension()

class sws_category_pension_line(osv.osv):
 
    _name = 'sws.category.pension.line'
    _description = 'sws.category.pension.line'
    
    def on_change_Work_Exp_from(self, cr, uid, ids,date_from,date_to, context=None):
        age = False
        month = False
        days = False
        if date_from and date_to:
            dt_from = datetime.strptime(date_from,"%Y-%m-%d")
            dt_to = datetime.strptime(date_to,"%Y-%m-%d")
            r = relativedelta(dt_to, dt_from)
            age = r.years
            month = (r.years * 12 + r.months + r.days/30) - age*12
            day = r.days % 30
            #day = (r.years * 365 + r.months * 30 + r.days)-(r.years * 365 + r.months * 30)
        if age >= 0 and month >= 0 and day >= 0:
            return {'value':{'total_year':age,
                           'total_month':month,
                           'total_days':day,
                           }}
    def on_change_wakf_regno_to_name(self, cr, uid, ids, reg_no, context=None):
        values = {}
        if reg_no:
            id_res_partner=self.pool.get('res.partner')
            search_condition = [('wakf_reg_no', '=', reg_no)]
            search_ids = id_res_partner.search(cr, uid, search_condition, context=context)
            if search_ids:
                similar_objs = id_res_partner.browse(cr, uid, search_ids, context=context)[0]
                values={'partner_id':similar_objs.id,
                            }
                return {'value' :values}
        return False
    
    _columns={
              'line_id':fields.many2one('sws.category.pension','PENSION line',ondelete='set null'),
              'partner_id':fields.many2one('res.partner','Wakf Name',domain=[('customer','=',True)],ondelete='set null',required=True),
              'reg_no':fields.integer('Register No:', required=True),
              'experience_from':fields.date('Experience From:', required=True),
              'experience_to':fields.date('Experience To:', required=True),
              'total_year':fields.integer('Total Year:', readonly=True),
              'total_month':fields.integer('Total Month:', readonly=True),
              'total_days':fields.integer('Total Days:', readonly=True),
              }
sws_category_pension_line()  

class sws_category_education(osv.osv):
 
    _name = 'sws.category.education'
    _description = 'sws.category.education'
    
    def on_change_DOB(self, cr, uid, ids,dob, context=None):
        age = False
        month = False
        days = False
        if dob:
            dt = datetime.strptime(dob,"%Y-%m-%d")
            r = relativedelta(datetime.now(), dt)
            age = r.years
            month = (r.years * 12 + r.months + r.days/30) - age*12
            day = r.days % 30
            #day = (r.years * 365 + r.months * 30 + r.days)-(r.years * 365 + r.months * 30)
        if age >= 0 and month >= 0 and day >= 0:
            return {'value':{'age':age,
                           }}
 
    _columns = {
            'course_name':fields.many2one('sws.scholar.criteria.course','Course Name',domain=[('allowed','=',True)],required=True),
            'qualification':fields.many2one('sws.scholar.criteria.qualification','Qualification',domain=[('allowed','=',True)],required=True),
            'qualifying_mark':fields.integer('Qualifying Mark :',size=64, required=False),
            'qualifying_percentage':fields.float('Qualifying % :',size=64, required=False),
            'date_of_birth':fields.date('Date of Birth:', required=False),
            'age':fields.integer('Age:', size=8, readonly=True),
            'total_annual_income':fields.float('Total Annual Income:', required=False),
            'institution_name':fields.text('Institution Name:',size=64, required=False),
            'institution_addr':fields.text('Institution Address:',size=128, required=False),
            'sws_id':fields.many2one('sws.registration','PENSION',ondelete='set null'),
            'sws_id1':fields.many2one('res.partner','PENSION2',ondelete='set null'),
                }
sws_category_education()

class sws_category_orphans(osv.osv):
 
    _name = 'sws.category.orphans'
    _description = 'sws.category.orphans'
    
    def on_change_DOB(self, cr, uid, ids,dob, context=None):
        age = False
        month = False
        days = False
        if dob:
            dt = datetime.strptime(dob,"%Y-%m-%d")
            r = relativedelta(datetime.now(), dt)
            age = r.years
            month = (r.years * 12 + r.months + r.days/30) - age*12
            day = r.days % 30
            #day = (r.years * 365 + r.months * 30 + r.days)-(r.years * 365 + r.months * 30)
        if age >= 0 and month >= 0 and day >= 0:
            return {'value':{'age':age,
                           'month':month,
                           'days':day,
                           }}
 
    _columns = {
            'job_name':fields.char('Job Name:',size=64, required=False),
            'income':fields.float('Income:', required=False),
            'other_income':fields.float('Other Income:', required=False),
            'total_income':fields.float('Annual Income:', required=False),
            'date_of_birth':fields.date('Date of Birth:', required=False),
            'age':fields.integer('Age:', size=8, readonly=True),
            'month':fields.integer('Month:', size=8, readonly=True),
            'days':fields.integer('Days:', size=8, readonly=True),
            'ben_wakf':fields.text('Ben: Wakf Board:',size=256, required=False),
            'check_required':fields.boolean('Date checking not Required:', required=False),
            'sws_id':fields.many2one('sws.registration','PENSION',ondelete='set null'),
            'sws_id1':fields.many2one('res.partner','PENSION3',ondelete='set null'),
                }
sws_category_orphans()

class sws_category_firms(osv.osv):
 
    _name = 'sws.category.firms'
    _description = 'sws.category.firms'
    
    def on_change_wakf_regno_to_name(self, cr, uid, ids, reg_no, context=None):
        values = {}
        if reg_no:
            id_res_partner=self.pool.get('res.partner')
            search_condition = [('wakf_reg_no', '=', reg_no)]
            search_ids = id_res_partner.search(cr, uid, search_condition, context=context)
            similar_objs = id_res_partner.browse(cr, uid, search_ids, context=context)[0]
            if similar_objs:
                values={'partner_id':similar_objs.id,
                        }
        return {'value' :values}
 
    _columns = {
            'wakf_name':fields.many2one('res.partner','Wakf Name',size=64, required=True),
            'reg_no':fields.integer('Wakf Register No', required=True),
            'name_firm':fields.char('Name of the Firm:', required=True),
            'designation':fields.char('Official Designation:', required=False),
            'financial_status':fields.text('Financial Status:',size=128, required=False),
            'objectives':fields.text('Objective of the firm:',size=256, required=False),
            'objectives_fund':fields.text('Objective of fund:',size=256, required=False),
            'sws_id':fields.many2one('sws.registration','PENSION',ondelete='set null'),
            'sws_id1':fields.many2one('res.partner','PENSION4',ondelete='set null'),
                }
sws_category_firms()

class sws_category_widow(osv.osv):
 
    _name = 'sws.category.widow'
    _description = 'sws.category.widow'
    
    def on_change_DOB(self, cr, uid, ids,dob, context=None):
        age = False
        month = False
        days = False
        if dob:
            dt = datetime.strptime(dob,"%Y-%m-%d")
            r = relativedelta(datetime.now(), dt)
            age = r.years
            month = (r.years * 12 + r.months + r.days/30) - age*12
            day = r.days % 30
            #day = (r.years * 365 + r.months * 30 + r.days)-(r.years * 365 + r.months * 30)
        if age >= 0 and month >= 0 and day >= 0:
            return {'value':{'age':age,
                           'month':month,
                           'days':day,
                           }}
 
    _columns = {
            'job_name':fields.char('Job:',size=64, required=False),
            'income':fields.float('Income:', required=False),
            'other_income':fields.float('Other Income:', required=False),
            'total_income':fields.float('Annual Income:', required=False),
            'date_of_birth':fields.date('Date of Birth:', required=False),
            'age':fields.integer('Age:', size=8, readonly=True),
            'month':fields.integer('Month:', size=8, readonly=True),
            'days':fields.integer('Days:', size=8, readonly=True),
            'ben_wakf':fields.text('Ben: Wakf Board:',size=256, required=False),
            'check_required':fields.boolean('Date checking not Required:', required=False),
            'sws_id':fields.many2one('sws.registration','PENSION',ondelete='set null'),
            'sws_id1':fields.many2one('res.partner','PENSION5',ondelete='set null'),
                }
sws_category_widow()

class sws_category_marriage(osv.osv):
 
    _name = 'sws.category.marriage'
    _description = 'sws.category.marriage'
    
    def on_change_DOB(self, cr, uid, ids,dob, context=None):
        age = False
        month = False
        days = False
        if dob:
            dt = datetime.strptime(dob,"%Y-%m-%d")
            r = relativedelta(datetime.now(), dt)
            age = r.years
            month = (r.years * 12 + r.months + r.days/30) - age*12
            day = r.days % 30
            #day = (r.years * 365 + r.months * 30 + r.days)-(r.years * 365 + r.months * 30)
        if age >= 0 and month >= 0 and day >= 0:
            return {'value':{'age':age,
                           'month':month,
                           'days':day,
                           }}
 
    _columns = {
            'job_name':fields.char('Job:',size=64, required=False),
            'income':fields.float('Income:', required=False),
            'other_income':fields.float('Other Income:', required=False),
            'total_income':fields.float('Annual Income:', required=False),
            'date_of_birth':fields.date('Date of Birth:', required=False),
            'age':fields.integer('Age:', size=8, readonly=True),
            'month':fields.integer('Month:', size=8, readonly=True),
            'days':fields.integer('Days:', size=8, readonly=True),
            'ben_wakf':fields.text('Ben: Wakf Board:',size=256, required=False),
            'check_required':fields.boolean('Date checking not Required:', required=False),
            'date_marriage':fields.date('Marriage Date:', required=True),
            'guardian_name':fields.char('Guardian Name:',size=128, required=False),
            'sws_id':fields.many2one('sws.registration','PENSION',ondelete='set null'),
            'sws_id1':fields.many2one('res.partner','PENSION6',ondelete='set null'),
                }
sws_category_marriage()

class sws_category_disease(osv.osv):
 
    _name = 'sws.category.disease'
    _description = 'sws.category.disease'
    
    def on_change_DOB(self, cr, uid, ids,dob, context=None):
        age = False
        month = False
        days = False
        if dob:
            dt = datetime.strptime(dob,"%Y-%m-%d")
            r = relativedelta(datetime.now(), dt)
            age = r.years
            month = (r.years * 12 + r.months + r.days/30) - age*12
            day = r.days % 30
            #day = (r.years * 365 + r.months * 30 + r.days)-(r.years * 365 + r.months * 30)
        if age >= 0 and month >= 0 and day >= 0:
            return {'value':{'age':age,
                           'month':month,
                           'days':day,
                           }}
 
    _columns = {
            'job_name':fields.char('Job:',size=64, required=False),
            'income':fields.float('Income:', required=False),
            'other_income':fields.float('Other Income:', required=False),
            'total_income':fields.float('Annual Income:', required=False),
            'date_of_birth':fields.date('Date of Birth:', required=False),
            'age':fields.integer('Age:', size=8, readonly=True),
            'month':fields.integer('Month:', size=8, readonly=True),
            'days':fields.integer('Days:', size=8, readonly=True),
            'ben_wakf':fields.text('Ben: Wakf Board:',size=64, required=False),
            'check_required':fields.boolean('Date checking not Required:', required=False),
            'disease':fields.text('Disease:', size=256,required=False),
            'guardian_name':fields.char('Guardian Name:',size=64, required=False),
            'sws_id':fields.many2one('sws.registration','PENSION',ondelete='set null'),
            'sws_id1':fields.many2one('res.partner','PENSION7',ondelete='set null'),
                }
sws_category_disease()

class sws_category_maintenance(osv.osv):
 
    _name = 'sws.category.maintenance'
    _description = 'sws.category.maintenance'
    
    def on_change_DOB(self, cr, uid, ids,dob, context=None):
        age = False
        month = False
        days = False
        if dob:
            dt = datetime.strptime(dob,"%Y-%m-%d")
            r = relativedelta(datetime.now(), dt)
            age = r.years
            month = (r.years * 12 + r.months + r.days/30) - age*12
            day = r.days % 30
            #day = (r.years * 365 + r.months * 30 + r.days)-(r.years * 365 + r.months * 30)
        if age >= 0 and month >= 0 and day >= 0:
            return {'value':{'age':age,
                           'month':month,
                           'days':day,
                           }}
 
    _columns = {
            'job_name':fields.char('Job:',size=64, required=False),
            'income':fields.float('Income:', required=False),
            'other_income':fields.float('Other Income:', required=False),
            'total_income':fields.float('Annual Income:', required=False),
            'date_of_birth':fields.date('Date of Birth:', required=False),
            'age':fields.integer('Age:', size=8, readonly=True),
            'month':fields.integer('Month:', size=8, readonly=True),
            'days':fields.integer('Days:', size=8, readonly=True),
            'ben_wakf':fields.text('Ben: Wakf Board:',size=64, required=False),
            'check_required':fields.boolean('Date checking not Required:', required=False),
            'sws_id':fields.many2one('sws.registration','PENSION',ondelete='set null'),
            'sws_id1':fields.many2one('res.partner','PENSION9',ondelete='set null'),
                }
sws_category_maintenance()

class sws_category_handicaped(osv.osv):
 
    _name = 'sws.category.handicaped'
    _description = 'sws.category.handicaped'
    
    def on_change_DOB(self, cr, uid, ids,dob, context=None):
        age = False
        month = False
        days = False
        if dob:
            dt = datetime.strptime(dob,"%Y-%m-%d")
            r = relativedelta(datetime.now(), dt)
            age = r.years
            month = (r.years * 12 + r.months + r.days/30) - age*12
            day = r.days % 30
            #day = (r.years * 365 + r.months * 30 + r.days)-(r.years * 365 + r.months * 30)
        if age >= 0 and month >= 0 and day >= 0:
            return {'value':{'age':age,
                           'month':month,
                           'days':day,
                           }}
 
    _columns = {
            'job_name':fields.char('Job:',size=64, required=False),
            'income':fields.float('Income:', required=False),
            'other_income':fields.float('Other Income:', required=False),
            'total_income':fields.float('Annual Income:', required=False),
            'date_of_birth':fields.date('Date of Birth:', required=False),
            'age':fields.integer('Age:', size=8, readonly=True),
            'month':fields.integer('Month:', size=8, readonly=True),
            'days':fields.integer('Days:', size=8, readonly=True),
            'ben_wakf':fields.text('Ben: Wakf Board:',size=64, required=False),
            'check_required':fields.boolean('Date checking not Required:', required=False),
            'sws_id':fields.many2one('sws.registration','HANDICAPPED',ondelete='set null'),
            'sws_id1':fields.many2one('res.partner','PENSION10',ondelete='set null'),
                }
sws_category_handicaped()

class sws_category_destitute(osv.osv):
 
    _name = 'sws.category.destitute'
    _description = 'sws.category.destitute'
    
    def on_change_DOB(self, cr, uid, ids,dob, context=None):
        age = False
        month = False
        days = False
        if dob:
            dt = datetime.strptime(dob,"%Y-%m-%d")
            r = relativedelta(datetime.now(), dt)
            age = r.years
            month = (r.years * 12 + r.months + r.days/30) - age*12
            day = r.days % 30
            #day = (r.years * 365 + r.months * 30 + r.days)-(r.years * 365 + r.months * 30)
        if age >= 0 and month >= 0 and day >= 0:
            return {'value':{'age':age,
                           'month':month,
                           'days':day,
                           }}
 
    _columns = {
            'job_name':fields.char('Job:',size=64, required=False),
            'income':fields.float('Income:', required=False),
            'other_income':fields.float('Other Income:', required=False),
            'total_income':fields.float('Annual Income:', required=False),
            'date_of_birth':fields.date('Date of Birth:', required=False),
            'age':fields.integer('Age:', size=8, readonly=True),
            'month':fields.integer('Month:', size=8, readonly=True),
            'days':fields.integer('Days:', size=8, readonly=True),
            'ben_wakf':fields.text('Ben: Wakf Board:',size=64, required=False),
            'check_required':fields.boolean('Date checking not Required:', required=False),
            'sws_id':fields.many2one('sws.registration','PENSION',ondelete='set null'),
            'sws_id1':fields.many2one('res.partner','PENSION11',ondelete='set null'),
                }
sws_category_destitute()

class pop_up_cancel(osv.osv):
 
    _name = 'pop.up.cancel'
    _description = 'pop.up.cancel'
    
    _columns = {
              'name':fields.char('Reason summary:', required=False), 
              'over_income':fields.boolean('Overincome:', required=False), 
              'grant_sanctioned':fields.boolean('Grant Sanctioned Once:', required=False),
              'after_marriage':fields.boolean('After Marriage:', required=False),
              'age_not_specified':fields.boolean('Age not verified:', required=False),
              'under_age':fields.boolean('Under Age:', required=False),
              'exp_not_spcfed':fields.boolean('Experience not specified:', required=False),
              'under_experience':fields.boolean('Under Prescribed Experience:', required=False),
              'job_income_not':fields.boolean('Job income not specified:', required=False),
              'no_reason':fields.boolean('No Reason:', required=False),
              'no_annual_income':fields.boolean('Not Specified Annual Income:', required=False),
              'mahal_not_regd':fields.boolean('Membership Mahal not specified:', required=False),
              'undefined_ctgry':fields.boolean('Un-defined Category:', required=False),
              'certificate_not':fields.boolean('Certificate(s) not Submitted:', required=False),
              'institue_not':fields.boolean('The service institution not Registered:', required=False),
              'sws_id1':fields.many2one('res.partner','Popup',ondelete='set null'), 
                
                
                }
pop_up_cancel()

