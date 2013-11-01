# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    
#    Copyright (C) 2012 Mentis d.o.o. All rights reserved.
# 
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import string
from osv import fields, osv
from tools.translate import _

"""
account.invoice object:
    - Add support customer invoice reference number - RF
    - RF number calculated from invoice number
"""

    #else:
    # raise osv.except_osv(_('Warning!'),
    #     _('Empty BBA Structured Communication!' \
    #    '\nPlease fill in a unique BBA Structured Communication.'))

class account_invoice(osv.osv):
    _inherit = 'account.invoice'
    
    def action_reference(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
            
        for inv in self.browse(cr, uid, ids):
            if inv.type == 'out_invoice':
                ref_number = self.parse_reference_RF(inv.number)
                self.write(cr, uid, ids, {'reference':ref_number})

    def parse_reference_RF(self, inv_number):
        tmp_ref = filter(lambda c: c.isalnum(), inv_number)
        ctrl_num = self.calculate_control_number(tmp_ref + 'RF00')
        ref_num = ctrl_num + ' ' + tmp_ref
        return ref_num
        
    def calculate_control_number(self, ref_string):
        tmp_ref = ''
        for char in ref_string.lower():
            if char == 'a':
                tmp_ref = tmp_ref + '10'
            elif char == 'b':
                tmp_ref = tmp_ref + '11'
            elif char == 'c':
                tmp_ref = tmp_ref + '12'
            elif char == 'd':
                tmp_ref = tmp_ref + '13'
            elif char == 'e':
                tmp_ref = tmp_ref + '14'
            elif char == 'f':
                tmp_ref = tmp_ref + '15'
            elif char == 'g':
                tmp_ref = tmp_ref + '16'
            elif char == 'h':
                tmp_ref = tmp_ref + '17'
            elif char == 'i':
                tmp_ref = tmp_ref + '18'
            elif char == 'j':
                tmp_ref = tmp_ref + '19'
            elif char == 'k':
                tmp_ref = tmp_ref + '20'
            elif char == 'l':
                tmp_ref = tmp_ref + '21'
            elif char == 'm':
                tmp_ref = tmp_ref + '22'
            elif char == 'n':
                tmp_ref = tmp_ref + '23'
            elif char == 'o':
                tmp_ref = tmp_ref + '24'
            elif char == 'p':
                tmp_ref = tmp_ref + '25'
            elif char == 'q':
                tmp_ref = tmp_ref + '26'
            elif char == 'r':
                tmp_ref = tmp_ref + '27'
            elif char == 's':
                tmp_ref = tmp_ref + '28'
            elif char == 't':
                tmp_ref = tmp_ref + '29'
            elif char == 'u':
                tmp_ref = tmp_ref + '30'
            elif char == 'v':
                tmp_ref = tmp_ref + '31'
            elif char == 'w':
                tmp_ref = tmp_ref + '32'
            elif char == 'x':
                tmp_ref = tmp_ref + '33'
            elif char == 'y':
                tmp_ref = tmp_ref + '34'
            elif char == 'z':
                tmp_ref = tmp_ref + '35'
            else:
                tmp_ref = tmp_ref + char
        #calculate MOD 97-10
        ctrl_num = 98 - int(tmp_ref) % 97
        if ctrl_num < 10:
            res = "RF0%s" % ctrl_num
        else:
            res = "RF%s" % ctrl_num
        return res
    
    def _reference(self, cursor, user, ids, name, args, context={}):
        try:
            #logger.notifyChannel('bank_reference',netsvc.LOG_DEBUG,'ids: %s' %ids)
            invs = self.browse(cursor, user, ids, context)
        except KeyError, e:
            pass
        reslist = {}
        for inv in invs:
            if not inv.number:
                reslist[inv.id]=""
                continue
            inv_no = [x for x in inv.number if x.isdigit()]
            try:
                companyid = str(inv.company_id.id)
                if len(companyid) < 2: companyid = "0%s"%companyid
                inv_no = [x for x in companyid if x.isdigit()] + inv_no
            except Exception, e:
                print 'Cannot add company id to reference number.'
                #logger.notifyChannel('bank_reference',netsvc.LOG_WARNING, 'Cannot add company id to reference number. %s - %s' % (inv.company_id,e))
            prefix = "".join(inv_no)
            myCompany = self.pool.get('res.users').browse(cursor, user, user).company_id
            #logger.notifyChannel('bank_reference',netsvc.LOG_DEBUG,'id: %s, inv_ref_type: %s' % (inv.id, myCompany.inv_ref_type))
            res = ""
            if myCompany.country_id.code in ('FI', 'RF_fi', 'fi'):
                #logger.notifyChannel('bank_reference',netsvc.LOG_DEBUG,'Calculating Finnish Domestic reference')
                inv_no.reverse()
                mul = 7
                cs = 0
                for x in inv_no:
                    cs += mul*int(x)
                    if mul==7: mul=3
                    elif mul==3: mul=1
                    elif mul==1: mul=7
                chk = int(round(cs,-1))
                if chk < cs:
                    chk += 10
                cs = chk-cs
                if cs == 10: cs = 0
                res = str(prefix)+str(cs)
                #logger.notifyChannel('bank_reference',netsvc.LOG_DEBUG,'Calculated reference nubmer: %s'%res)
                resl = [x for x in res]
                i = 5

            if myCompany.country_id.code in ('FI', 'RF_fi', 'fi'):
                prefix = "".join([x for x in res if x.isdigit()])
                #logger.notifyChannel('bank_reference',netsvc.LOG_DEBUG,'Using finnish domestic reference as a root for RF number')

            if myCompany.country_id.code in ('FI', 'RF_fi', 'fi'):
                cs = 98 - int(prefix) % 97
                if cs < 10:
                    res = "RF0%s%s" % (cs,prefix)
                else:
                    res = "RF%s%s" % (cs,prefix)
            
            #cs = 98 - int(prefix) % 97
            #if cs < 10:
            #    res = "RF0%s%s" % (cs,prefix)
            #else:
            #    res = "RF%s%s" % (cs,prefix)
            self.write(cursor, user, ids, {'finref':res})
            reslist[inv.id] = res
        
        
        #logger.notifyChannel('bank_reference',netsvc.LOG_DEBUG,'reslist: %s' % reslist)
        return reslist

    _columns = {
        'bank_reference': fields.function(_reference, method=True, type='char', string='Bank reference'),
        'finref': fields.char('Finnish Reference', required=False)
    }
account_invoice()
