from unicodedata import name
from flask import Flask, render_template, request, redirect, url_for, session
import ibm_db
from flask_mail import Mail, Message
import re

app = Flask(__name__)
mail = Mail(app)

# configuration of mail
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'skilljobrecommender@gmail.com'
app.config['MAIL_PASSWORD'] = 'xkoqxpgdvnxiyons'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)


app.secret_key='a'
conn = ibm_db.connect("DATABASE=bludb;HOSTNAME=6667d8e9-9d4d-4ccb-ba32-21da3bb5aafc.c1ogj3sd0tgtu0lqde00.databases.appdomain.cloud;PORT=30376;Security=SSL;SSLServerCertificate=DigiCertGlobalRootCA.crt;UID=ckm89634;PWD=ccjHLwxhkyX3XI3v;",'','')

@app.route('/')
def home():
    return render_template('/home.html')

@app.route('/registertemp',methods=["POST","GET"])
def registertemp():
    return render_template("register.html")

@app.route('/uploaddata',methods =['GET','POST'])
def register():
    msg = ''
    if request.method == 'POST':
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        skill1 = request.form['skill1']  
        skill2 =request.form['skill2']
        stmt = ibm_db.prepare(conn, 'SELECT * FROM userss WHERE username = ?')
        ibm_db.bind_param(stmt, 1, username)
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt) 
        if account:
            msg = 'Account already exists !'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address !'
        elif not re.match(r'^[A-Za-z0-9_.-]*$', username):
            msg = 'name must contain only characters and numbers !'
        else:
            prep_stmt = ibm_db.prepare(conn,'INSERT INTO userss(firstname, lastname, username, email, password,skill1,skill2 ) VALUES(?, ?, ?, ?, ?, ?,?)')
            ibm_db.bind_param(prep_stmt, 1, firstname)
            ibm_db.bind_param(prep_stmt, 2, lastname)
            ibm_db.bind_param(prep_stmt, 3, username)
            ibm_db.bind_param(prep_stmt, 4, email)
            ibm_db.bind_param(prep_stmt, 5, password)
            ibm_db.bind_param(prep_stmt, 6, skill1)
            ibm_db.bind_param(prep_stmt, 7, skill2)
            ibm_db.execute(prep_stmt)
            msg = 'Dear % s You have successfully registered!'%(username)
            msg1 = Message('Hello', sender = 'skilljobrecommender@gmail.com', recipients = [email])
            msg1.body = " Hello "+ username +", you have sucessfully registered your account in skill job recommender"
            mail.send(msg1)
        return render_template('register.html',a = msg,indicator="success")
    else:
        msg = 'Please fill the form!'
    return render_template('register.html',a = msg, indicator='failure')

@app.route('/jobs',methods=["POST","GET"])
def jobs():
    msg = ''
    if request.method == 'POST':
        company = request.form['company']
        website = request.form['website']
        position=request.form['position'] 
        skill1=request.form['skill1']
        skill2=request.form['skill2']   
        skill3=request.form['skill3']  
        stmt = ibm_db.prepare(conn,'INSERT INTO jobs(company,website,position,skill1,skill2,skill3) VALUES (?, ?, ?, ?, ?, ?)')
        ibm_db.bind_param(stmt, 1, company)
        ibm_db.bind_param(stmt, 2, website)
        ibm_db.bind_param(stmt, 3, position)
        ibm_db.bind_param(stmt, 4, skill1)
        ibm_db.bind_param(stmt, 5, skill2)
        ibm_db.bind_param(stmt, 6, skill3)
        ibm_db.execute(stmt)
        msg = 'data has been stored sucessfully'
        return render_template('jobs.html',a = msg)
    return render_template('jobs.html',a = msg)

@app.route('/login',methods=["POST","GET"])
def login():
    return render_template("login.html")

