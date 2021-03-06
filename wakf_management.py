from osv import osv
from osv import fields
from tools.translate import _


class wakf_management(osv.osv):
    """
         Open ERP Model
    """
    _name = 'wakf.management'
    _description = 'wakf.management'
    _order = "id desc"
    
    def on_change_wakf(self, cr, uid, ids, wakf_reg_no, context=None):
        values = {}
        if wakf_reg_no:
            cust = self.pool.get('res.partner').browse(cr, uid, wakf_reg_no, context=context)
            values = {
                'wakf_reg_no': cust.wakf_reg_no
            }
        return {'value' : values}
    def on_change_wakf_name(self, cr, uid, ids, reg_no, context=None):
        values = {}
        id_res_partner = self.pool.get('res.partner')
        if reg_no:
            search_condition = [('wakf_reg_no', '=', reg_no)]
            search_ids = id_res_partner.search(cr, uid, search_condition, context=context)
            similar_objs = id_res_partner.browse(cr, uid, search_ids, context=context)
            if similar_objs:
                output = id_res_partner.browse(cr, uid, search_ids, context=context)[0].id
                values = {
                            'wakf_id': output,
               
                    }
            else:
                values ={
                            'wakf_id': False,
                              }
        return {'value' : values}
    def _get_active_id(self, cr, uid, ids, context=None):
        if context is None: context = {}
        return context.get('active_id', False)
 
    _columns = {
            'wakf_id':fields.many2one('res.partner','Wakf Name',ondelete='set null'),           
            'name':fields.selection([('muthavalli','Muthavalli'),('mangement','Management Committee'),('kswb','State Waqf Board')],'Managed by'),
            'name_waquif':fields.char('Waquif Name', size=128, required=False),
            'name_father':fields.char('Waquif Father Name', size=128, required=False),
            'details_waquif':fields.text('Managing Committee Address ',required=False),
            'from_date':fields.date('Committee Approved Date',required=False),
            'to_date':fields.date('Expired Date',required=False),
            'name_member':fields.char('Member Name', size=64, required=False),
            'name_presi':fields.char('President Name', size=64, required=False),
            'managedby_address':fields.text('Managing Committee Address',required=False),
            'name_city':fields.char('City', size=64, required=False),
            'company_id': fields.many2one('res.company', 'Company', required=False)
        }
    _defaults = {
            'company_id': lambda self,cr,uid,ctx: self.pool['res.company']._company_default_get(cr,uid,object='wakf.management',context=ctx)
                 }

wakf_management()

class wakf_managedby(osv.osv):
    
    _name = 'wakf.managedby'
    _description = 'wakf.managedby'
 
    _columns = {
                'name':fields.char('Name', size=64, required=True),
                'description':fields.text('Description',required=False),
                }
    
    
wakf_managedby()