from flask import Flask, render_template, request, session, redirect, send_file, url_for, flash, jsonify
import mysql.connector
import os
from cryptography.fernet import Fernet
from io import BytesIO
from flask_mail import Mail, Message
import socket
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Email configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = 'testmailalert20@gmail.com'
app.config['MAIL_PASSWORD'] = 'qwghdvduxumxjidk'
app.config['MAIL_DEFAULT_SENDER'] = 'datasecureemail@gmail.com'

mail = Mail(app)

def send_email(remail, key):
    msg = Message('Data Breach', recipients=[remail])
    msg.body = f'Your request has been approved. Your key: {key}'
    try:
        mail.send(msg)
    except Exception as e:
        print(f'Error sending email: {str(e)}')

def send_intrusion_email(remail, uname, ipaddress, attempt_time):
    """Send a security warning email when an account is locked due to failed login attempts."""
    msg = Message('⚠️ Security Alert: Your Account Has Been Locked', recipients=[remail])
    msg.body = (
        f'Dear {uname},\n\n'
        f'We detected 3 consecutive failed login attempts on your Data Security account.\n\n'
        f'Details:\n'
        f'  - IP Address : {ipaddress}\n'
        f'  - Date & Time: {attempt_time}\n\n'
        f'Your account has been LOCKED as a security precaution.\n'
        f'Please contact the administrator to unlock your account.\n\n'
        f'If this was you, please reach out to the admin immediately.\n\n'
        f'— Data Security System'
    )
    try:
        mail.send(msg)
    except Exception as e:
        print(f'Error sending intrusion email: {str(e)}')

# MySQL configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_DATABASE'] = 'databreach'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''

# Encryption key setup
key_path = "encryption_key.key"
if not os.path.exists(key_path):
    key = Fernet.generate_key()
    with open(key_path, "wb") as key_file:
        key_file.write(key)
else:
    with open(key_path, "rb") as key_file:
        key = key_file.read()
fernet = Fernet(key)

# ------------------- HARDCODED SERVER CREDENTIALS -------------------
# Server A and Server B credentials for the 3-step approval chain
SERVER_A_CREDS = {'username': 'servera', 'password': 'servera123'}
SERVER_B_CREDS = {'username': 'serverb', 'password': 'serverb123'}

def getip():
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    return ip_address

def get_db_connection():
    return mysql.connector.connect(
        host=app.config['MYSQL_HOST'],
        database=app.config['MYSQL_DATABASE'],
        user=app.config['MYSQL_USER'],
        password=app.config['MYSQL_PASSWORD']
    )


# ------------------- ROUTES -------------------
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/server', methods=['GET', 'POST'])
def server():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Admin credentials — goes to intrusion monitoring
        if username == 'admin' and password == 'admin':
            return redirect(url_for('intrusions_list'))

        # Server A credentials — goes to Server A dashboard
        elif username == SERVER_A_CREDS['username'] and password == SERVER_A_CREDS['password']:
            session['server_role'] = 'server_a'
            flash('Server A login successful!', 'success')
            return redirect(url_for('server_a_dashboard'))

        # Server B credentials — goes to Server B dashboard
        elif username == SERVER_B_CREDS['username'] and password == SERVER_B_CREDS['password']:
            session['server_role'] = 'server_b'
            flash('Server B login successful!', 'success')
            return redirect(url_for('server_b_dashboard'))

        else:
            flash('Invalid username or password', 'danger')
            return redirect(url_for('server'))

    return render_template('server.html')


## ------------------- LOGIN / SIGNUP -------------------

