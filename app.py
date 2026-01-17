from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

# Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Task Model (Database Schema)
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(50), nullable=False) # Work, Personal, Study
    priority = db.Column(db.String(20), nullable=False) # High, Medium, Low
    due_date = db.Column(db.String(10)) # YYYY-MM-DD
    completed = db.Column(db.Boolean, default=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

# Initialize Database
with app.app_context():
    db.create_all()

@app.route('/', methods=['GET', 'POST'])
def index():
    search_query = request.args.get('search', '')
    filter_category = request.args.get('category', 'All')

    # Base Query
    query = Task.query

    # Backend Search Logic
    if search_query:
        query = query.filter(Task.title.contains(search_query))
    
    # Backend Categorization Logic
    if filter_category != 'All':
        query = query.filter_by(category=filter_category)

    # Priority Sorting Logic (High -> Medium -> Low)
    # Custom sorting using a case statement or simple ordering
    tasks = query.order_by(Task.completed.asc(), Task.priority.asc()).all()
    
    return render_template('index.html', tasks=tasks, search_query=search_query)

@app.route('/add', methods=['POST'])
def add_task():
    new_task = Task(
        title=request.form['title'],
        category=request.form['category'],
        priority=request.form['priority'],
        due_date=request.form['due_date'],
        completed=False
    )
    db.session.add(new_task)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/update/<int:id>')
def update_task(id):
    task = Task.query.get_or_404(id)
    task.completed = not task.completed
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/delete/<int:id>')
def delete_task(id):
    task = Task.query.get_or_404(id)
    db.session.delete(task)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/priority')
def priority_page():
    high_tasks = Task.query.filter_by(priority='High').all()
    med_tasks = Task.query.filter_by(priority='Medium').all()
    low_tasks = Task.query.filter_by(priority='Low').all()

    return render_template('priority.html', high=high_tasks, medium=med_tasks, low=low_tasks)

@app.route('/categories')
def categories_page():
    work_tasks = Task.query.filter_by(category='Work').all()
    study_tasks = Task.query.filter_by(category='Study').all()
    personal_tasks = Task.query.filter_by(category='Personal').all()
    return render_template('categories.html', work=work_tasks, study=study_tasks, personal=personal_tasks)

@app.route('/dates')
def dates_page():
    # Saare tasks ko date ke hisab se sort karke dikhayega
    all_tasks = Task.query.order_by(Task.due_date.asc()).all()
    return render_template('dates.html', tasks=all_tasks)

if __name__ == "__main__":
    app.run(debug=True)