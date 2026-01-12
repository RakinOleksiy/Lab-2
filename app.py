from flask import Flask, jsonify, request, render_template_string
from datetime import datetime
import json

app = Flask(__name__)

class TaskManager:
    def __init__(self):
        self.tasks = []
        self.next_id = 1
    
    def add_task(self, title, description=""):
        task = {
            'id': self.next_id,
            'title': title,
            'description': description,
            'completed': False,
            'created_at': datetime.now().isoformat()
        }
        self.tasks.append(task)
        self.next_id += 1
        return task
    
    def get_all_tasks(self):
        return self.tasks
    
    def get_task(self, task_id):
        return next((t for t in self.tasks if t['id'] == task_id), None)
    
    def update_task(self, task_id, **kwargs):
        task = self.get_task(task_id)
        if task:
            task.update(kwargs)
            return task
        return None
    
    def delete_task(self, task_id):
        task = self.get_task(task_id)
        if task:
            self.tasks.remove(task)
            return True
        return False
    
    def get_statistics(self):
        total = len(self.tasks)
        completed = sum(1 for t in self.tasks if t['completed'])
        return {
            'total': total,
            'completed': completed,
            'pending': total - completed,
            'completion_rate': round(completed / total * 100, 2) if total > 0 else 0
        }

manager = TaskManager()

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="uk">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Менеджер Завдань - CI/CD Demo</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 900px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        .header h1 { font-size: 2.5em; margin-bottom: 10px; }
        .header p { opacity: 0.9; font-size: 1.1em; }
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            padding: 30px;
            background: #f8f9fa;
        }
        .stat-card {
            background: white;
            padding: 20px;
            border-radius: 15px;
            text-align: center;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .stat-card .number {
            font-size: 2.5em;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 5px;
        }
        .stat-card .label {
            color: #6c757d;
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        .content { padding: 30px; }
        .form-group {
            background: #f8f9fa;
            padding: 25px;
            border-radius: 15px;
            margin-bottom: 30px;
        }
        .form-row {
            display: flex;
            gap: 15px;
            margin-bottom: 15px;
        }
        input[type="text"], textarea {
            flex: 1;
            padding: 12px;
            border: 2px solid #e9ecef;
            border-radius: 10px;
            font-size: 1em;
            transition: border-color 0.3s;
        }
        input[type="text"]:focus, textarea:focus {
            outline: none;
            border-color: #667eea;
        }
        textarea { resize: vertical; min-height: 60px; }
        button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 12px 30px;
            border-radius: 10px;
            font-size: 1em;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }
        .tasks-list { display: flex; flex-direction: column; gap: 15px; }
        .task-item {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 15px;
            display: flex;
            align-items: center;
            gap: 15px;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        .task-item:hover {
            transform: translateX(5px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
        .task-item.completed {
            opacity: 0.6;
            background: #e9ecef;
        }
        .task-checkbox {
            width: 24px;
            height: 24px;
            cursor: pointer;
        }
        .task-content {
            flex: 1;
        }
        .task-title {
            font-size: 1.2em;
            font-weight: 600;
            margin-bottom: 5px;
            color: #212529;
        }
        .task-description {
            color: #6c757d;
            font-size: 0.9em;
        }
        .task-meta {
            font-size: 0.8em;
            color: #adb5bd;
            margin-top: 5px;
        }
        .task-actions {
            display: flex;
            gap: 10px;
        }
        .btn-delete {
            background: #dc3545;
            padding: 8px 20px;
            font-size: 0.9em;
        }
        .btn-delete:hover {
            box-shadow: 0 5px 15px rgba(220, 53, 69, 0.4);
        }
        .empty-state {
            text-align: center;
            padding: 60px 20px;
            color: #6c757d;
        }
        .empty-state img {
            width: 200px;
            opacity: 0.5;
            margin-bottom: 20px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📋 Менеджер Завдань</h1>
            <p>CI/CD Pipeline Demo Project</p>
        </div>
        
        <div class="stats">
            <div class="stat-card">
                <div class="number" id="total-tasks">0</div>
                <div class="label">Всього завдань</div>
            </div>
            <div class="stat-card">
                <div class="number" id="completed-tasks">0</div>
                <div class="label">Виконано</div>
            </div>
            <div class="stat-card">
                <div class="number" id="pending-tasks">0</div>
                <div class="label">В роботі</div>
            </div>
            <div class="stat-card">
                <div class="number" id="completion-rate">0%</div>
                <div class="label">Прогрес</div>
            </div>
        </div>
        
        <div class="content">
            <div class="form-group">
                <div class="form-row">
                    <input type="text" id="task-title" placeholder="Назва завдання..." />
                </div>
                <div class="form-row">
                    <textarea id="task-description" placeholder="Опис завдання (необов'язково)..."></textarea>
                </div>
                <div class="form-row">
                    <button onclick="addTask()">➕ Додати завдання</button>
                </div>
            </div>
            
            <div class="tasks-list" id="tasks-list"></div>
        </div>
    </div>
    
    <script>
        async function loadTasks() {
            const response = await fetch('/api/tasks');
            const tasks = await response.json();
            renderTasks(tasks);
            await loadStats();
        }
        
        async function loadStats() {
            const response = await fetch('/api/stats');
            const stats = await response.json();
            document.getElementById('total-tasks').textContent = stats.total;
            document.getElementById('completed-tasks').textContent = stats.completed;
            document.getElementById('pending-tasks').textContent = stats.pending;
            document.getElementById('completion-rate').textContent = stats.completion_rate + '%';
        }
        
        function renderTasks(tasks) {
            const container = document.getElementById('tasks-list');
            if (tasks.length === 0) {
                container.innerHTML = `
                    <div class="empty-state">
                        <div style="font-size: 4em;">📝</div>
                        <h3>Немає завдань</h3>
                        <p>Додайте своє перше завдання вище</p>
                    </div>
                `;
                return;
            }
            
            container.innerHTML = tasks.map(task => `
                <div class="task-item ${task.completed ? 'completed' : ''}">
                    <input type="checkbox" class="task-checkbox" 
                           ${task.completed ? 'checked' : ''} 
                           onchange="toggleTask(${task.id})">
                    <div class="task-content">
                        <div class="task-title">${task.title}</div>
                        ${task.description ? `<div class="task-description">${task.description}</div>` : ''}
                        <div class="task-meta">Створено: ${new Date(task.created_at).toLocaleString('uk-UA')}</div>
                    </div>
                    <div class="task-actions">
                        <button class="btn-delete" onclick="deleteTask(${task.id})">🗑️ Видалити</button>
                    </div>
                </div>
            `).join('');
        }
        
        async function addTask() {
            const title = document.getElementById('task-title').value.trim();
            const description = document.getElementById('task-description').value.trim();
            
            if (!title) {
                alert('Введіть назву завдання!');
                return;
            }
            
            await fetch('/api/tasks', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ title, description })
            });
            
            document.getElementById('task-title').value = '';
            document.getElementById('task-description').value = '';
            await loadTasks();
        }
        
        async function toggleTask(id) {
            const response = await fetch(`/api/tasks/${id}`);
            const task = await response.json();
            
            await fetch(`/api/tasks/${id}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ completed: !task.completed })
            });
            
            await loadTasks();
        }
        
        async function deleteTask(id) {
            if (confirm('Видалити це завдання?')) {
                await fetch(`/api/tasks/${id}`, { method: 'DELETE' });
                await loadTasks();
            }
        }
        
        loadTasks();
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    return jsonify(manager.get_all_tasks())

@app.route('/api/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    task = manager.get_task(task_id)
    if task:
        return jsonify(task)
    return jsonify({'error': 'Task not found'}), 404

@app.route('/api/tasks', methods=['POST'])
def create_task():
    data = request.get_json()
    task = manager.add_task(data['title'], data.get('description', ''))
    return jsonify(task), 201

@app.route('/api/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    data = request.get_json()
    task = manager.update_task(task_id, **data)
    if task:
        return jsonify(task)
    return jsonify({'error': 'Task not found'}), 404

@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    if manager.delete_task(task_id):
        return jsonify({'success': True})
    return jsonify({'error': 'Task not found'}), 404

@app.route('/api/stats', methods=['GET'])
def get_stats():
    return jsonify(manager.get_statistics())

@app.route('/health')
def health():
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)