@app.route('/userlogin', methods=["GET","POST"])
def login():
    message = ''
    warning_level = ''   # 'info' | 'warning' | 'danger'
    attempts_left = None

    if request.method == "POST":
        name = request.form.get('name')
        password = request.form.get('password')

        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True, buffered=True)
        try:
            # --- Look up by username only first ---
            cursor.execute("SELECT * FROM user WHERE name=%s", (name,))
            user_by_name = cursor.fetchone()

            if user_by_name:
                # Check if already blocked
                if user_by_name['status'] == 'blocked':
                    message = "Your account is locked. Please contact the administrator."
                    warning_level = 'danger'
                    return render_template('login.html', message=message, warning_level=warning_level, attempts_left=attempts_left)

                # Verify password
                if user_by_name['password'] == password:
                    # ✅ Correct — clear attempts and log in
                    session.pop('login_attempts', None)
                    session.pop('login_username', None)
                    session['uid'] = user_by_name['uid']
                    session['uname'] = user_by_name['name']
                    flash("Login successful!", "success")
                    return redirect(url_for('dashboard'))
                else:
                    # ❌ Wrong password — track attempts per username in session
                    attempt_key = f'login_attempts_{user_by_name["uid"]}'
                    session[attempt_key] = session.get(attempt_key, 0) + 1
                    current_attempts = session[attempt_key]
                    MAX_ATTEMPTS = 3

                    if current_attempts >= MAX_ATTEMPTS:
                        # 🔒 Lock the account
                        cursor.execute("UPDATE user SET status='blocked' WHERE uid=%s", (user_by_name['uid'],))

                        # 📋 Log to intrusion table
                        ipaddress = getip()
                        current_dt = datetime.now()
                        cursor.execute(
                            "INSERT INTO intrusion (ownerid, uid, uname, ipaddress, filename, date) VALUES (%s,%s,%s,%s,%s,%s)",
                            (0, user_by_name['uid'], user_by_name['name'], ipaddress, 'LOGIN_ATTEMPT', current_dt.date())
                        )
                        connection.commit()

                        # 📧 Send warning email
                        if user_by_name.get('email'):
                            send_intrusion_email(
                                user_by_name['email'],
                                user_by_name['name'],
                                ipaddress,
                                current_dt.strftime('%Y-%m-%d %H:%M:%S')
                            )

                        # Clear attempt counter
                        session.pop(attempt_key, None)

                        message = ("🔒 Your account has been LOCKED after 3 failed attempts. "
                                   "A security alert has been sent to your email. "
                                   "Please contact the administrator to unlock your account.")
                        warning_level = 'danger'
                    else:
                        remaining = MAX_ATTEMPTS - current_attempts
                        message = f"Invalid credentials. {remaining} attempt(s) remaining before your account is locked."
                        warning_level = 'warning' if current_attempts == 2 else 'info'
                        attempts_left = remaining
            else:
                # Username doesn't exist — don't reveal specifics
                message = "Invalid username or password."
                warning_level = 'info'
        finally:
            cursor.close()
            connection.close()

    return render_template('login.html', message=message, warning_level=warning_level, attempts_left=attempts_left)

@app.route('/usersignup', methods=["GET","POST"])
def signup():
    connection = get_db_connection()
    cursor = connection.cursor(buffered=True)
    message = ''
    if request.method == "POST":
        name = request.form['name']
        password = request.form['password']
        email = request.form['email']

        try:
            cursor.execute(
                "INSERT INTO user (name, password, status, email) VALUES (%s,%s,%s,%s)",
                (name, password, "allowed", email)
            )
            connection.commit()
            flash("Signup successful! Now login with your credentials.", "success")
            return redirect(url_for('login'))
        except Exception as e:
            print(f"Signup error: {e}")
            message = "Error signing up. Username or email may already exist."
        finally:
            cursor.close()
            connection.close()
    return render_template('signup.html', message=message)

# ------------------- DASHBOARD -------------------

