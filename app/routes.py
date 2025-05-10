from flask import request, jsonify, render_template


def register_routes(app):
    from app.database import db
    from app.models import Task

    @app.route('/')
    def index():
        tasks = Task.query.all()
        return render_template('index.html', tasks=tasks)

    @app.route('/tasks', methods=['POST'])
    def create_task():
        data = request.form if request.form else request.get_json()
        task = Task(title=data.get('title'), description=data.get('description'))
        db.session.add(task)
        db.session.commit()
        
        if request.headers.get('HX-Request'):
            return render_template('_task.html', task=task)
        return jsonify({
            'id': task.id,
            'title': task.title,
            'description': task.description,
            'done': task.done
        }), 201

    @app.route('/tasks', methods=['GET'])
    def get_tasks():
        tasks = Task.query.all()
        if request.headers.get('HX-Request'):
            return render_template('_task.html', task=task)
        return jsonify([
            {
                'id': t.id,
                'title': t.title,
                'description': t.description,
                'done': t.done
            } for t in tasks
        ])

    @app.route('/tasks/<int:task_id>', methods=['GET'])
    def get_task(task_id):
        task = Task.query.get(task_id)
        if not task:
            return jsonify({'error': 'Task not found'}), 404
        if request.headers.get('HX-Request'):
            return render_template('_task.html', task=task)
        return jsonify({
            'id': task.id,
            'title': task.title,
            'description': task.description,
            'done': task.done
        })

    @app.route('/tasks/<int:task_id>', methods=['PUT'])
    def update_task(task_id):
        task = Task.query.get(task_id)
        if not task:
            return jsonify({'error': 'Task not found'}), 404
        data = request.form if request.form else request.get_json()
        task.title = data.get('title', task.title)
        task.description = data.get('description', task.description)
        task.done = not task.done if 'done' in data else task.done
        db.session.commit()
        
        if request.headers.get('HX-Request'):
            return render_template('_task.html', task=task)
        return jsonify({
            'id': task.id,
            'title': task.title,
            'description': task.description,
            'done': task.done
        })

    @app.route('/tasks/<int:task_id>', methods=['DELETE'])
    def delete_task(task_id):
        task = Task.query.get(task_id)
        if not task:
            return jsonify({'error': 'Task not found'}), 404
        db.session.delete(task)
        db.session.commit()
        
        if request.headers.get('HX-Request'):
            return ''
        return jsonify({'message': 'Task deleted'})
