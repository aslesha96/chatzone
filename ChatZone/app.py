from flask import Flask, request, session, redirect, url_for, render_template, flash, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
# from flask.ext.socketio import SocketIO, emit
from sqlalchemy import DateTime, desc
import datetime
import json

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = 'ssshhhhhh'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blogContent.db'
db = SQLAlchemy(app)
# socketio = SocketIO(app)

class UserDatabase(db.Model):
	email = db.Column(db.String(100), primary_key = True)
	name = db.Column(db.String(100))
	password = db.Column(db.String(100))
	phone = db.Column(db.String(20))

	def __init__(self, name, password, email, phone):
		self.name = name
		self.password = password
		self.email = email
		self.phone = phone

class blogcontent(db.Model):
	id = db.Column(db.Integer, autoincrement = True, primary_key = True)
	blog_by = db.Column(db.String(200))
	blog_title = db.Column(db.String(100))
	blog_content = db.Column(db.String(1000))
	blog_upvotes = db.Column(db.Integer)
	blog_downvotes = db.Column(db.Integer)
	time = db.Column(DateTime)
	status = db.Column(db.String(50))

	def __init(self, blog_by, blog_title, blog_content, blog_upvotes, blog_downvotes, time, status = "pending"):
		self.blog_by = blog_by
		self.blog_title = blog_title
		self.blog_content = blog_content
		self.blog_upvotes = blog_upvotes
		self.blog_downvotes = blog_downvotes
		self.time = time
		self.status = status

class chatDB(db.Model):
	id = db.Column(db.Integer, autoincrement = True, primary_key = True)
	blogid = db.Column(db.Integer)
	email = db.Column(db.String(200))
	message = db.Column(db.String(250))

	def __init__(self, blogid, email, message):
		self.blogid = blogid
		self.email = email
		self.message = message

	def as_dict(self):
		d = {}
		d["email"] = self.email
		d["message"] = self.message
		return d

class votesDB(db.Model):
	id = db.Column(db.Integer, autoincrement = True, primary_key = True)
	blog_id = db.Column(db.Integer)
	email = db.Column(db.String(200))
	like = db.Column(db.Integer)
	dislike = db.Column(db.Integer)

	def __init__(self, blog_id, email, like, dislike):
		self.blog_id = blog_id
		self.email = email
		self.like = like
		self.dislike = dislike


db.create_all()

@app.route('/up', methods = ['GET','POST'])
def handlevote1():
	user = votesDB.query.filter_by(email = session['log_email']).filter_by(blog_id = request.form['blog_id']).all()
	# print("santhan")
	if len(user) == 0:
		updatevotesDB = votesDB(blog_id = request.form['blog_id'], email = session['log_email'], like = 0, dislike = 0)
		db.session.add(updatevotesDB)
		db.session.commit()

	user = votesDB.query.filter_by(email = session['log_email']).filter_by(blog_id = request.form['blog_id']).one()
	if user.like == 0 and user.dislike == 0:
		user.like = 1
		db.session.commit()
		updatevote = blogcontent.query.filter_by(id = request.form['blog_id']).one()
		updatevote.blog_upvotes = updatevote.blog_upvotes + 1
		db.session.commit()
		data = int(updatevote.blog_upvotes)
		data2 = int(updatevote.blog_downvotes)
		return jsonify({'data': data, 'data2':data2})

	elif user.like == 0 and user.dislike == 1:
		user.dislike = 0
		user.like = 1
		db.session.commit()
		updatevote = blogcontent.query.filter_by(id = request.form['blog_id']).one()
		updatevote.blog_upvotes = updatevote.blog_upvotes + 1
		updatevote.blog_downvotes = updatevote.blog_downvotes - 1
		db.session.commit()
		data = int(updatevote.blog_upvotes)
		data2 = int(updatevote.blog_downvotes)
		return jsonify({'data': data, 'data2':data2})

	else:
		updatevote = blogcontent.query.filter_by(id = request.form['blog_id']).one()
		data = int(updatevote.blog_upvotes)
		data2 = int(updatevote.blog_downvotes)
		return jsonify({'data': data, 'data2':data2})
			
