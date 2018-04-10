from flask import Flask, render_template, request, redirect
import sqlite3 as sql

app = Flask(__name__)

conn = sql.connect('jobs.db')


@app.route('/')
def index():
	'''Render index page'''
	curs = conn.cursor()
	jobs = curs.execute('SELECT * from jobs ORDER BY timestamp');
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
		q = c.execute(sql, values)
		conn.commit()
		c.close()


	return redirect('/')


@app.route('/jobs/<job_id>/edit', methods=("GET", "POST"))
def edit_job(job_id):
	'''Get and post to edit page of specific jobs'''
	c = conn.cursor()
	# Render edit page for get requests
	if request.method == "GET":
		job = c.execute('SELECT * FROM jobs WHERE job_id=?', (job_id,))
		job = list(job)[0]
		c.close()
		return render_template('index.html', current_job=job)
	# Update job entry with new values and redirect to home page
	else:
		sql = '''
			UPDATE 
				jobs 
			SET 
				company=?, url=?, status=?, notes=?
			WHERE 
				job_id=?
		'''
		values = (
			request.form['company'],
			request.form['url'], 
			request.form['status'],
			request.form['notes'],
			job_id,
		)
		c.execute(sql, values)
		# Check for status change and add row in db if necessary
		prev_status = request.form['prev-status'] # hidden value in form
		status = request.form['status']
		if prev_status != status:
			status_sql = '''
				INSERT INTO
					status_changes(job_id, to_status, from_status)
				VALUES
					(?,?,?)
			'''
			status_values = (job_id, request.form['status'], prev_status)
			c.execute(status_sql, status_values)
		conn.commit()
		c.close()
		return redirect('/')

