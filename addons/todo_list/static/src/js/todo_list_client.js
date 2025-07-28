/** @odoo-module **/

import { Component, useState, onWillStart } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

class TodoListClient extends Component {
    static template = "todo_list.TodoListClient";

    setup() {
        this.rpc = useService("rpc");
        this.notification = useService("notification");
        
        this.state = useState({
            tasks: [],
            newTask: {
                title: '',
                description: '',
                due_date: '',
                status: 'pending'
            },
            showForm: false,
            editingTask: null
        });

        onWillStart(async () => {
            this.loadLocalTasks();
        });
    }

    // Local Storage Management
    loadLocalTasks() {
        try {
            const storedTasks = localStorage.getItem('odoo_todo_tasks');
            if (storedTasks) {
                this.state.tasks = JSON.parse(storedTasks);
            }
        } catch (error) {
            console.error('Error loading tasks from localStorage:', error);
            this.state.tasks = [];
        }
    }

    saveLocalTasks() {
        try {
            localStorage.setItem('odoo_todo_tasks', JSON.stringify(this.state.tasks));
        } catch (error) {
            console.error('Error saving tasks to localStorage:', error);
            this.notification.add('Error saving tasks locally', { type: 'danger' });
        }
    }

    // Task Management
    addTask() {
        if (!this.state.newTask.title.trim()) {
            this.notification.add('Please enter a task title', { type: 'warning' });
            return;
        }

        const task = {
            id: Date.now(), // Simple ID for local storage
            title: this.state.newTask.title,
            description: this.state.newTask.description,
            due_date: this.state.newTask.due_date,
            status: 'pending'
        };

        this.state.tasks.push(task);
        this.saveLocalTasks();
        this.resetForm();
        this.notification.add('Task added successfully', { type: 'success' });
    }

    editTask(task) {
        this.state.editingTask = { ...task };
        this.state.newTask = { ...task };
        this.state.showForm = true;
    }

    updateTask() {
        if (!this.state.newTask.title.trim()) {
            this.notification.add('Please enter a task title', { type: 'warning' });
            return;
        }

        const index = this.state.tasks.findIndex(t => t.id === this.state.editingTask.id);
        if (index !== -1) {
            this.state.tasks[index] = { ...this.state.newTask };
            this.saveLocalTasks();
            this.resetForm();
            this.notification.add('Task updated successfully', { type: 'success' });
        }
    }

    deleteTask(task) {
        if (confirm('Are you sure you want to delete this task?')) {
            const index = this.state.tasks.findIndex(t => t.id === task.id);
            if (index !== -1) {
                this.state.tasks.splice(index, 1);
                this.saveLocalTasks();
                this.notification.add('Task deleted successfully', { type: 'success' });
            }
        }
    }

    toggleTaskStatus(task) {
        task.status = task.status === 'pending' ? 'completed' : 'pending';
        this.saveLocalTasks();
        this.notification.add('Task status updated', { type: 'info' });
    }

    resetForm() {
        this.state.newTask = {
            title: '',
            description: '',
            due_date: '',
            status: 'pending'
        };
        this.state.showForm = false;
        this.state.editingTask = null;
    }

    // Sync with Backend
    async syncWithBackend() {
        try {
            const result = await this.rpc('/todo_list/sync', {
                tasks: this.state.tasks
            });

            if (result.success) {
                this.notification.add(
                    `Sync successful! ${result.created_count} tasks created in backend.`,
                    { type: 'success' }
                );
                // Clear local storage after successful sync
                this.state.tasks = [];
                localStorage.removeItem('odoo_todo_tasks');
            } else {
                this.notification.add(`Sync failed: ${result.error}`, { type: 'danger' });
            }
        } catch (error) {
            console.error('Sync error:', error);
            this.notification.add('Sync failed: Network error', { type: 'danger' });
        }
    }

    async loadFromBackend() {
        try {
            const result = await this.rpc('/todo_list/get_tasks', {});

            if (result.success) {
                this.state.tasks = result.tasks.map(task => ({
                    ...task,
                    id: `backend_${task.id}` // Prefix to distinguish from local IDs
                }));
                this.saveLocalTasks();
                this.notification.add('Tasks loaded from backend', { type: 'success' });
            } else {
                this.notification.add(`Load failed: ${result.error}`, { type: 'danger' });
            }
        } catch (error) {
            console.error('Load error:', error);
            this.notification.add('Load failed: Network error', { type: 'danger' });
        }
    }

    // UI Helpers
    formatDate(dateStr) {
        if (!dateStr) return '';
        return new Date(dateStr).toLocaleDateString();
    }

    isOverdue(task) {
        if (!task.due_date || task.status === 'completed') return false;
        return new Date(task.due_date) < new Date();
    }

    get pendingTasks() {
        return this.state.tasks.filter(task => task.status === 'pending');
    }

    get completedTasks() {
        return this.state.tasks.filter(task => task.status === 'completed');
    }
}

registry.category("actions").add("todo_list_client", TodoListClient);