@app.route('/dashboard', methods=["GET", "POST"])
def dashboard():
    uid = session.get('uid')
    name = session.get('uname')
    if not uid:
        return redirect(url_for('login'))

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True, buffered=True)

    try:
        # Fetch user's files
        cursor.execute("SELECT * FROM files WHERE uid=%s", (uid,))
        files = cursor.fetchall()

        # Other users' files
        cursor.execute("""
            SELECT files.*, user.name AS owner_name
            FROM files
            JOIN user ON files.uid = user.uid
            WHERE files.uid != %s
        """, (uid,))
        others = cursor.fetchall()

        # Requests made by this user
        cursor.execute("""
            SELECT requests.*, files.filename, user.name AS owner_name
            FROM requests
            JOIN files ON requests.fileid = files.fid
            JOIN user ON files.uid = user.uid
            WHERE requests.rid = %s
        """, (uid,))
        my_requests = cursor.fetchall()

        # Handle file upload
        if request.method == "POST":
            file_obj = request.files.get('file')
            skey = request.form.get('skey')
            if not file_obj or not skey:
                return "File or Secret Key missing!", 400

            filename = file_obj.filename
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            encrypted_content = fernet.encrypt(file_obj.read())
            with open(filepath, "wb") as f:
                f.write(encrypted_content)

            cursor.execute("INSERT INTO files (uid, filename, filepath, skey) VALUES (%s,%s,%s,%s)",
                           (uid, filename, filepath, skey))
            connection.commit()
            flash("File uploaded successfully!", "success")
            return redirect(url_for('dashboard'))

        return render_template('dashboard.html', name=name.upper(), files=files, others=others, my_requests=my_requests)

    finally:
        cursor.close()
        connection.close()


# ------------------- REQUEST FILE -------------------

@app.route('/request/<int:fid>/<int:oid>')
def request_file(fid, oid):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True, buffered=True)
    try:
        cursor.execute("SELECT * FROM requests WHERE rid=%s AND fileid=%s", (session['uid'], fid))
        existing_request = cursor.fetchone()

        if existing_request:
            flash("You already requested this file!", "warning")
        else:
            cursor.execute("INSERT INTO requests (rid, rname, fileid, ownerid, status) VALUES (%s,%s,%s,%s,%s)",
                           (session['uid'], session['uname'], fid, oid, "pending"))
            connection.commit()
            flash("Request sent successfully!", "success")
        return redirect(url_for('dashboard'))
    finally:
        cursor.close()
        connection.close()

# ------------------- VIEW REQUESTS MADE BY LOGGED-IN USER -------------------

@app.route('/yourrequest', methods=["GET"])
def your_requests():
    uid = session.get('uid')
    if not uid:
        return redirect(url_for('login'))

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True, buffered=True)
    try:
        cursor.execute("""
            SELECT requests.*, files.filename, user.name AS owner_name
            FROM requests
            JOIN files ON requests.fileid = files.fid
            JOIN user ON files.uid = user.uid
            WHERE requests.rid = %s
        """, (uid,))
        my_requests = cursor.fetchall()
        return render_template('yourrequest.html', my_requests=my_requests)
    finally:
        cursor.close()
        connection.close()

# ------------------- VIEW REQUESTS FOR OWNER (TO APPROVE/DENY + UNBLOCK) -------------------

@app.route('/requests', methods=["GET"])
def get_requests():
    uid = session.get('uid')
    if not uid:
        return redirect(url_for('login'))

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True, buffered=True)
    try:
        # MODIFIED: Only show requests where BOTH Server A and Server B have approved
        # This is Step 4 of the 3-step approval chain — file owner is the LAST approver
        cursor.execute("""
            SELECT r.id, r.rid, r.fileid, r.status AS request_status,
                   r.server_a_status, r.server_b_status,
                   f.filename,
                   u.name AS rname, u.email, u.uid AS ruid, u.status AS user_status
            FROM requests r
            JOIN files f ON r.fileid = f.fid
            JOIN user u ON r.rid = u.uid
            WHERE f.uid = %s
              AND r.server_b_status = 'approved'
        """, (uid,))
        requests_data = cursor.fetchall()
        return render_template('requests.html', requests=requests_data)
    finally:
        cursor.close()
        connection.close()

# ------------------- UNBLOCK USER -------------------

@app.route('/unblock_ajax/<int:uid>')
def unblock_ajax(uid):
    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("UPDATE user SET status='allowed' WHERE uid=%s", (uid,))
        connection.commit()

        if cursor.rowcount > 0:
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'message': 'User not found or already allowed'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})
    finally:
        cursor.close()
        connection.close()