@app.route('/logindata',methods=["POST","GET"])
def logindata():
    global userid
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        stmt = ibm_db.prepare(conn,'SELECT * FROM userss WHERE username = ? AND password = ?')
        ibm_db.bind_param(stmt,1,username)
        ibm_db.bind_param(stmt,2,password)
        ibm_db.execute(stmt)
        account = ibm_db.fetch_tuple(stmt)
        if account:
            session['id'] = account[0]
            userid =  account[0]
            session['username'] = account[1]
            return redirect(url_for('dashboard'))
        else:
            msg = 'Incorrect username / password !'
            return render_template('login.html', b = msg, indicator="failure")

@app.route('/home')




def dashboard():
    if 'id' in session:
        uid = session['id']
        stmt = ibm_db.prepare(conn, 'SELECT * FROM userss WHERE id = ?')
        ibm_db.bind_param(stmt, 1, uid)
        ibm_db.execute(stmt)
        ibm_db.fetch_tuple(stmt)
        username = session['username']
        return render_template('user dashboard.html', name = username)

@app.route('/profile',methods=["POST","GET"])
def profile():
    if 'id' in session:
        uid = session['id']
        stmt = ibm_db.prepare(conn, 'SELECT * FROM userss WHERE id = ?')
        ibm_db.bind_param(stmt, 1, uid)    
        ibm_db.execute(stmt)
        acc = ibm_db.fetch_tuple(stmt)        
        return render_template('userprofile.html',fullname=acc[1]+acc[2],username=acc[3],email=acc[4],skill1=acc[6],skill2=acc[6])
    return render_template('userprofile.html')





@app.route('/admin')
def admin():
    return render_template('admin.html')


@app.route('/adminpage')
def adminpage():
    return render_template('admin dashboard.html')

@app.route('/adminlog',methods=["POST","GET"])
def adminlog():
    msg = ''
    email = request.form['email']
    password = request.form['password']
    stmt = ibm_db.prepare(conn, 'SELECT * FROM admininfo  WHERE email = ?  and password = ?')
    ibm_db.bind_param(stmt,1, email)
    ibm_db.bind_param(stmt,2, password)
    ibm_db.execute(stmt)
    logged = ibm_db.fetch_assoc(stmt)
    if(logged):
        msg = 'successfully loggedin'
        return render_template("admin dashboard.html",a=msg)
    else:
        return render_template("admin.html",a="Incorrect email/password")
    
@app.route('/loggout')
def loggout():
    if 'id ' in session:
        session.pop('id',None)
        session.pop('email',None)
        session.pop('password',None)
    return redirect(url_for('home'))

@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    return redirect(url_for('login'))


@app.route('/agent',methods=["POST","GET"])
def agent():
    return render_template('agent.html')

@app.route('/agentdata',methods=["POST","GET"])
def agentdata():
    msg = ''
    username = request.form['username']
    password = request.form['password']
    stmt = ibm_db.prepare(conn,'INSERT INTO agentinfo(username, password) VALUES (?, ?)')
    ibm_db.bind_param(stmt, 1, username)
    ibm_db.bind_param(stmt, 2, password)
    ibm_db.execute(stmt)
    msg = 'Agent has been created successfully'
    return render_template('agent.html',a = msg)

@app.route('/courses')
def courses():
    return render_template('/courses.html')

@app.route('/index' ,methods=["POST","GET"])
def index():
    if request.method == "POST":
           skill=request.form['skill1']
           stmt = ibm_db.prepare(conn, 'SELECT company, website, position, skill1, skill2, skill3 FROM jobs WHERE skill1 = ? ')
           ibm_db.bind_param(stmt, 1, skill)    
           ibm_db.execute(stmt)
           acc = ibm_db.fetch_tuple(stmt)
           data = []
           while acc != False:
              data.append(acc)
              acc = ibm_db.fetch_tuple(stmt)
              print(data)
           return render_template('index.html',tdata = data) 
    return render_template('index.html')








if __name__ == '__main__':
    app.debug=True
    app.run(host='0.0.0.0',port=8080)