@app.route('/down', methods = ['GET','POST'])
def handlevote2():
	user = votesDB.query.filter_by(email = session['log_email']).filter_by(blog_id = request.form['blog_id']).all()
	if len(user) == 0:
		updatevotesDB = votesDB(blog_id = request.form['blog_id'], email = session['log_email'], like = 0, dislike = 0)
		db.session.add(updatevotesDB)
		db.session.commit()
	user = votesDB.query.filter_by(email = session['log_email']).filter_by(blog_id = request.form['blog_id']).one()
	if user.like == 0 and user.dislike == 0:
		user.dislike = 1
		db.session.commit()
		updatevote = blogcontent.query.filter_by(id = request.form['blog_id']).one()
		updatevote.blog_downvotes = updatevote.blog_downvotes + 1
		db.session.commit()
		data1 = int(updatevote.blog_downvotes)
		data2 = int(updatevote.blog_upvotes)
		return jsonify({'data': data1, 'data2': data2})

	elif user.like == 1 and user.dislike == 0:
		user.dislike = 1
		user.like = 0
		db.session.commit()
		updatevote = blogcontent.query.filter_by(id = request.form['blog_id']).one()
		updatevote.blog_upvotes = updatevote.blog_upvotes - 1
		updatevote.blog_downvotes = updatevote.blog_downvotes + 1
		db.session.commit()
		data1 = int(updatevote.blog_downvotes)
		data2 = int(updatevote.blog_upvotes)
		return jsonify({'data': data1, 'data2':data2})

	else:
		updatevote = blogcontent.query.filter_by(id = request.form['blog_id']).one()
		data = int(updatevote.blog_downvotes)
		data2 = int(updatevote.blog_upvotes)
		return jsonify({'data': data, 'data2':data2})


@app.route('/reload', methods = ['GET','POST'])
def rel():
	updatevote = blogcontent.query.filter_by(id = request.form['blog_id']).one()
	return jsonify({'likes': updatevote.blog_upvotes, 'dislikes': updatevote.blog_downvotes})

# @socketio.on('up')
# def handlevote1(ballot):
# 	print("santhan upvote")
# 	updatevote = blogcontent.query.filter_by(id = ballot).one()
# 	print(updatevote)
# 	updatevote.blog_upvotes = updatevote.blog_upvotes + 1

# 	db.session.commit()
# 	emit('vote_results', {'upvote': updatevote.blog_upvotes, 'downvote': updatevote.blog_downvotes}, broadcast = True)

# @socketio.on('down')
# def handlevote2(ballot):
# 	print("santhan downvote")
# 	updatevote = blogcontent.query.filter_by(id = ballot)
# 	updatevote.blog_downvotes = updatevote.blog_downvotes + 1
# 	db.session.commit()
# 	emit('vote_results', {'upvote': updatevote.blog_upvotes, 'downvote': updatevote.blog_downvotes}, broadcast = True)

@app.route('/chat', methods = ['POST'])
def chat():
	if request.form['message']:
		msg = request.form['message'].replace("<", "&lt;")
		msg = msg.replace(">","&gt;")
		newChatItem = chatDB(blogid=request.form['blog_id'], email=session['name'], message=msg)
		db.session.add(newChatItem)
		db.session.commit()
	return jsonify({'email': session['name'], 'message': msg})

@app.route('/chatReload', methods = ['POST'])
def chatReload():
    chats = chatDB.query.filter_by(blogid = request.form['blog_id']).all()
    d = [chat.as_dict() for chat in chats]
    return json.dumps([chat.as_dict() for chat in chats])

######################################################
@app.route('/adminpage', methods = ['GET','POST'])
def admin():
	if session['log_email'] == "aslesha402@gmail.com":
		return render_template('mypage.html')
	else:
		abort(404)

@app.route('/admin-dashboard', methods = ['GET','POST'])
def admindashboard():
	if session['log_email'] == "aslesha402@gmail.com":
		pendingblogs = blogcontent.query.filter_by(status = "pending").all()
		return render_template('mydashboard.html', pendingblogs = pendingblogs)
	else:
		abort(404)

@app.route('/blogstatus', methods = ['GET','POST'])
def blogstatus():
	if session['log_email'] == "aslesha402@gmail.com":
		approve = request.form.get("approve")
		if approve:
			update = blogcontent.query.filter_by(id = approve).one()
			update.status = "approved"
			db.session.commit()
			return redirect(url_for('admindashboard'))
		else:
			decline = request.form.get("decline")
			update = blogcontent.query.filter_by(id = decline).one()
			update.status = "declined"
			db.session.commit()
			return redirect(url_for('admindashboard'))
	else:
		abort(404)

@app.route('/yourposts',methods = ['GET','POST'])
def yourposts():
	if session['logged_in']==True:
		yourposts = blogcontent.query.filter_by(blog_by = session['log_email']).all()
		if session['log_email'] == "aslesha402@gmail.com":
			return render_template("yourposts.html", yourposts = yourposts, admin = True)
		else:
			return render_template("yourposts.html", yourposts = yourposts)
	else:
		return redirect(url_for('homepage'))



