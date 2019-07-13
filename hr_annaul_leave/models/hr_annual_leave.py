# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2014-2015 Asmaa Aly.
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
import datetime
import math
import time
from operator import attrgetter

from openerp import models, fields, api
from openerp.exceptions import except_orm, Warning, RedirectWarning
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta

#Test

class hr_annual_leave(models.Model):
	_name = "hr.annual.leave"
	_description ="Annual leave"
	
	name = fields.Char(String="Year", required=True)
	department_ids = fields.Many2many('hr.department', string="Department(s)")
	start_date = fields.Date(string="Start Date", default=lambda *a: time.strftime('%Y-01-01'), required=True)
	end_date = fields.Date(string="End Date", default=lambda *a: time.strftime('%Y-12-31'), required=True)
	leave_days_ids = fields.One2many('hr.annual.leave.day', 'annual_leave_id', string="Annual Leave Days", index=True)
	
	state = fields.Selection([
		('draft','Draft'),
		('confirm','Confirmed'),
	], string="Status", default='draft', track_visibility='onchange', copy=False)
	
	
	@api.model
	def create(self, values):
		res = super(hr_annual_leave, self).create(values)
		for lv_day in res['leave_days_ids']:
			if lv_day.date_of_day < res['start_date'] or lv_day.date_of_day > res['end_date']:
				raise except_orm('Warning','The date must be in range')
		return res
	
	@api.multi
	def apply_annual_leave(self):
		holiday_obj = self.env['hr.holidays']
		holiday_status_id = self.env['hr.holidays.status'].search([('name','=','Annual Leave')]).id
		
		for day in self.leave_days_ids:
			holiday_list = []
			if self.department_ids:
				for dep in self.department_ids:
					for employee in self.env['hr.employee'].search([('department_id','=',dep.id)]):
						vals ={
							'name': day.event,
							'holiday_status_id': holiday_status_id,
							'date_from': day.date_of_day,
							'date_to': day.date_of_day,
							'employee_id': employee.id,
							'number_of_days_temp': 1.0,
						}
						holiday_id=holiday_obj.create(vals)
						holiday_id.holidays_validate()
						holiday_list.append(holiday_id)
			else:
				for employee in self.env['hr.employee'].search([]):
					vals ={
						'name': day.event,
						'holiday_status_id': holiday_status_id,
						'date_from': day.date_of_day,
						'date_to': day.date_of_day,
						'employee_id': employee.id,
						'number_of_days_temp': 1.0,
					}
					holiday_id=holiday_obj.create(vals)
					holiday_id.holidays_validate()
					holiday_list.append(holiday_id)
			
			day.write({'holiday_ids':holiday_list})	
		self.write({'state':'confirm'})
	
	
class hr_annual_leave_day(models.Model):
	_name = "hr.annual.leave.day"
	_description="Annual Leave Days"
	
	@api.one
	def _get_name(self):
		
		ds = datetime.strptime(self.date_of_day, '%Y-%m-%d')
		self.name = ds.strftime('%d/%m')+"( "+ self.event +" )"
	
	name = fields.Char(string="Name", compute='_get_name')
	date_of_day = fields.Date(string="Date", required=True)
	day_of_week = fields.Selection([
		('0','Monday'),
		('1','Tuesday'),
		('2','Wednesday'),
		('3','Thursday'),
		('4','Friday'),
		('5','Saturday'),
		('6','Sunday')], string ="Day of Week", required=True, select=True)
	event = fields.Char(string="Event", required=True)
	holiday_ids = fields.One2many('hr.holidays','annual_leave_day_id', string="Holidays")
	annual_leave_id = fields.Many2one('hr.annual.leave', string="Annual Leave Ref.", ondelete='cascade')
	
	@api.multi
	def onchange_date_of_day(self, date_of_day):
		if date_of_day:
			return {
				'value':{
					'day_of_week' : str(datetime.strptime(date_of_day,"%Y-%m-%d").weekday())
					}
				}
	@api.multi			
	def delete_leave_day(self):
		leave_type = self.env['hr.holidays.status'].search([('name','=','Annual Leave')]).id
		holiday_ids = self.env['hr.holidays'].search([('date_from','=',self.date_of_day),('holiday_status_id','=',leave_type)])
		for lv_day in self:
			for holiday in holiday_ids:
				holiday.holidays_reset()
				holiday.unlink()
			lv_day.unlink()
		return {
			'type': 'ir.actions.client',
			'tag': 'reload',
		}

class hr_holidays(models.Model):
	_inherit="hr.holidays"
	
	annual_leave_day_id = fields.Many2one('hr.annual.leave.day', string="Annual Leave Ref.", ondelete='cascade')
		