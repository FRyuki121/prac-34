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
    # Передаем обычный список задач и режим фильтрации 'all'
    return render_template('index.html', tasks=tasks, filter_mode='all')


@app.route('/add', methods=['POST'])
def add_task():
    new_task = request.form['task']

    if new_task:
        # Модифицированная структура: добавлено поле 'done': False 
        task = {
            'text': new_task,
            'date': datetime.now().strftime('%d.%m.%Y %H:%M'),
            'done': False
        }

        tasks.append(task)
        save_tasks(tasks)

    return redirect('/')


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


@app.route('/edit/<int:task_id>', methods=['GET', 'POST'])
def edit_task(task_id):
    if task_id < 0 or task_id >= len(tasks):
        return "Задача не найдена", 404

    task = tasks[task_id]

    if request.method == 'POST':
        new_text = request.form.get('task', '').strip()
        old_text = task['text']

        if new_text == '':
            return render_template(
                'edit.html',
                task=task,
                message="Текст не может быть пустым!"
            )

        if new_text == old_text:
            return render_template(
                'edit.html',
                task=task,
                message="Ничего не изменено"
            )

        task['text'] = new_text
        save_tasks(tasks)
        return redirect('/')

    return render_template('edit.html', task=task)


# ==========================================
# НОВЫЙ КОД ПРАКТИКИ И САМОСТОЯТЕЛЬНОЙ РАБОТЫ
# ==========================================

@app.route('/toggle/<int:task_id>')
def toggle_task(task_id):
    """Переключение статуса выполнения конкретной задачи [cite: 49, 50]"""
    if 0 <= task_id < len(tasks):
        # Меняем True на False и наоборот [cite: 54]
        tasks[task_id]['done'] = not tasks[task_id]['done']
        save_tasks(tasks)git add .
    return redirect(request.referrer or '/')


@app.route('/active')
def active_tasks():
    """Самостоятельная работа: Показ только активных задач [cite: 144]"""
    return render_template('index.html', tasks=tasks, filter_mode='active')


@app.route('/completed')
def completed_tasks():
    """Самостоятельная работа: Показ только выполненных задач [cite: 145]"""
    return render_template('index.html', tasks=tasks, filter_mode='completed')


@app.route('/toggle_all/<string:action>')
def toggle_all(action):
    """Самостоятельная работа: Выполнить все / Отменить все [cite: 146, 147]"""
    for task in tasks:
        if action == 'complete':
            task['done'] = True  # Выполнить все 
        elif action == 'clear':
            task['done'] = False # Отменить все 
    save_tasks(tasks)
    return redirect('/')


if __name__ == '__main__':
    app.run(debug=True)