# ------------------- SEND KEY AFTER ACCEPTING REQUEST -------------------

@app.route('/send_key', methods=['POST'])
def send_key():
    rid = request.form.get('rid')
    fid = request.form.get('fid')
    key = request.form.get('key')
    email = request.form.get('email')

    if not (rid and fid and key and email):
        flash("Missing data to send key", "danger")
        return redirect(url_for('get_requests'))

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        # Update request status to allowed and save the key
        cursor.execute("UPDATE requests SET status='allowed', skey=%s WHERE rid=%s AND fileid=%s", (key, rid, fid))
        connection.commit()

        # Send email with key
        try:
            send_email(email, key)
            flash(f"Key sent successfully to {email}", "success")
        except Exception as e:
            flash(f"Failed to send email: {str(e)}", "danger")

    finally:
        cursor.close()
        connection.close()

    return redirect(url_for('get_requests'))

# ------------------- APPROVE / DENY (old style, keep if needed) -------------------

@app.route('/allow/<int:rid>/<int:fid>')
def allow(rid, fid):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True, buffered=True)
    try:
        cursor.execute("SELECT * FROM files WHERE fid=%s", (fid,))
        file = cursor.fetchone()
        if not file:
            return "File not found", 404

        # Update request to allowed and send key
        cursor.execute("UPDATE requests SET status='allowed', skey=%s WHERE rid=%s AND fileid=%s",
                       (file['skey'], rid, fid))
        connection.commit()

        cursor.execute("SELECT * FROM user WHERE uid=%s", (rid,))
        user = cursor.fetchone()
        if user:
            send_email(user['email'], file['skey'])

        flash(f"Request approved! Key sent to {user['email']}", "success")
        return redirect(url_for('get_requests'))
    finally:
        cursor.close()
        connection.close()

@app.route('/deny/<int:rid>/<int:fid>')
def deny(rid, fid):
    connection = get_db_connection()
    cursor = connection.cursor(buffered=True)
    try:
        cursor.execute("UPDATE requests SET status='denied' WHERE rid=%s AND fileid=%s", (rid, fid))
        connection.commit()
        flash("Request denied!", "warning")
        return redirect(url_for('get_requests'))
    finally:
        cursor.close()
        connection.close()

# ------------------- DOWNLOAD FILE -------------------

@app.route('/download/<int:fid>', methods=["POST"])
def download(fid):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True, buffered=True)
    current_date = datetime.now().date()
    ipaddress = getip()
    try:
        skey = request.form.get('key')
        cursor.execute("SELECT * FROM files WHERE fid=%s", (fid,))
        file = cursor.fetchone()
        if not file:
            return "File not found", 404

        if skey == file['skey']:
            filepath = file['filepath']
            if os.path.exists(filepath):
                with open(filepath, "rb") as f:
                    encrypted_content = f.read()
                decrypted_content = fernet.decrypt(encrypted_content)
                file_stream = BytesIO(decrypted_content)
                file_stream.seek(0)

                cursor.execute("INSERT INTO downloads (ownerid, uid, uname, filename, date) VALUES (%s,%s,%s,%s,%s)",
                               (file['uid'], session['uid'], session['uname'], file['filename'], current_date))
                connection.commit()

                return send_file(file_stream, as_attachment=True, download_name=file['filename'])
            else:
                return "File missing on server", 404
        else:
            session['wrong'] = session.get('wrong', 0) + 1
            if session['wrong'] >= 3:
                cursor.execute("UPDATE user SET status='blocked' WHERE uid=%s", (session['uid'],))
                cursor.execute("INSERT INTO intrusion (ownerid, uid, uname, ipaddress, filename, date) VALUES (%s,%s,%s,%s,%s,%s)",
                               (file['uid'], session['uid'], session['uname'], ipaddress, file['filename'], current_date))
                connection.commit()
                # Send email warning for wrong download key intrusion
                cursor.execute("SELECT email FROM user WHERE uid=%s", (session['uid'],))
                u = cursor.fetchone()
                if u and u.get('email'):
                    send_intrusion_email(
                        u['email'], session['uname'], ipaddress,
                        datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    )
                session.pop('wrong', None)
                return redirect(url_for('logout'))
            flash("Wrong key entered!", "warning")
            return redirect(url_for('dashboard'))
    finally:
        cursor.close()
        connection.close()

