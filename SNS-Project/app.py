from flask import Flask, render_template, request, redirect, session, url_for,send_file,flash

from database import createTables, AuthQueries, NotesQueries, FilesQueries
import random
from utils import EmailTemplates, sendEmail
from utils import generateHashPassword, validateHashPassword
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadTimeSignature
import os
from werkzeug.utils import secure_filename
import uuid
from mimetypes import guess_type

app = Flask(__name__)
app.secret_key = "moulya@13"

serializer = URLSafeTimedSerializer(app.secret_key)

if os.path.exists('uploads'):
    os.mkdir('uploads')


# ============================================================
# Token Functions
# ============================================================

def generateToken(email: str):
    return serializer.dumps(obj=email, salt="reset-password")


def validateToken(token):
    try:
        email = serializer.loads(
            token,
            salt="reset-password",
            max_age=600
        )
        return email

    except (SignatureExpired, BadTimeSignature):
        return None


# ============================================================
# Home Route
# ============================================================

@app.route('/')
def home():
    return render_template('home.html')


# ============================================================
# Login
# ============================================================

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')

    email = request.form.get('email')
    password = request.form.get('password')

    status, user = AuthQueries.checkEmailExists(
        email=email,
        data=True
    )

    if not status:
        flash(user, 'msg' if status else 'err')
        return redirect(url_for('login'))

    status = validateHashPassword(
        password=password,
        hash_password=user['hashpassword']
    )

    if not status:
        flash("password incorrect", 'msg' if status else 'err')
        return redirect(url_for('login'))

    session.clear()
    session['id'] = user['userid']
    session['username'] = user['username']

    return redirect(url_for('dashboard'))


# ============================================================
# Register
# ============================================================

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')

    name = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')
    confirm_password = request.form.get('confirm_password')

    if not name or not email or not password or not confirm_password:
        return "Please fill all fields", 400

    if password != confirm_password:
        flash("password mismatch", 'msg' if status else 'err')
        return redirect(url_for('register'))

    status, msg = AuthQueries.checkEmailExists(email=email)

    if status:
        flash("msg", 'msg' if status else 'err')
        return redirect(url_for('login'))

    otp = random.randint(1000, 9999)

    body = EmailTemplates.registerEmailTemplate(
        otp=otp,
        username=name
    )

    status, msg = sendEmail(
        to_email=email,
        subject="SNS Management Register",
        body=body
    )

    if not status:
        flash("msg", 'msg' if status else 'err')
        return redirect(url_for('register'))

    session.clear()
    session['otp'] = otp
    session['username'] = name
    session['email'] = email
    session['password'] = password

    return redirect(url_for('verify_otp'))


# ============================================================
# Verify OTP
# ============================================================

@app.route('/verify-otp', methods=['GET', 'POST'])
def verify_otp():
    if request.method == 'GET':
        return render_template('verify-otp.html')

    if 'otp' not in session:
        return redirect(url_for('register'))

    entered_otp = request.form.get('otp', type=int)

    if entered_otp != session['otp']:
        print("OTP incorrect")
        return redirect(url_for('verify_otp'))

    hash_password = generateHashPassword(
        password=session['password']
    )

    status, msg = AuthQueries.insertUserRecord(
        username=session['username'],
        email=session['email'],
        hash_password=hash_password
    )

    if not status:
        flash("msg", 'msg' if status else 'err')
        return redirect(url_for('register'))

    flash("msg", 'msg' if status else 'err')

    session.clear()
    return redirect(url_for('login'))


# ============================================================
# Forgot Password
# ============================================================

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'GET':
        return render_template('forgot_password.html')

    email = request.form.get('email')

    status, msg = AuthQueries.checkEmailExists(email=email)

    if not status:
        flash("msg", 'msg' if status else 'err')
        return redirect(url_for('forgot_password'))

    token = generateToken(email=email)

    reset_link = url_for(
        'reset_password',
        token=token,
        _external=True
    )

    body = EmailTemplates.forgotPasswordTemplate(url=reset_link)

    status, msg = sendEmail(
        to_email=email,
        subject="Reset Password - SNS",
        body=body
    )

    if not status:
        flash("msg", 'msg' if status else 'err')
        return redirect(url_for('forgot_password'))

    return redirect(url_for('login'))


# ============================================================
# Reset Password
# ============================================================

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    email = validateToken(token)

    if email is None:
        return "Reset link is invalid or expired. Please request a new link.", 400

    if request.method == 'GET':
        return render_template(
            'reset_password.html',
            token_val=token
        )

    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')

    if not new_password or not confirm_password:
        return "Please enter both password fields", 400

    if new_password != confirm_password:
        print("Password mismatch")
        return redirect(url_for('reset_password', token=token))

    hash_password = generateHashPassword(
        password=new_password
    )

    status, msg = AuthQueries.updatePassword(
        email=email,
        hash_password=hash_password
    )

    flash("msg", 'msg' if status else 'err')
    return f"<h2>{msg}</h2>"


# ============================================================
# Dashboard
# ============================================================

@app.route('/dashboard')
def dashboard():
    if 'id' not in session:
        return redirect(url_for('login'))

    status1, total_notes = NotesQueries.getTotalNotes(
        userid=session['id']
    )

    status2, total_files = FilesQueries.getTotalFiles(
        userid=session['id']
    )

    if not status1:
        total_notes = 0

    if not status2:
        total_files = 0

    return render_template(
        'dashboard.html',
        username=session['username'],
        total_notes=total_notes,
        total_files=total_files
    )
# ============================================================
# Notes Routes
# ============================================================

