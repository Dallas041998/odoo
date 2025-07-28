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

// Template for the component
TodoListClient.template = `
<div class="todo-list-client">
    <div class="row">
        <div class="col-12">
            <div class="card">
                <div class="card-header d-flex justify-content-between align-items-center">
                    <h3>Todo List (Local Storage)</h3>
                    <div>
                        <button class="btn btn-primary me-2" t-on-click="() => this.state.showForm = !this.state.showForm">
                            Add Task
                        </button>
                        <button class="btn btn-success me-2" t-on-click="syncWithBackend">
                            Sync to Backend
                        </button>
                        <button class="btn btn-info" t-on-click="loadFromBackend">
                            Load from Backend
                        </button>
                    </div>
                </div>
                <div class="card-body">
                    <!-- Task Form -->
                    <div t-if="state.showForm" class="card mb-3">
                        <div class="card-header">
                            <h5 t-if="state.editingTask">Edit Task</h5>
                            <h5 t-else="">Add New Task</h5>
                        </div>
                        <div class="card-body">
                            <div class="row">
                                <div class="col-md-6">
                                    <div class="mb-3">
                                        <label class="form-label">Title *</label>
                                        <input type="text" class="form-control" 
                                               t-model="state.newTask.title" 
                                               placeholder="Enter task title"/>
                                    </div>
                                </div>
                                <div class="col-md-6">
                                    <div class="mb-3">
                                        <label class="form-label">Due Date</label>
                                        <input type="date" class="form-control" 
                                               t-model="state.newTask.due_date"/>
                                    </div>
                                </div>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Description</label>
                                <textarea class="form-control" rows="3" 
                                          t-model="state.newTask.description" 
                                          placeholder="Enter task description"/>
                            </div>
                            <div class="d-flex gap-2">
                                <button class="btn btn-primary" 
                                        t-on-click="state.editingTask ? updateTask : addTask">
                                    <span t-if="state.editingTask">Update Task</span>
                                    <span t-else="">Add Task</span>
                                </button>
                                <button class="btn btn-secondary" t-on-click="resetForm">
                                    Cancel
                                </button>
                            </div>
                        </div>
                    </div>

                    <!-- Task Statistics -->
                    <div class="row mb-3">
                        <div class="col-md-4">
                            <div class="card bg-primary text-white">
                                <div class="card-body text-center">
                                    <h4 t-esc="state.tasks.length"/>
                                    <small>Total Tasks</small>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-4">
                            <div class="card bg-warning text-white">
                                <div class="card-body text-center">
                                    <h4 t-esc="pendingTasks.length"/>
                                    <small>Pending Tasks</small>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-4">
                            <div class="card bg-success text-white">
                                <div class="card-body text-center">
                                    <h4 t-esc="completedTasks.length"/>
                                    <small>Completed Tasks</small>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Tasks List -->
                    <div class="row">
                        <!-- Pending Tasks -->
                        <div class="col-md-6">
                            <h5>Pending Tasks</h5>
                            <div t-if="pendingTasks.length === 0" class="alert alert-info">
                                No pending tasks
                            </div>
                            <div t-else="" class="todo-tasks">
                                <div t-foreach="pendingTasks" t-as="task" t-key="task.id" 
                                     class="card mb-2" 
                                     t-att-class="isOverdue(task) ? 'border-danger' : ''">
                                    <div class="card-body">
                                        <div class="d-flex justify-content-between">
                                            <h6 t-esc="task.title" t-att-class="isOverdue(task) ? 'text-danger' : ''"/>
                                            <div class="btn-group btn-group-sm">
                                                <button class="btn btn-success" 
                                                        t-on-click="() => this.toggleTaskStatus(task)"
                                                        title="Mark as completed">
                                                    ✓
                                                </button>
                                                <button class="btn btn-primary" 
                                                        t-on-click="() => this.editTask(task)"
                                                        title="Edit task">
                                                    ✎
                                                </button>
                                                <button class="btn btn-danger" 
                                                        t-on-click="() => this.deleteTask(task)"
                                                        title="Delete task">
                                                    ×
                                                </button>
                                            </div>
                                        </div>
                                        <p t-if="task.description" class="text-muted small mb-1" t-esc="task.description"/>
                                        <small t-if="task.due_date" 
                                               t-att-class="isOverdue(task) ? 'text-danger' : 'text-muted'">
                                            Due: <span t-esc="formatDate(task.due_date)"/>
                                        </small>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <!-- Completed Tasks -->
                        <div class="col-md-6">
                            <h5>Completed Tasks</h5>
                            <div t-if="completedTasks.length === 0" class="alert alert-info">
                                No completed tasks
                            </div>
                            <div t-else="" class="todo-tasks">
                                <div t-foreach="completedTasks" t-as="task" t-key="task.id" 
                                     class="card mb-2 bg-light">
                                    <div class="card-body">
                                        <div class="d-flex justify-content-between">
                                            <h6 class="text-decoration-line-through text-muted" t-esc="task.title"/>
                                            <div class="btn-group btn-group-sm">
                                                <button class="btn btn-warning" 
                                                        t-on-click="() => this.toggleTaskStatus(task)"
                                                        title="Mark as pending">
                                                    ↻
                                                </button>
                                                <button class="btn btn-danger" 
                                                        t-on-click="() => this.deleteTask(task)"
                                                        title="Delete task">
                                                    ×
                                                </button>
                                            </div>
                                        </div>
                                        <p t-if="task.description" class="text-muted small mb-1" t-esc="task.description"/>
                                        <small t-if="task.due_date" class="text-muted">
                                            Due: <span t-esc="formatDate(task.due_date)"/>
                                        </small>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
`;

registry.category("actions").add("todo_list_client", TodoListClient);