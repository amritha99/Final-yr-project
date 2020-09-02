import os
from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm 
from wtforms import StringField, PasswordField, BooleanField,FileField
from wtforms.validators import InputRequired, Email, Length
from flask_sqlalchemy  import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user


#UPLOAD_FOLDER = '/Users/sreep/Desktop/lp'


app = Flask(__name__)
app.config['SECRET_KEY'] = '999999999'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:test123@localhost/detection'
bootstrap = Bootstrap(app)
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
app.config['UPLOAD_FOLDER'] = '/Users/sreep/OneDrive/Documents/flask_app/uploads'
app.config["ALLOWED_IMAGE_EXTENSIONS"] = ["PNG", "JPG", "JPEG", "GIF","MP4"]

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), unique=True)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(80))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class LoginForm(FlaskForm):
    username = StringField('username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=80)])
    remember = BooleanField('remember me')

class RegisterForm(FlaskForm):
    email = StringField('email', validators=[InputRequired(), Email(message='Invalid email'), Length(max=50)])
    username = StringField('username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=80)])


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if check_password_hash(user.password, form.password.data):
                login_user(user, remember=form.remember.data)
                return redirect(url_for('dashboard'))

        return '<h1>Invalid username or password</h1>'
        #return '<h1>' + form.username.data + ' ' + form.password.data + '</h1>'

    return render_template('login.html', form=form)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = RegisterForm()

    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data, method='sha256')
        new_user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        return '<h1>New user has been created!</h1>'
        #return '<h1>' + form.username.data + ' ' + form.email.data + ' ' + form.password.data + '</h1>'

    return render_template('signup.html', form=form)

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', name=current_user.username)


#def ImageUploader():
 # return render_template("dashboard.html")
 
def allowed_image(filename):

    # We only want files with a . in the filename
    if not "." in filename:
        return False

    # Split the extension from the filename
    ext = filename.rsplit(".", 1)[1]

    # Check if the extension is in ALLOWED_IMAGE_EXTENSIONS
    if ext.upper() in app.config["ALLOWED_IMAGE_EXTENSIONS"]:
        return True
    else:
        return False

@app.route("/ImageUploader", methods=["GET", "POST"])
def ImageUploader():
    msg = ""
    # Check to be sure the data is a POST
    # rather than a GET.
    if request.method == "POST":
        # IF a file was uploaded.
        if request.files:
            # Retrieve the submitted file data
            # and place that data in a variable
            # called "fileData"
            image = request.files["image"]
            if image.filename == "":
                print("No filename")
                return redirect(request.url)
        
            if allowed_image(image.filename):
                filename = secure_filename(image.filename)

                image.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))

                print("Image saved")

                return redirect(request.url)

            else:
                print("That file extension is not allowed")
                return redirect(request.url)

            # Call function for saving the file
            # data to Postgres.

    
    return render_template("dashboard.html")
            #SaveFileToPG(fileData)
        #else:
            # If no file was uploaded, create a message
            # for the user.
            
#msg = "No file found. Please choose one from your device."
    # Show the user our HTML page and send a message if one exists.
    #return render_template("dashboard.html", msg)

#def SaveFileToPG(id_image, fileData):
    #s = ""
    #s += "INSERT INTO tbl_files_images"
    #s += "("
    #s += "id_image"
    #s += ", blob_image_data"
    #s += ") VALUES ("
    #s += "(%id_image)"
    #s += ", '(%fileData)'"
    #s += ")"
    
    #try:
     #   db_cursor.execute(s, [id_image, fileData])
    #except psycopg2.Error as e:
    #    t_msg_err = "SQL error: " + e + "/n SQL: " + s
    #    return render_template("dashboard.html", msg = t_msg_err)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)