# ------------------- DOWNLOADS LIST -------------------

@app.route('/downloads')
def downloads_list():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True, buffered=True)
    try:
        cursor.execute("SELECT * FROM downloads")
        data = cursor.fetchall()
        return render_template('totaldownloads.html', data=data)
    finally:
        cursor.close()
        connection.close()

# ------------------- INTRUSIONS -------------------

@app.route('/intrusions')
def intrusions_list():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True, buffered=True)
    try:
        cursor.execute("""
            SELECT i.ownerid, i.uname, i.ipaddress,
                   i.filename, i.date, u.uid, u.status
            FROM intrusion i
            JOIN user u ON i.uid = u.uid
        """)
        data = cursor.fetchall()
        return render_template('intruders.html', data=data)
    finally:
        cursor.close()
        connection.close()


# =================== SERVER A ROUTES (3-Step Approval Chain) ===================

# --- Server A Login ---
@app.route('/server_a/login', methods=['GET', 'POST'])
def server_a_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check against hardcoded Server A credentials
        if username == SERVER_A_CREDS['username'] and password == SERVER_A_CREDS['password']:
            session['server_role'] = 'server_a'  # Track login in session
            flash('Server A login successful!', 'success')
            return redirect(url_for('server_a_dashboard'))
        else:
            flash('Invalid Server A credentials', 'danger')
            return redirect(url_for('server_a_login'))

    return render_template('server_a_login.html')

# --- Server A Dashboard ---
# Shows ALL requests where status='pending' AND server_a_status='pending'
@app.route('/server_a/dashboard')
def server_a_dashboard():
    # Protect route — redirect to login if not logged in as server_a
    if session.get('server_role') != 'server_a':
        flash('Please login as Server A first.', 'warning')
        return redirect(url_for('server_a_login'))

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True, buffered=True)
    try:
        # Fetch requests that are waiting for Server A approval (Step 2)
        cursor.execute("""
            SELECT r.id, r.rid, r.rname, r.fileid, r.status,
                   r.server_a_status, r.server_b_status,
                   f.filename,
                   u.name AS owner_name
            FROM requests r
            JOIN files f ON r.fileid = f.fid
            JOIN user u ON f.uid = u.uid
            WHERE r.status = 'pending' AND r.server_a_status = 'pending'
        """)
        requests_data = cursor.fetchall()
        return render_template('server_a_dashboard.html', requests=requests_data)
    finally:
        cursor.close()
        connection.close()

# --- Server A Approve ---
# Sets server_a_status='approved' so the request moves to Server B
@app.route('/server_a/approve/<int:request_id>')
def server_a_approve(request_id):
    if session.get('server_role') != 'server_a':
        return redirect(url_for('server_a_login'))

    connection = get_db_connection()
    cursor = connection.cursor(buffered=True)
    try:
        cursor.execute("UPDATE requests SET server_a_status='approved' WHERE id=%s", (request_id,))
        connection.commit()
        flash('Request approved by Server A! Forwarded to Server B.', 'success')
    except Exception as e:
        flash(f'Error approving request: {str(e)}', 'danger')
    finally:
        cursor.close()
        connection.close()
    return redirect(url_for('server_a_dashboard'))

# --- Server A Deny ---
# Sets status='denied' — the entire approval flow STOPS here
@app.route('/server_a/deny/<int:request_id>')
def server_a_deny(request_id):
    if session.get('server_role') != 'server_a':
        return redirect(url_for('server_a_login'))

    connection = get_db_connection()
    cursor = connection.cursor(buffered=True)
    try:
        cursor.execute("UPDATE requests SET status='denied' WHERE id=%s", (request_id,))
        connection.commit()
        flash('Request denied by Server A.', 'warning')
    except Exception as e:
        flash(f'Error denying request: {str(e)}', 'danger')
    finally:
        cursor.close()
        connection.close()
    return redirect(url_for('server_a_dashboard'))