##########################################################




###############HomePage######################
@app.route('/')
def homepage():
	try:
	    chat = chatDB.query.all()
	    if session['logged_in']==True:
	        blogs = blogcontent.query.filter_by(status = "approved").order_by(desc(blogcontent.blog_upvotes)).all()
	        if session['log_email'] == "aslesha402@gmail.com":
	        	return render_template('getpost.html', blogs = blogs, chats = chat, admin = True)
	        return render_template('getpost.html', blogs = blogs, chats = chat)
	    else:
	        blogs = blogcontent.query.filter_by(status = "approved").order_by(desc(blogcontent.blog_upvotes)).all()
	        return render_template('getpost.html', blogs = blogs, chats = chat)

	except:
		session['logged_in']=False
		blogs = blogcontent.query.filter_by(status = "approved").order_by(desc(blogcontent.blog_upvotes)).all()
		# print(blogs)
		chat = chatDB.query.all()
		return render_template('getpost.html', blogs = blogs, chats = chat)
#############################################

@app.route('/dopost', methods = ['GET','POST'])
def dopost():
	if session['logged_in'] == True:
		return render_template('dopost.html')
	else:
		return redirect(url_for('homepage'))

@app.route('/writepost', methods = ['GET', 'POST'])
def writepost():
	if request.method == 'GET':
		try:
			if session['logged_in']==True:
				render_template('dopost.html')
			else:
				return redirect(url_for('homepage'))
		except:
			return redirect(url_for('homepage'))
	else:
		blog_title = request.form['blog_title']
		blog_content = request.form['blog_message']
		blog_by = session['log_email']
		newblog = blogcontent(blog_by = blog_by, blog_title = blog_title, blog_content = blog_content, blog_upvotes = 0, blog_downvotes = 0, time = datetime.datetime.now(), status = "pending")
		db.session.add(newblog)
		db.session.commit()
		return redirect(url_for('homepage'))
################LoginPage####################
@app.route('/login', methods = ['GET', 'POST'])
def login():
	error = None
	loggin = True
	if request.method == 'POST':
		if checkLogin(request.form['email'], request.form['password']):
		    session['logged_in'] = True
		    getname = UserDatabase.query.filter_by(email = request.form['email']).one()
		    session['name'] = getname.name
		    session['log_email'] = request.form['email']
		    flash("You are logged in")
		    if session['log_email'] == "aslesha402@gmail.com":
		    	return redirect(url_for('homepage'))
		    else:
		    	return redirect(url_for('homepage'))

		else:
			error = 'Invalid Credentials'
		return render_template('login.html', error = error, loggin = loggin)
	try:
		if session['logged_in']==True:
			return redirect(url_for('homepage'))
	except:
		return render_template('login.html', error = "", loggin = loggin)
	return render_template('login.html', error = "", loggin = loggin)

def checkLogin(e, p):
    details = UserDatabase.query.filter_by(email=e).filter_by(password=p).all()
    # print(details)
    if(len(details) > 0):
        return True
    else:
        return False
##############################################

##############SignUp##########################
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    error = None
    signup = True
    if request.method == 'GET':
    	try:
    		if session['logged_in']==True:
    			return redirect(url_for('homepage'))
    	except:
    		signup = 'signup'
    		return render_template('login.html', error=error, signup = signup)
    if request.method == 'POST':
        if request.form['password'] != request.form['confirm-password']:
            error = 'Renter both password fields'
        elif checksignup(request.form['email'], request.form['username']):
        	error = 'Username or Email already exists'
        else:
            newUser = UserDatabase(email=request.form['email'],name=request.form['username'],password=request.form['password'],phone=request.form['phone'])
            db.session.add(newUser)
            db.session.commit()
            flash('You have registered, please login!!')
            loggin = True
            return render_template('login.html', error = "", loggin = loggin)
    return render_template('login.html', error=error, signup = signup)



def checksignup(e, p):
    useremail = UserDatabase.query.filter_by(email=e).all()
    username = UserDatabase.query.filter_by(name=p).all()
    # print(details)
    if(len(useremail) > 0 or len(username) > 0):
        return True
    else:
        return False
################################################

################Logout##########################
@app.route('/logout')
def logout():
    session['logged_in'] = False
    return redirect(url_for('homepage'))

################################################

############Main###########
if __name__ == '__main__':
	app.run()
    # socketio.run(app)
###########################