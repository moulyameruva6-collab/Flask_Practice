from flask import Flask, render_template, request, redirect, session, url_for

from database import createTables, AuthQueries
import random
from utils import EmailTemplates, sendEmail
from utils import generateHashPassword, validateHashPassword
from itsdangerous import URLSafeTimedSerializer, SignatureExpired,  BadTimeSignature

app = Flask(__name__)
app.secret_key = "moulya@13"
serializer = URLSafeTimedSerializer(app.secret_key)

#generateotp
def generateToken(email:str):
    token = serializer.dumps(obj=email,salt="reset-password")
    return token

#validate token
def validateToken(token):
    try:
        data=serializer.loads(token,salt="reset-password",max_age=600)#10mins
        return data
    except BadTimeSignature:
        print("URL Time Expired")
        return redirect('/login')
    except SignatureExpired:
        print("Invalid url")
        return redirect('/login')



# Home route
@app.route('/')
def home():
    return render_template('home.html')


# Login
@app.route("/login", methods=['GET', 'POST'])
def login():

    # GET request
    if request.method == 'GET':
        return render_template('login.html')

    # POST request
    
    if request.method=='POST':
        email = request.form.get('email')
        password = request.form.get('password')
        status, user = AuthQueries.checkEmailExists(email=email, data=True)

        if status == False:
            print(user)
            return redirect('/login')
        #match password
        status = validateHashPassword(password=password, hash_password=user['hashpassword'])

        if status == False:
            print("Password incoorect")
            return redirect('/login')
        #redirect to dashboard page
        return redirect('/dashboard')



        
    


# Register
@app.route("/register", methods=['GET', 'POST'])
def register():

    # GET request
    if request.method == 'GET':
        return render_template('register.html')

    # POST request
    if request.method == 'POST':

        name = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        print(name, email, password, confirm_password)

        # Check password and confirm password
        if password != confirm_password:
            print("password miss match")
            return redirect('/register')

        # Check email already exists
        status, msg = AuthQueries.checkEmailExists(email=email)

        if status == True:
            print(msg)
            return redirect('/login')

        print(msg)

        # Generate OTP
        otp = random.randint(1000, 9999)

        # Email body
        body = EmailTemplates.registerEmailTemplate(
            otp=otp,
            username=name
        )

        # Send OTP
        status, msg = sendEmail(
            to_email=email,
            subject="SNS Management Register!!!",
            body=body
        )

        if status == False:
            print(msg)
            return redirect('/register')

        # Store data in session
        session.clear()
        session['otp'] = otp
        session['username'] = name
        session['email'] = email
        session['password'] = password

        # Go to OTP page
        return redirect('/verify-otp')


# Verify OTP
@app.route('/verify-otp', methods=['GET', 'POST'])
def verify_otp():

    if request.method == 'GET':
        return render_template('verify-otp.html')

    if request.method == 'POST':
        otp = int(request.form.get('otp'))

        if otp != session['otp']:
            print("OTP Incorrect")
            return redirect('/verify-otp')

        hash_password = generateHashPassword(
            password=session['password']
        )

        status, msg = AuthQueries.insertUserRecord(
            username=session['username'],
            email=session['email'],
            hash_password=hash_password
        )

        if status == False:
            print(msg)
            return redirect('/')

        print(msg)
        return redirect('/login')

#forgot password
@app.route("/forgot_password", methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'GET':
        return render_template('forgot_password.html')
    if request.method=='POST':
        email=request.form.get('email')
       
        #checkemailexists
        status, msg=AuthQueries.checkEmailExists(email=email)
        if status == False:
            print(msg)
            return redirect(url_for('login'))
        #storeemail in token
        token = generateToken(email=email)
        #generate reset passwrd link
        reset_link =  url_for('reset_password',token=token,_external=True)
         #send link via email
        body= EmailTemplates.forgotPasswordTemplate(url=reset_link)
        status,msg = sendEmail(to_email=email,subject="Reset Password -SNS",body=body)
        if status ==False:
            print(msg)
            return redirect(url_for('forgot_password'))
        #redirect tologin page
        return redirect(url_for('login'))

#reset password
@app.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_password(token):
    email=validateToken(token=token)
    if request.method == 'GET':
        return render_template('reset_password.html',token_val=token)
    if request.method=='POST':
        new_password=request.form.get('new_password')
        confirm_password=request.form.get('confirm_password')
        if new_password != confirm_password:
            print("Password miss match")
            return redirect(url_for('reset_password',token=token))
        #generatehash password
        hash_password=generateHashPassword(password=new_password)
        #update hashpassword in database updates by using email
        status,msg = AuthQueries.updatePassword(email=email,hash_password=hash_password)
        print(msg)
        return f"<h2>{msg}</h2>"

        #return msglike "password updates successfully"

    

#dashboard
@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")



if __name__ == "__main__":
    print(createTables())
    app.run(debug=True)