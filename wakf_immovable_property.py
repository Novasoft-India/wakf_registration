from openerp.osv import osv
from openerp.osv import fields

class wakf_immovableproperty(osv.osv):
    """
         Open ERP Model for immovableproperty
    """
    _name = 'wakf.immovableproperty'
    _description = 'wakf.immovableproperty'
    
    def get_convert(self, cr, uid, ids, fields, arg, context):
        converted = {}
        for record in self.browse(cr, uid, ids):
            area_non_standard = record.area
            unit = record.units_id.code
            ################ LookUp Table ################
            # 1 Acre = 100.01467985501355 Cent
            # 1 Sq.Feet = 0.002296 Cent
            # 1 Sq.Metres = 0.024688 Cent
            # 1 Sq.Yard = 0.020664 Cent
            # 1 Hectares = 247.1363878343195 Cent
            # 1 Kottah = 1.65311998677504 Cent
            # 1 Kanal = 247.93218242767915 Cent
            # 1 Marla = 12.396608987519919 Cent
            # 1 Ares = 2.4704960000259897 Cent
            ##############################################
            if unit == 'ACRE': value = 100.01467
            if unit == 'SQFT': value = 0.002296
            if unit == 'SQMT': value = 0.024688
            if unit == 'SQYD': value = 0.020664
            if unit == 'HCTR': value = 247.13638
            if unit == 'KOTA': value = 1.653119
            if unit == 'KANL': value = 247.932182
            if unit == 'MRLA': value = 12.396608
            if unit == 'ARES': value = 2.470496
            area_converted = area_non_standard * value
            converted[record.id]= area_converted
        return converted
 
    _columns = {
            'wakf_id':fields.many2one('res.partner','Wakf Name',ondelete='set null'), 
            'type_id':fields.many2one('wakf.type','Wakf Type',ondelete='set null',required=True),
                        
            'name':fields.char('Name', size=128, required=True),
            'landtype_id':fields.many2one('wakf.landtype','Land Type',ondelete='set null'),
            'location_boundaries':fields.text('Location / Boundaries',required=False),
            'propery_specifications':fields.text('Wakf Objectives',required=False),
            'area':fields.float('Area',required=False),
            'units_id':fields.many2one('wakf.units','Units',ondelete='set null'),
            'propery_classification':fields.selection((('rural','Rural'), ('urban','Urban')),'Rural/Urban',required=True),
            'wakf_objectives':fields.text('Wakf Objectives',required=False),
            'value':fields.float('Estimated Value',required=False),
            'valuation_date':fields.date('Valuation Date',required=False),
            'property_curr_status':fields.many2one('wakf.properystatus','Property Status',ondelete='set null'),
            'survey_no':fields.char('Survey Number',size=64,required=True),
            'survey_details':fields.text('survey Details',required=False),
            'survey_date':fields.date('Survey Date',required=False),
            'census_code':fields.char('Censud Code',size=8,required=False),
            'khata_no':fields.char('Khata No',size=8,required=False),
            'khewat_no':fields.char('Khasra / Khewat No',size=8,required=False),
            'amsom':fields.char('Amsom',size=8,required=False),
            'plot_no':fields.char('Plot no',size=8,required=False),
            'door_no':fields.char('Door No',size=8,required=False),
            'patta_no':fields.char('Patta No',size=8,required=False),
            'district_id':fields.many2one('wakf.district','District',ondelete='set null'),
            'taluk_id':fields.many2one('wakf.taluk','Taluk',ondelete='set null'),
            'village_id':fields.many2one('wakf.village','Village',ondelete='set null'), 
            'converted_area':fields.function(get_convert,string='Area in Cent',store=True,type='float',method=False),
        }
wakf_immovableproperty()

class wakf_landtype(osv.osv):
    
    _name='wakf.landtype'
    _description='wakf.description'
    
    _columns= {
               'name':fields.char('Name',size=32,required=True),
               'description':fields.text('Description',required=True)
               
               }
wakf_landtype()

class wakf_units(osv.osv):
    
    _name='wakf.units'
    _description='wakf.description'
    
    _columns= {
               'code':fields.char('Code',size=32,required=True),
               'name':fields.char('Name',size=32,required=True),
               'description':fields.text('Description',required=True)           
              
              }
wakf_units()

class wakf_properystatus(osv.osv):
    
    _name ='wakf.properystatus'
    _description='wakf.properystatus'
    
    _columns = {
            'name':fields.char('Name',size=32,required=True),
            'description':fields.text('Description',required=True) 
                
     }
wakf_properystatus()

