from flask import Flask, render_template, request, redirect
import sqlite3 as sql

app = Flask(__name__)

conn = sql.connect('jobs.db')


@app.route('/')
def index():

	curs = conn.cursor()
	jobs = curs.execute('SELECT * from jobs');
	jobs = list(jobs)
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
		with c
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

