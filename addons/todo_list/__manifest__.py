# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Todo List',
    'version': '1.0',
    'category': 'Productivity',
    'summary': 'Simple to-do list application with local storage sync',
    'description': """
Todo List Application
=====================

A simple to-do list application that allows users to:
* Add, edit, complete, and delete tasks
* Use local storage for offline functionality
* Sync tasks with Odoo backend
* Access through dedicated menu

Features:
* Task management with title, description, status, and due date
* Client-side interface with localStorage persistence
* Backend synchronization when needed
* User-specific task access
    """,
    'depends': ['base', 'web'],
    'data': [
        'security/ir.model.access.csv',
        'security/todo_list_security.xml',
        'views/todo_task_views.xml',
        'views/todo_list_menus.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'todo_list/static/src/js/todo_list_client.js',
            'todo_list/static/src/css/todo_list.css',
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}