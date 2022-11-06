from flask import Flask, render_template, request, redirect, url_for, session 
import ibm_db
import re
app = Flask( __name__) 

app.secret_key = 'a'
conn = ibm_db.connect("DATABASE=bludb;HOSTNAME=b0aebb68-94fa-46ec-a1fc-1c999edb6187.c3n41cmd0nqnrk39u98g.databases.appdomain.cloud;PORT=31249;Security= SSL;SSLServerCertificate=DigiCertGlobalRootCA.crt;UID=xhn44043;PWD=q8X1bG8CN5Uk7nAb;",'','')

@app.route('/')
@app.route('/login', methods =['GET', 'POST']) 
def login():
   msg = ''
   if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
      username = request.form['username'] 
      password = request.form['password']
      stmt = ibm_db.prepare(conn,'SELECT * FROM user WHERE username = ? AND password = ?')
      ibm_db.bind_param(stmt,1,username) 
      ibm_db.bind_param(stmt,2,password) 
      ibm_db.execute(stmt)
      account = ibm_db.fetch_assoc(stmt) 
      if account:
         session['loggedin'] = True
         session['username'] = account['USERNAME'] 
         msg = 'Logged in successfully !'
         return render_template('index.html', msg = msg) 
      else:
         msg = 'Incorrect username / password !'
   return render_template('login.html', msg = msg)

@app.route('/logout') 
def logout():
  session.pop('loggedin', None) 
  session.pop('id', None) 
  session.pop('username', None) 
  return redirect(url_for('login'))

@app.route('/register', methods =['GET', 'POST']) 
def register():
   msg = ''
   if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form :
      username = request.form['username'] 
      password = request.form['password'] 
      email = request.form['email']
      stmt = ibm_db.prepare(conn,'SELECT * FROM user WHERE username = ?') 
      ibm_db.bind_param(stmt,1,username)
      ibm_db.execute(stmt)
      account = ibm_db.fetch_assoc(stmt) 
      if account:
         msg = 'Account already exists !'
      elif not re.match(r'[^@]+@[^@]+\.[^@]+', email): 
            msg = 'Invalid email address !'
      elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers !' 
      elif not username or not password or not email:
         msg = 'Please fill out the form !' 
      else:
         prep_stmt = ibm_db.prepare(conn,"INSERT INTO user VALUES(?, ?, ?)")
         ibm_db.bind_param(prep_stmt, 1, username)
         ibm_db.bind_param(prep_stmt, 2, email)
         ibm_db.bind_param(prep_stmt, 3, password) 
         ibm_db.execute(prep_stmt)
         msg = 'You have successfully registered !' 
   elif request.method == 'POST':
      msg = 'Please fill out the form !'
   return render_template('register.html', msg = msg)

if __name__ == '__main__': 
   app.debug = True 
   app.run(host='0.0.0.0',port=8080)
