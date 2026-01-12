import unittest
import json
from app import app, TaskManager

class TestTaskManager(unittest.TestCase):
    def setUp(self):
        self.manager = TaskManager()
    
    def test_add_task(self):
        task = self.manager.add_task("Тестове завдання", "Опис")
        self.assertEqual(task['title'], "Тестове завдання")
        self.assertEqual(task['description'], "Опис")
        self.assertFalse(task['completed'])
        self.assertEqual(task['id'], 1)
    
    def test_get_all_tasks(self):
        self.manager.add_task("Завдання 1")
        self.manager.add_task("Завдання 2")
        tasks = self.manager.get_all_tasks()
        self.assertEqual(len(tasks), 2)
    
    def test_get_task(self):
        task = self.manager.add_task("Завдання")
        retrieved = self.manager.get_task(task['id'])
        self.assertEqual(retrieved['title'], "Завдання")
    
    def test_get_nonexistent_task(self):
        result = self.manager.get_task(999)
        self.assertIsNone(result)
    
    def test_update_task(self):
        task = self.manager.add_task("Завдання")
        updated = self.manager.update_task(task['id'], completed=True)
        self.assertTrue(updated['completed'])
    
    def test_delete_task(self):
        task = self.manager.add_task("Завдання")
        result = self.manager.delete_task(task['id'])
        self.assertTrue(result)
        self.assertEqual(len(self.manager.get_all_tasks()), 0)
    
    def test_delete_nonexistent_task(self):
        result = self.manager.delete_task(999)
        self.assertFalse(result)
    
    def test_statistics_empty(self):
        stats = self.manager.get_statistics()
        self.assertEqual(stats['total'], 0)
        self.assertEqual(stats['completed'], 0)
        self.assertEqual(stats['pending'], 0)
        self.assertEqual(stats['completion_rate'], 0)
    
    def test_statistics_with_tasks(self):
        self.manager.add_task("Завдання 1")
        task2 = self.manager.add_task("Завдання 2")
        self.manager.update_task(task2['id'], completed=True)
        
        stats = self.manager.get_statistics()
        self.assertEqual(stats['total'], 2)
        self.assertEqual(stats['completed'], 1)
        self.assertEqual(stats['pending'], 1)
        self.assertEqual(stats['completion_rate'], 50.0)

class TestAPIEndpoints(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
    
    def test_index_route(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'<!DOCTYPE html>', response.data)
    
    def test_health_check(self):
        response = self.app.get('/health')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'healthy')
    
    def test_get_tasks_empty(self):
        response = self.app.get('/api/tasks')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIsInstance(data, list)
    
    def test_create_task(self):
        response = self.app.post('/api/tasks',
            data=json.dumps({'title': 'Нове завдання', 'description': 'Опис'}),
            content_type='application/json')
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data['title'], 'Нове завдання')
    
    def test_get_task(self):
        create_response = self.app.post('/api/tasks',
            data=json.dumps({'title': 'Завдання'}),
            content_type='application/json')
        task = json.loads(create_response.data)
        
        response = self.app.get(f'/api/tasks/{task["id"]}')
        self.assertEqual(response.status_code, 200)
    
    def test_get_nonexistent_task(self):
        response = self.app.get('/api/tasks/999')
        self.assertEqual(response.status_code, 404)
    
    def test_update_task(self):
        create_response = self.app.post('/api/tasks',
            data=json.dumps({'title': 'Завдання'}),
            content_type='application/json')
        task = json.loads(create_response.data)
        
        response = self.app.put(f'/api/tasks/{task["id"]}',
            data=json.dumps({'completed': True}),
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['completed'])
    
    def test_delete_task(self):
        create_response = self.app.post('/api/tasks',
            data=json.dumps({'title': 'Завдання'}),
            content_type='application/json')
        task = json.loads(create_response.data)
        
        response = self.app.delete(f'/api/tasks/{task["id"]}')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
    
    def test_get_statistics(self):
        response = self.app.get('/api/stats')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('total', data)
        self.assertIn('completed', data)
        self.assertIn('pending', data)
        self.assertIn('completion_rate', data)

if __name__ == '__main__':
    unittest.main()