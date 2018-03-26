from flask import Flask, render_template, request, redirect
import sqlite3 as sql
from celery import Celery

app = Flask(__name__)
app.config.update(
    CELERY_BROKER_URL='redis://localhost:6379',
    CELERY_RESULT_BACKEND='redis://localhost:6379'
)


def make_celery(app):
    celery = Celery(app.import_name, backend=app.config['CELERY_RESULT_BACKEND'],
                    broker=app.config['CELERY_BROKER_URL'])
    celery.conf.update(app.config)
    TaskBase = celery.Task
    class ContextTask(TaskBase):
        abstract = True
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)
    celery.Task = ContextTask
    return celery
celery = make_celery(app)
conn = sql.connect('jobs.db')

@celery.task()
def test(a,b):
    print b
    return a


@app.route('/')
def index():

    curs = conn.cursor()
    jobs = curs.execute('SELECT * from jobs')
    a = test.delay("a", "B")
    print a
    jobs = list(jobs)
    x = a.wait()
    print x
    return render_template('index.html', jobs=jobs)


@app.route('/jobs', methods=['GET', 'POST', 'PUT', 'PATCH'])
def jobs():

    if request.method == "POST":
        comp = request.form['company']
        url = request.form['url']
        status = request.form['status']

        sql = '''
				INSERT INTO 
					jobs (company, url, status) 
				VALUES 
					(?,?,?)
			'''
        values = (comp, url, status)
        c = conn.cursor()
        q = c.execute(sql, values)
        conn.commit()
        c.close()

    return redirect('/')


@app.route('/jobs/<job_id>/edit', methods=("GET", "POST"))
def edit_job(job_id):

    c = conn.cursor()
    if request.method == "GET":
        job = c.execute('SELECT * FROM jobs WHERE job_id=?', job_id)
        job = list(job)[0]
        c.close()
        return render_template('index.html', current_job=job)
    else:
        sql = '''
				UPDATE 
					jobs 
				SET 
					company=?, url=?, status=? 
				WHERE 
					job_id=?
			'''
        values = (
            request.form['company'],
            request.form['url'],
            request.form['status'],
            job_id,
        )
        c.execute(sql, values)
        conn.commit()
        c.close()
        return redirect('/')
