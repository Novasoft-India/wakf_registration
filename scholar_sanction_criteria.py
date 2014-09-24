from osv import osv
from osv import fields
from tools.translate import _

class sws_scholar_sanction_criteria(osv.osv):
 
    _name = 'sws.scholar.sanction.criteria'
    _description = 'sws.scholar.sanction.criteria'
 
    _columns = {
            'name':fields.char('Criteria Name:', required=False),
            'criteria_no':fields.integer('Criteria Number:', required=False), 
            'active_is':fields.boolean('Active',required=False),
            'date_valid':fields.date('Date valid From',required=False),
            'criteria_line_id':fields.one2many('sws.scholar.sanction.criteria.line','criteria1_id'),  
            'company_id': fields.many2one('res.company', 'Company', required=False)
                }
    _defaults = {
            'company_id': lambda self,cr,uid,ctx: self.pool['res.company']._company_default_get(cr,uid,object='sws.scholar.sanction.criteria',context=ctx)
                 }
sws_scholar_sanction_criteria()


class sws_scholar_sanction_criteria_line(osv.osv):
 
    _name = 'sws.scholar.sanction.criteria.line'
    _description = 'sws.scholar.sanction.criteria.line'
 
    _columns = {
            'category_course':fields.many2one('sws.scholar.criteria.course','Course', required=True), 
            'amount_sanction':fields.integer('Total Amount',required=True),
            'amount_per_year':fields.integer('Amount Per Year',required=True),
            'total_year':fields.integer('Total Years', required=True),
            'criteria1_id':fields.many2one('sws.scholar.sanction.criteria','Line of Sanction Criteria')   
            
                }
sws_scholar_sanction_criteria_line()