# View All Notes
@app.route('/dashboard/notes')
def mynotes():
    if 'id' not in session:
        return redirect(url_for('login'))

    userid = session['id']

    status, all_notes = NotesQueries.getAllNotes(
        userid=userid
    )

    if not status:
        return str(all_notes)

    return render_template(
        'notes.html',
        all_notes=all_notes
    )


# Create New Note
@app.route('/dashboard/notes/new-notes', methods=['GET', 'POST'])
def new_notes():
    if 'id' not in session:
        return redirect(url_for('login'))

    if request.method == 'GET':
        return render_template('new_notes.html')

    title = request.form.get('title')
    content = request.form.get('content')

    if not title or not content:
        return "Please enter title and content", 400

    status, msg = NotesQueries.insertNotesRecord(
        userid=session['id'],
        title=title,
        content=content
    )

    if status:
        return redirect(url_for('mynotes'))

    return str(msg)


# View Single Note
@app.route('/dashboard/notes/view/<int:id>')
def view_notes(id):
    if 'id' not in session:
        return redirect(url_for('login'))

    status, note = NotesQueries.getAllNotes(
        userid=session['id'],
        notesid=id
    )

    if not status:
        return str(note)

    if not note:
        return "Note not found", 404

    return render_template(
        'view_notes.html',
        note=note
    )


# Update Note
@app.route('/dashboard/notes/update/<int:notesid>', methods=['GET', 'POST'])
def edit_notes(notesid):
    if 'id' not in session:
        return redirect(url_for('login'))

    userid = session['id']

    if request.method == 'GET':
        status, note = NotesQueries.getAllNotes(
            userid=userid,
            notesid=notesid
        )

        if not status:
            return str(note)

        if not note:
            return "Note not found", 404

        return render_template(
            'edit_notes.html',
            title=note['title'],
            content=note['content'],
            id=notesid
        )

    title = request.form.get('title')
    content = request.form.get('content')

    if not title or not content:
        return "Please enter title and content", 400

    status, msg = NotesQueries.updateNotes(
        userid=userid,
        notesid=notesid,
        title=title,
        content=content
    )

    if status:
        return redirect(url_for('mynotes'))

    return str(msg)

# Delete Note
@app.route('/dashboard/notes/delete/<int:notesid>', methods=['GET'])
def delete_notes(notesid):
    if 'id' not in session:
        return redirect(url_for('login'))

    status, msg = NotesQueries.deleteNotes(
        userid=session['id'],
        notesid=notesid
    )
    flash("msg", 'msg' if status else 'err')
    return redirect(url_for('mynotes'))


# ==================================================
# View Files
# ==================================================
@app.route('/dashboard/files')
def myfiles():
    if 'id' not in session:
        return redirect(url_for('login'))

    # Get all files based on userid
    status, all_files = FilesQueries.getAllFiles(
        userid=session['id']
    )

    if status:
        return render_template('files.html', files=all_files)

    return str(all_files), 500


@app.route('/dashboard/files/upload_file', methods=['GET', 'POST'])
def upload_file():
    if 'id' not in session:
        return redirect(url_for('login'))

    if request.method == 'GET':
        return render_template('upload_file.html')

    file = request.files.get('file')

    if not file or file.filename == '':
        return "Please select a file"

    # File metadata
    original_name = file.filename
    file_name = secure_filename(original_name)

    if not file_name or '.' not in file_name:
        return "Invalid filename"

    file_type = file_name.rsplit('.', 1)[-1].lower()

    if file_type not in {'pdf', 'jpg', 'jpeg', 'png', 'docx', 'ppt', 'csv'}:
        return "File type not allowed"

    # Unique filename
    unique_name = str(uuid.uuid1()) + "_" + file_name

    # Create uploads folder
    upload_folder = os.path.join(app.root_path, 'uploads_folder')
    os.makedirs(upload_folder, exist_ok=True)

    # Full file path
    file_path = os.path.join(upload_folder, unique_name)

    # Save uploaded file
    file.save(file_path)

    # Get file metadata
    file_size = os.path.getsize(file_path)
    mime_type = guess_type(file_path)[0]

    data = (
        session['id'],
        original_name,
        unique_name,
        mime_type,
        file_size,
        file_path
    )

    status, msg = FilesQueries.insertFileRecord(file_data=data)

    flash("msg", 'msg' if status else 'err')

    if status:
        return redirect(url_for('myfiles'))

    return str(msg), 500


# ==================================================
# View Individual File
# ==================================================
@app.route('/dashboard/files/view/<int:file_id>')
def view_file(file_id):
    #getfile metadata by using file_id
    status,file=FilesQueries.getAllFiles(userid=session['id'], fileid=file_id)
    return send_file(
        path_or_file=file['filepath'],
        mimetype=file['mimetype'],
        as_attachment=False
        )

# ==================================================
# Download File
# ==================================================
@app.route('/dashboard/files/download/<int:file_id>')
def download_file(file_id):
    #getfile metadata by using file_id
        status,file=FilesQueries.getAllFiles(userid=session['id'], fileid=file_id)
        return send_file(
            path_or_file=file['filepath'],
            mimetype=file['mimetype'],
            as_attachment=True
            )
    


# ==================================================
# Delete File
# ==================================================
@app.route('/dashboard/files/delete/<int:file_id>')
def delete_file(file_id):
    if 'id' not in session:
        return redirect(url_for('login'))

    status, msg = FilesQueries.deleteFile(fileid=file_id)
    flash("msg", 'msg' if status else 'err')

    if status:
        return redirect(url_for('myfiles'))

    return str(msg), 500

#==========================================
# logout
#==========================================
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')


# ==================================================
# Run Application
# ==================================================
if __name__ == '__main__':
    print(createTables())
    app.run(debug=True)
