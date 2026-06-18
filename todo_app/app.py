from flask import Flask, render_template, request, redirect
import json
import os
import time
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
            'id': int(time.time() * 1000),
            'text': new_task,
            'date': datetime.now().strftime('%Y-%m-%d'),
            'done': False,
            'priority': priority
        }
        tasks.append(task)
        save_tasks(tasks)

    return redirect('/')


@app.route('/toggle/<int:task_id>')
def toggle_task(task_id):
    for task in tasks:
        if task.get('id') == task_id:
            task['done'] = not task['done']
            save_tasks(tasks)
            break
    return redirect(request.referrer or '/')


@app.route('/delete/<int:task_id>')
def delete_task(task_id):
    for i, task in enumerate(tasks):
        if task.get('id') == task_id:
            tasks.pop(i)
            save_tasks(tasks)
            break
    return redirect('/')


@app.route('/clear')
def clear_tasks():
    tasks.clear()
    save_tasks(tasks)
    return redirect('/')


@app.route('/search')
def search():
    query = request.args.get('q', '').strip().lower()
    if query:
        filtered_tasks = [task for task in tasks if query in task['text'].lower()]
    else:
        filtered_tasks = tasks
    return render_template('index.html', tasks=filtered_tasks, search_query=query, filter_mode='all')


@app.route('/sort/date')
def sort_by_date():
    sorted_tasks = sorted(tasks, key=lambda t: t.get('date', ''), reverse=True)
    return render_template('index.html', tasks=sorted_tasks, filter_mode='all')


@app.route('/sort/status')
def sort_by_status():
    sorted_tasks = sorted(tasks, key=lambda t: t.get('done', False))
    return render_template('index.html', tasks=sorted_tasks, filter_mode='all')


@app.route('/sort/priority')
def sort_by_priority():
    priority_order = {'высокий': 1, 'средний': 2, 'низкий': 3}
    sorted_tasks = sorted(
        tasks,
        key=lambda t: priority_order.get(t.get('priority', 'средний'), 2)
    )
    return render_template('index.html', tasks=sorted_tasks, filter_mode='all')


@app.route('/sort/alpha')
def sort_by_alpha():
    sorted_tasks = sorted(tasks, key=lambda t: t.get('text', '').lower())
    return render_template('index.html', tasks=sorted_tasks, filter_mode='all')


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
    task = None
    for t in tasks:
        if t.get('id') == task_id:
            task = t
            break

    if not task:
        return "Задача не найдена", 404

    if request.method == 'POST':
        new_text = request.form.get('task', '').strip()
        new_priority = request.form.get('priority', 'средний')

        if new_text == '':
            return render_template('edit.html', task=task, message="Текст не может быть пустым!")

        task['text'] = new_text
        task['priority'] = new_priority
        save_tasks(tasks)
        return redirect('/')

    return render_template('edit.html', task=task)


if __name__ == '__main__':
    app.run(debug=True)