# --- Server A Logout ---
@app.route('/server_a/logout')
def server_a_logout():
    session.pop('server_role', None)  # Clear only the server role
    flash('Logged out from Server A.', 'info')
    return redirect(url_for('server'))


# =================== SERVER B ROUTES (3-Step Approval Chain) ===================

# --- Server B Login ---
@app.route('/server_b/login', methods=['GET', 'POST'])
def server_b_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check against hardcoded Server B credentials
        if username == SERVER_B_CREDS['username'] and password == SERVER_B_CREDS['password']:
            session['server_role'] = 'server_b'  # Track login in session
            flash('Server B login successful!', 'success')
            return redirect(url_for('server_b_dashboard'))
        else:
            flash('Invalid Server B credentials', 'danger')
            return redirect(url_for('server_b_login'))

    return render_template('server_b_login.html')

# --- Server B Dashboard ---
# Shows requests where server_a_status='approved' AND server_b_status='pending'
@app.route('/server_b/dashboard')
def server_b_dashboard():
    # Protect route — redirect to login if not logged in as server_b
    if session.get('server_role') != 'server_b':
        flash('Please login as Server B first.', 'warning')
        return redirect(url_for('server_b_login'))

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True, buffered=True)
    try:
        # Fetch requests that Server A approved, waiting for Server B (Step 3)
        cursor.execute("""
            SELECT r.id, r.rid, r.rname, r.fileid, r.status,
                   r.server_a_status, r.server_b_status,
                   f.filename,
                   u.name AS owner_name
            FROM requests r
            JOIN files f ON r.fileid = f.fid
            JOIN user u ON f.uid = u.uid
            WHERE r.server_a_status = 'approved' AND r.server_b_status = 'pending'
        """)
        requests_data = cursor.fetchall()
        return render_template('server_b_dashboard.html', requests=requests_data)
    finally:
        cursor.close()
        connection.close()

# --- Server B Approve ---
# Sets server_b_status='approved' so the request moves to the File Owner
@app.route('/server_b/approve/<int:request_id>')
def server_b_approve(request_id):
    if session.get('server_role') != 'server_b':
        return redirect(url_for('server_b_login'))

    connection = get_db_connection()
    cursor = connection.cursor(buffered=True)
    try:
        cursor.execute("UPDATE requests SET server_b_status='approved' WHERE id=%s", (request_id,))
        connection.commit()
        flash('Request approved by Server B! Forwarded to File Owner.', 'success')
    except Exception as e:
        flash(f'Error approving request: {str(e)}', 'danger')
    finally:
        cursor.close()
        connection.close()
    return redirect(url_for('server_b_dashboard'))

# --- Server B Deny ---
# Sets status='denied' — the entire approval flow STOPS here
@app.route('/server_b/deny/<int:request_id>')
def server_b_deny(request_id):
    if session.get('server_role') != 'server_b':
        return redirect(url_for('server_b_login'))

    connection = get_db_connection()
    cursor = connection.cursor(buffered=True)
    try:
        cursor.execute("UPDATE requests SET status='denied' WHERE id=%s", (request_id,))
        connection.commit()
        flash('Request denied by Server B.', 'warning')
    except Exception as e:
        flash(f'Error denying request: {str(e)}', 'danger')
    finally:
        cursor.close()
        connection.close()
    return redirect(url_for('server_b_dashboard'))

# --- Server B Logout ---
@app.route('/server_b/logout')
def server_b_logout():
    session.pop('server_role', None)  # Clear only the server role
    flash('Logged out from Server B.', 'info')
    return redirect(url_for('server'))


# ------------------- LOGOUT -------------------

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# ------------------- RUN -------------------

if __name__ == '__main__':
    app.run(debug=True, port=5001)
