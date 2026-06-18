from flask import Flask, render_template, request, redirect
import json
import os
from datetime import datetime

app = Flask(__name__)

FILE_NAME = 'tasks.json'


def load_tasks():
    if os.path.exists(FILE_NAME):
        with open(FILE_NAME, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []


def save_tasks(tasks):
    with open(FILE_NAME, 'w', encoding='utf-8') as f:
        json.dump(tasks, f, ensure_ascii=False, indent=2)


tasks = load_tasks()


@app.route('/')
def index():
    return render_template('index.html', tasks=tasks, filter_mode='all')


@app.route('/add', methods=['POST'])
def add_task():
    new_task = request.form.get('task')
    priority = request.form.get('priority', 'средний')

    if new_task:
        task = {
            'text': new_task,
            'date': datetime.now().strftime('%d.%m.%Y %H:%M'),
            'done': False,
            'priority': priority
        }
        tasks.append(task)
        save_tasks(tasks)

    return redirect('/')


@app.route('/toggle/<int:task_id>')
def toggle_task(task_id):
    if 0 <= task_id < len(tasks):
        tasks[task_id]['done'] = not tasks[task_id]['done']
        save_tasks(tasks)
    return redirect(request.referrer or '/')


@app.route('/delete/<int:task_id>')
def delete_task(task_id):
    if 0 <= task_id < len(tasks):
        tasks.pop(task_id)
        save_tasks(tasks)
    return redirect('/')


@app.route('/clear')
def clear_tasks():
    tasks.clear()
    save_tasks(tasks)
    return redirect('/')


@app.route('/by_priority')
def by_priority():
    priority_order = {'высокий': 3, 'средний': 2, 'низкий': 1}
    sorted_tasks = sorted(
        tasks,
        key=lambda task: priority_order.get(task.get('priority', 'средний'), 2),
        reverse=True
    )
    return render_template('index.html', tasks=sorted_tasks, filter_mode='all')


@app.route('/by_priority_active')
def by_priority_active():
    priority_order = {'высокий': 3, 'средний': 2, 'низкий': 1}
    active_tasks = [t for t in tasks if not t.get('done', False)]
    sorted_active = sorted(
        active_tasks,
        key=lambda task: priority_order.get(task.get('priority', 'средний'), 2),
        reverse=True
    )
    return render_template('index.html', tasks=sorted_active, filter_mode='active')


@app.route('/active')
def active_tasks():
    return render_template('index.html', tasks=tasks, filter_mode='active')


@app.route('/completed')
def completed_tasks():
    return render_template('index.html', tasks=tasks, filter_mode='completed')


@app.route('/toggle_all/<string:action>')
def toggle_all(action):
    for task in tasks:
        if action == 'complete':
            task['done'] = True
        elif action == 'clear':
            task['done'] = False
    save_tasks(tasks)
    return redirect('/')


@app.route('/edit/<int:task_id>', methods=['GET', 'POST'])
def edit_task(task_id):
    if task_id < 0 or task_id >= len(tasks):
        return "Задача не найдена", 404

    task = tasks[task_id]

    if request.method == 'POST':
        new_text = request.form.get('task', '').strip()
        new_priority = request.form.get('priority', 'средний')
        
        old_text = task['text']
        old_priority = task.get('priority', 'средний')

        if new_text == '':
            return render_template('edit.html', task=task, message="Текст не может быть пустым!")

        if new_text == old_text and new_priority == old_priority:
            return render_template('edit.html', task=task, message="Ничего не изменено")

        task['text'] = new_text
        task['priority'] = new_priority
        save_tasks(tasks)
        return redirect('/')

    return render_template('edit.html', task=task)


if __name__ == '__main__':
    app.run(debug=True)