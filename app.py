from flask import Flask, render_template, request
import sqlite3 as sql
app = Flask(__name__)

conn = sql.connect('jobs.db')

@app.route('/')
def index():
	curs = conn.cursor()
	jobs = curs.execute('SELECT * from jobs');
	jobs = list(jobs)
	return render_template('index.html', jobs=jobs)

@app.route('/jobs', methods=['GET', 'POST'])
def jobs():
	if request.method == "POST":
		comp = request.form['company']
		url = request.form['url']
		status = request.form['status']

		c = conn.cursor()
		q = c.execute('INSERT INTO jobs (company, url, status) VALUES (?,?,?)', (comp, url, status))
		conn.commit()
		c.close()


	return render_template('index.html')