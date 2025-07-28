# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import json
from odoo import http
from odoo.http import request


class TodoSyncController(http.Controller):

    @http.route('/todo_list/sync', type='json', auth='user', methods=['POST'])
    def sync_tasks(self, **kw):
        """Sync local storage tasks with backend."""
        try:
            tasks_data = kw.get('tasks', [])
            
            # Get existing tasks for the user
            existing_tasks = request.env['todo.task'].search([
                ('user_id', '=', request.env.user.id)
            ])
            
            # Create new tasks from local storage
            created_tasks = []
            for task_data in tasks_data:
                # Ensure user_id is set to current user
                task_data['user_id'] = request.env.user.id
                
                # Convert date strings if present
                if 'due_date' in task_data and task_data['due_date']:
                    # Assuming ISO date format from JS
                    task_data['due_date'] = task_data['due_date']
                
                task = request.env['todo.task'].create(task_data)
                created_tasks.append({
                    'id': task.id,
                    'title': task.title,
                    'description': task.description,
                    'status': task.status,
                    'due_date': task.due_date.isoformat() if task.due_date else None,
                })
            
            # Return all user tasks (existing + newly created)
            all_tasks = request.env['todo.task'].search([
                ('user_id', '=', request.env.user.id)
            ])
            
            result = []
            for task in all_tasks:
                result.append({
                    'id': task.id,
                    'title': task.title,
                    'description': task.description,
                    'status': task.status,
                    'due_date': task.due_date.isoformat() if task.due_date else None,
                })
            
            return {
                'success': True,
                'tasks': result,
                'created_count': len(created_tasks)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    @http.route('/todo_list/get_tasks', type='json', auth='user', methods=['POST'])
    def get_tasks(self, **kw):
        """Get all tasks for the current user."""
        try:
            tasks = request.env['todo.task'].search([
                ('user_id', '=', request.env.user.id)
            ])
            
            result = []
            for task in tasks:
                result.append({
                    'id': task.id,
                    'title': task.title,
                    'description': task.description,
                    'status': task.status,
                    'due_date': task.due_date.isoformat() if task.due_date else None,
                })
            
            return {
                'success': True,
                'tasks': result
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }