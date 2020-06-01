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
{
	'name' : 'HR Annual Leave test',
	'version' : '0.1',
	'author' : 'Asmaa Aly',
	'category' : 'Human Resources',
	'description' : """
	The purpose of this module is to manage Annual Leave for all employee or for each department through odoo 8 annual leave Module as HR new feature. 
	Integrated with Holidays Management

	""",

	'depends' : ['hr', 'hr_holidays'],
	'data': [
		'datas/hr_annual_leave_data.xml',
		'views/hr_annual_leave_view.xml',
	],

	'installable': True,
	'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
