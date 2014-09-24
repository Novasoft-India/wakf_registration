from osv import osv
from osv import fields
from tools.translate import _

class sws_criteria(osv.osv):
 
    _name = 'sws.criteria'
    _description = 'sws.criteria'
 
    _columns = {
            'name':fields.char('Criteria Name:', required=False),
            'criteria_no':fields.integer('Criteria Number:', required=False), 
            'active_is':fields.boolean('Active',required=False),
            'date_valid':fields.date('Date valid From',required=False),
            'criteria_line_id':fields.one2many('sws.criteria.line','criteria_id'),  
            'company_id': fields.many2one('res.company', 'Company', required=False)
                }
    _defaults = {
            'company_id': lambda self,cr,uid,ctx: self.pool['res.company']._company_default_get(cr,uid,object='sws.scholar.sanction.criteria',context=ctx)
                 }
sws_criteria()

class sws_criteria_line(osv.osv):
 
    _name = 'sws.criteria.line'
    _description = 'sws.criteria.line'
 
    _columns = {
            'category':fields.many2one('product.product','Category',domain=['&',('income','!=',True),('expense','!=',True)], required=True), 
            'lower_age':fields.integer('Lower Age Limit',required=False),
            'higher_income':fields.integer('higher Income Limit',required=False),
            'min_exp':fields.integer('Minimum Experience(in year)',required=False),
            'min_work_gap':fields.integer('Minimum Work Gap(in months)',required=False),
            'criteria_id':fields.many2one('sws.criteria','Category', required=False),   
            
                }
sws_criteria_line()