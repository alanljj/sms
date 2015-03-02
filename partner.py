# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Autor:Kevin Kong (kfx2007@163.com)
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

from openerp import fields,_,api,models

class partner(models.Model):
	_name="partner.sms"

	message = fields.Text('Message')

	@api.one
	def btn_ok(self):
		ids = self.env.context.get('active_ids')
		partner_obj = self.env['res.partner']
		sms_obj = self.env['sms.message']
		for id in ids:
			partner = partner_obj.search([('id','=',id)])
			if not partner.mobile:
				raise ValueError(_('Partner has no mobile!'))
			sms = sms_obj.create({'partner':partner.id,'mobile':partner.mobile,'message':self.message})
			if sms:
				sms.btn_send()
