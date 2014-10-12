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
    _order = "id desc"
    
    def action_scheduler_pension(self, cr, uid, automatic=False, use_new_cursor=False, context=None):
        pension_line = []
        today = date.today()
        today_copy = today
        month = today.month
        year = today.year
        today = today.strftime("%Y-%m-%d")
        id_search = self.pool.get('res.partner').search(cr,uid,[('state1','in',['sanctioned','revolving']),('head.name','=',"Pension")])
        for id_browse in self.pool.get('res.partner').browse(cr,uid,id_search):
            pension_line = []
            browse_id = id_browse.id
            amount = id_browse.amount_sanction
            date_sanction = id_browse.date_sanction
            if month == 1: month = 'JAN'
            if month == 2: month = 'FEB'
            if month == 3: month = 'MAR'
            if month == 4: month = 'APR'
            if month == 5: month = 'MAY'
            if month == 6: month = 'JUN'
            if month == 7: month = 'JUL'
            if month == 8: month = 'AUG'
            if month == 9: month = 'SEP'
            if month == 10: month = 'OCT'
            if month == 11: month = 'NOV'
            if month == 12: month = 'DEC'
            if date_sanction <= today:  
                pension_line.append((0,0,{'date_sanction':today,'status':'pending','for_month':month,'year':year,'amount':amount}))
                self.pool.get('res.partner').write(cr,uid,id_browse.id,{'state1':'revolving','history_transaction':pension_line})
        return True
    
    def action_edu_loan_days(self, cr, uid, automatic=False, use_new_cursor=False, context=None):
        pension_line = []
        invoice_ids = []
        today = date.today()
        today_copy = today
        month = today.month
        year = today.year
        today = today.strftime("%Y-%m-%d")
        id_search_all = self.pool.get('res.partner').search(cr,uid,[('state1','in',['sanctioned','revolving']),('head.name','=',"Education Loan")])
        for id_browse in self.pool.get('res.partner').browse(cr,uid,id_search_all):
            course_end = id_browse.course_end
            if course_end <= today:
                self.pool.get('res.partner').write(cr,uid,id_browse.id,{'state1':'re_payment'})    
        id_search = self.pool.get('res.partner').search(cr,uid,[('state1','in',['sanctioned','revolving','re_payment']),('head.name','=',"Education Loan")])
        for id_browse in self.pool.get('res.partner').browse(cr,uid,id_search):
            head = id_browse.head.id
            appli_no = id_browse.appli_no
            output = id_browse.id
            product = id_browse.category.id
            action_line = []
            for lines in id_browse.education_byyear:
                if today >= lines.date_from and today < lines.date_to and lines.state == 'pending':
                    invoice_ids = []
                    line_id = lines.id
                    date_from = lines.date_from
                    date_to = lines.date_to
                    amount = lines.amount
                    price_unit = lines.amount
                    new_amount = lines.amount
                    ###############################################################################################
                    search_ids = self.pool.get('account.account').search(cr,uid,[('name','=',"Accounts Receivable")])
                    if not search_ids:
                        raise osv.except_osv(_('Warning!'), _('Please create an account "Accounts Receivable" first'))
                    account_id = self.pool.get('account.account').browse(cr,uid,search_ids)[0].id
                    
                    search_ids = self.pool.get('account.journal').search(cr,uid,[('name','=',"Assessment Journal")])
                    if not search_ids:
                        raise osv.except_osv(_('Warning!'), _('Please create "Assessment Journal" First'))
                    journal_id = self.pool.get('account.journal').browse(cr,uid,search_ids)[0].id
                    ###############################################################################################
                    invoice_ids.append((0,0,{'product_id':product,'name':"Education Loan",'quantity':1,'price_unit':price_unit,'new_amount':new_amount,'sws':True}))
                    self.pool.get('account.invoice').create(cr,uid,{'date_sanction':date_from,'head':head,'journal_type':'sale','type':'out_invoice','is_sws':True,'appli_no':appli_no,'account_id':account_id,'journal_id':journal_id,'partner_id':output,'invoice_line':invoice_ids})
                    action_line.append((1,line_id,{'state':'collected'}))
                    self.pool.get('res.partner').write(cr,uid,output,{'state1':'revolving','education_byyear':action_line})
            ##############################################################################################################
            ##############################################################################################################
        id_search = self.pool.get('res.partner').search(cr,uid,[('state1','in',['re_payment','revolving']),('head.name','=',"Education Loan")])
        for id_browse in self.pool.get('res.partner').browse(cr,uid,id_search):
            list_find = [lines.state for lines in id_browse.education_byyear]
            if list_find:
                if list_find[-1] == 'returned':
                    id_write = id_browse.id
                    self.pool.get('res.partner').write(cr,uid,id_write,{'state1':'paid'},context=None)
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
                        'district_sws_id':similar_objs.district_id.id,
                        }
                return {'value' :values}
            else:
                values={'partner_id':False,
                        'district_sws_id':False}
                return {'value' :False}
        return {'value' :False}
    
    def on_change_wakf_name1_to_regno(self, cr, uid, ids, wakf_id, context=None):
        values = {}
        id_res_partner=self.pool.get('res.partner')
        if wakf_id:
            similar_objs = id_res_partner.browse(cr, uid, wakf_id, context=context).wakf_reg_no
            if similar_objs:
                values={'reg_no':similar_objs,
                        'district_sws_id':similar_objs.district_id.id,
                            }
                return {'value' :values}
            else:
                values={'reg_no':False,
                        'district_sws_id':False
                            }
                return {'value' :values}
        return False
    
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
    
    def on_change_wakf_name_to_regno(self, cr, uid, ids, wakf_id, context=None):
        values = {}
        id_res_partner=self.pool.get('res.partner')
        if wakf_id:
            similar_objs = id_res_partner.browse(cr, uid, wakf_id, context=context).wakf_reg_no
            values={'reg_no':similar_objs,
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

class education_loan_by_year(osv.osv):
 
    _name = 'education.loan.byyearp'
    _description = 'education.loan.byyear'
    
    _columns = {
                'year':fields.integer('Year', required=False),
                'date_from':fields.date('Date From', required=False),
                'date_to':fields.date('Date To', required=False),
                'amount':fields.float('Amount'),
                'state': fields.selection([
                    ('pending', 'Pending'),
                    ('collected', 'Transfered'),
                    ('returned', 'Returned'),
                    ],'status', readonly=False), 
                'education_loan_byyear_id':fields.many2one('res.partner','EDU LOAN YEAR',ondelete='set null'),
                
                }
education_loan_by_year()

#################################################################################################
###################################  UPDATES  ###################################################
class pension_cycle(osv.osv):
    _name = 'pension.cycle'
    _description = 'pension.cycle'
    
    def _deflt_pending_pensions(self, cr, uid, ids, context=None):
        pending_list = []
        date_reference = False
        for_month = False
        year = False
        amount = False
        status = False
        for rec in self.browse(cr,uid,ids,context):
            ################## Finding Order for payment ##############            
            ###########################################################
            res_partner_search = self.pool.get('res.partner').search(cr,uid,[('head.name','=','Pension'),('state1','in',['sanctioned','revolving'])])
            res_partner_browse = self.pool.get('res.partner').browse(cr,uid,res_partner_search)
            for records in res_partner_browse:
                name_appli = records.id
                application_no = records.appli_no
                head = records.head.id
                category = records.category.id
                for line in records.history_transaction:
                    if line.status == 'pending':
                        amount = line.amount
                        year = line.year
                        for_month = line.for_month
                        date_reference = line.date_sanction
                        status = 'Pending'
                        pending_list.append((0,0,{'category':category,'head':head,'application_no':application_no,'date_reference':date_reference,'name_appli':name_appli,'date_year':year,'date_month':for_month,'sanctioned_amount':amount,'status':status,'full_reconcile':False}))
            return pending_list
        
    def button_update(self, cr, uid, ids, context):
        total_pending = 0
        pending_year_list = []
        return_list = []
        dummy_list = []
        dicto = {}
        granded_amount = 0
        balance_amount = 0
        total_reconcile = 0
        for rec in self.browse(cr,uid,ids):
            granded_amount = rec.maximum_amount
            balance_amount = granded_amount
            for line in rec.pension_line_id:
                if line.date_reference:
                    pending_year_list.append(line.date_reference)
                total_pending = total_pending + line.sanctioned_amount
            #pending_year_list = pending_year_list.sort()
            #sorted(pending_year_list)   #### NOW DATES ARE IN ASCENDING ORDER
            for datas in pending_year_list:
                for line_in in rec.pension_line_id:
                    id_test = line_in.id
                    application_no = line_in.application_no
                    name_appli = line_in.name_appli.id
                    date_reference = line_in.date_reference
                    date_year = line_in.date_year
                    date_month = line_in.date_month
                    sanctioned_amount = line_in.sanctioned_amount
                    status = line_in.status
                    full_reconcile = line_in.full_reconcile    
                    if line_in.date_reference: 
                        if datas == line_in.date_reference:  # Matching Date field with sorted date
                            amount_single = line_in.sanctioned_amount
                            if amount_single <= balance_amount:
                                balance_amount = balance_amount - amount_single
                                total_reconcile = total_reconcile + amount_single
                                total_pending = total_pending - amount_single
                                full_reconcile = True
                                return_list.append((1, id_test, {'full_reconcile':full_reconcile}))    
                    id_of = line_in.id                                  ###  Removing Noise in the list
                    dummy_list.append((1,id_of,{'full_reconcile':False}))
            self.write(cr,uid,ids,{'pension_line_id':dummy_list})
            self.write(cr,uid,ids,{'test':pending_year_list,'actual_amount':total_pending,'balance_amount':balance_amount,'pension_line_id':return_list})
        return True
    
    def button_allocate(self, cr, uid, ids, context):
        invoice_ids = []
        change_list = []
        for rec in self.browse(cr,uid,ids,context=context):
            for line in rec.pension_line_id:
                invoice_ids = []
                if line.full_reconcile:
                    date_sanction = line.date_reference
                    head = line.head.id
                    for_month = line.date_month
                    year = line.date_year
                    amount = line.sanctioned_amount
                    appli_no = line.application_no
                    partner_id = line.name_appli.id
                    product = line.category.id
                    name = line.category.name
                    quantity = 1
                    price_unit = amount
                    new_amount = amount
                    ###############################################################################################
                    search_ids = self.pool.get('account.account').search(cr,uid,[('name','=',"Accounts Receivable")])
                    if not search_ids:
                        raise osv.except_osv(_('Warning!'), _('Please create an account "Accounts Receivable" first'))
                    account_id = self.pool.get('account.account').browse(cr,uid,search_ids)[0].id
                    
                    search_ids = self.pool.get('account.journal').search(cr,uid,[('name','=',"Assessment Journal")])
                    if not search_ids:
                        raise osv.except_osv(_('Warning!'), _('Please create "Assessment Journal" First'))
                    journal_id = self.pool.get('account.journal').browse(cr,uid,search_ids)[0].id
                    ###############################################################################################
                    invoice_ids.append((0,0,{'product_id':product,'name':name,'quantity':quantity,'price_unit':price_unit,'new_amount':new_amount,'sws':True}))
                    self.pool.get('account.invoice').create(cr,uid,{'date_sanction':date_sanction,'key':"pension",'head':head,'for_month':for_month,'year':year,'amount':amount,'journal_type':'purchase','type':'in_invoice','is_sws':True,'appli_no':appli_no,'account_id':account_id,'journal_id':journal_id,'partner_id':partner_id,'invoice_line':invoice_ids})   
                    #################################################################################################
                    #################################################################################################
                    search_res = self.pool.get('res.partner').search(cr,uid,[('head.name','=','Pension'),('appli_no','=',appli_no),('id','=',partner_id),('state1','in',['sanctioned','revolving'])])
                    res_partner_browse = self.pool.get('res.partner').browse(cr,uid,search_res)
                    for values in res_partner_browse:
                        id_res = values.id
                        for line in values.history_transaction:
                            if line.amount == amount and line.date_sanction == date_sanction and line.status == 'pending':
                                id_line = line.id
                                change_list.append((1,id_line,{'status':'invoiced'}))
                                self.pool.get('res.partner').write(cr,uid,id_res,{'history_transaction':change_list})
        return True
        
    
    _columns = {
            'date_today':fields.date('Date of Sanction'),
            'date_upto':fields.date('Date Upto'),
            'maximum_amount':fields.float('Granted Amount'),
            'actual_amount':fields.float('Amount Required to reconcile'),
            'balance_amount':fields.float('Unreconciled Amount'),
            'pension_line_id':fields.one2many('pension.cycle.line','cycle_id','Pension Cycle'),
            'test':fields.text('test'),
                }
    _defaults = {
                 'pension_line_id':_deflt_pending_pensions,
                 'date_today':time.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                 }
pension_cycle()
class pension_cycle_line(osv.osv):
    _name = 'pension.cycle.line'
    _description = 'pension.cycle.line'
    _order = "date_reference asc"
    
    _columns = {
            'application_no':fields.char('Application No.'),
            'name_appli':fields.many2one('res.partner','Name',ondelete='set null'),
            'head':fields.many2one('product.category','Head',ondelete='set null'),
            'category':fields.many2one('product.product','Category',ondelete='set null'),
            'date_reference':fields.date('Due Date'),
            'date_year':fields.char('Year'),
            'date_month':fields.char('Month'),
            'sanctioned_amount':fields.float('Amount'),
            'status':fields.char('Status'),
            'full_reconcile':fields.boolean('Full Reconcile'),
            'cycle_id':fields.many2one('pension.cycle','Cycle of Pension',ondelete='set null'),
                }
pension_cycle_line()
#################################################################################################



