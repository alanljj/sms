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

from openerp import api,_,models,fields
from xml.etree import ElementTree
from openerp.exceptions import except_orm
import httplib,urllib
import cookielib
from datetime import datetime,timedelta


class sms_message(models.Model):
	_name='sms.message'

	partner = fields.Many2one('res.partner','Partner',required=True)
	mobile = fields.Char('Mobile')
	message = fields.Text('Message',required=True)
        send_time = fields.Datetime('Send Time')
	state = fields.Selection([('draft','Draft'),('success','Success'),('failed','Failed')],'States')
        err_msg = fields.Char('Err Msg')

        _defaults={
                "state":"draft",
        }

        @api.one
        def btn_send(self):
            #check if the partner's mobile is empty!
            if not self.partner.mobile:
				raise except_orm(_('Warning!'),_('the partner has no mobile!'))
            s_time = datetime.strptime(self.send_time,'%Y-%m-%d %H:%M:%S')+timedelta(hours=8)
            res = self.send_sms(self.mobile,self.message,s_time)
            if res['status']=="Success":
                self.state = "success"
            else:
                self.state = "failed"
                self.err_msg = res['message']

        @api.multi
        def send_sms(self,mobile,content,send_time):
            #get settings
            config_obj = self.env['ir.config_parameter']
            user_id = config_obj.get_param('sms.config.userid')
            send_address = config_obj.get_param('sms.config.address')
            username = config_obj.get_param('sms.config.username')
            password = config_obj.get_param('sms.config.password')
            appendix = config_obj.get_param('sms.config.appendix')

            httpclient=None
	    res ={}
	    try:
	        params=urllib.urlencode({
		    "action":"send",
		    "userid":int(user_id),
		    "account":username,
		    "password":password,
		    "mobile":mobile,
		    "content":content+appendix,
                    "sendTime":send_time,
		    "extno":'',
	        })
	    
	        address = send_address.split(':')
	        port = len(address)>1 and address[1] or 80

	        headers={"Content-type":"application/x-www-form-urlencoded","Accept":"text/plain"}
	        httpclient = httplib.HTTPConnection(address[0],int(port),timeout=30)
	        httpclient.request("POST","/sms.aspx",params,headers)

	        response=httpclient.getresponse()
	        result = response.read()
	    
	        # handle the xml result.
	        root = ElementTree.fromstring(result)
	        lst_node = root.getiterator("returnstatus")
	        for node in lst_node:
		    res['status'] = node.text
	        mes_node = root.getiterator("message")
	        res['message'] = mes_node[0].text
	    except Exception,e:
	        print e
	    finally:
	        if httpclient:
		    httpclient.close() 
	    return res


class sms_config(models.Model):
	_name="sms.config.settings"
	_inherit="res.config.settings"

	user_id = fields.Char('User ID',Help='user id that service provider gives to you')
	send_address = fields.Char('Interface Address',Help='The address that your sms send to')
	user_name = fields.Char('Account',Help='The username that can pass interface')
	pass_word = fields.Char('Password',password=True)
	appendix = fields.Char('End Text',Help="The text that append to every message's end")

	@api.multi
	def get_default_val(self):
		user_id = self.env['ir.config_parameter'].get_param('sms.config.userid')
		send_address = self.env['ir.config_parameter'].get_param('sms.config.address')
		username= self.env['ir.config_parameter'].get_param('sms.config.username')
		password = self.env['ir.config_parameter'].get_param('sms.config.password')
		appendix = self.env['ir.config_parameter'].get_param('sms.config.appendix')
		return {'user_id':user_id,'send_address':send_address,'user_name':username,
				'pass_word':password,'appendix':appendix}

	@api.multi
	def set_default_val(self):
		config_obj = self.env['ir.config_parameter']
		config_obj.set_param('sms.config.userid',self.user_id)
		config_obj.set_param('sms.config.address',self.send_address)
		config_obj.set_param('sms.config.username',self.user_name)
		config_obj.set_param('sms.config.password',self.pass_word)
		config_obj.set_param('sms.config.appendix',self.appendix)
