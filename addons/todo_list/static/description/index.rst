# Todo List Module

A simple to-do list application for Odoo that provides both backend storage and local storage functionality.

## Features

- **Backend Tasks**: Full Odoo integration with database storage
- **Local Storage Interface**: Client-side task management with browser persistence
- **Sync Functionality**: Push local tasks to Odoo backend
- **User Security**: Users can only see their own tasks
- **Task Management**: Add, edit, complete, and delete tasks
- **Due Date Tracking**: Set and track task due dates

## Usage

1. Install the module
2. Navigate to the Todo List menu
3. Use "Backend Tasks" for server-side task management
4. Use "Local Storage Interface" for offline task management
5. Use the sync button to push local tasks to the backend

## Technical Details

- Model: `todo.task` with fields: title, description, status, due_date, user_id
- Controllers: `/todo_list/sync` and `/todo_list/get_tasks` for API access
- JavaScript: LocalStorage-powered interface with OWL components
- Security: Record rules ensure users only access their own tasks