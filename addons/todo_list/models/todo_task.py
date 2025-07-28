# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class TodoTask(models.Model):
    _name = 'todo.task'
    _description = 'Todo Task'
    _order = 'due_date asc, create_date desc'

    title = fields.Char(string='Title', required=True)
    description = fields.Text(string='Description')
    status = fields.Selection([
        ('pending', 'Pending'),
        ('completed', 'Completed')
    ], string='Status', default='pending', required=True)
    due_date = fields.Date(string='Due Date')
    user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user, required=True)
    
    def name_get(self):
        """Return a meaningful representation of the task."""
        result = []
        for record in self:
            name = record.title
            if record.due_date:
                name = f"{name} (Due: {record.due_date})"
            result.append((record.id, name))
        return result
    
    @api.model
    def create_from_local_storage(self, tasks_data):
        """Create tasks from local storage data."""
        created_tasks = []
        for task_data in tasks_data:
            # Only create if user_id matches current user or is not set
            if 'user_id' not in task_data:
                task_data['user_id'] = self.env.user.id
            elif task_data['user_id'] != self.env.user.id:
                continue  # Skip tasks that don't belong to current user
                
            task = self.create(task_data)
            created_tasks.append(task)
        return created_tasks
    
    def toggle_status(self):
        """Toggle task status between pending and completed."""
        for task in self:
            task.status = 'completed' if task.status == 'pending' else 'pending'