from flask import Flask, render_template, request, redirect, url_for, session,jsonify,send_file
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
import openai
import os
import shutil

arr=[]  
app = Flask(__name__)
  
openai.api_key="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"
app.secret_key = 'xyzsdfg'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'user-system'
  
mysql = MySQL(app)
  
@app.route('/')
@app.route('/login', methods =['GET', 'POST'])
def login():
    mesage = ''
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email = request.form['email']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM user WHERE email = % s AND password = % s', (email, password, ))
        user = cursor.fetchone()
        if user:
            session['loggedin'] = True
            session['userid'] = user['userid']
            session['name'] = user['name']
            session['email'] = user['email']
            mesage = 'Logged in successfully !'
            return render_template('chat.html', mesage = mesage)
        else:
            mesage = 'Please enter correct email / password !'
    return render_template('login.html', mesage = mesage)
  
@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('userid', None)
    session.pop('email', None)
    if os.path.isfile("chat_history.txt"):
        os.remove("chat_history.txt")
    return redirect(url_for('login'))

@app.route('/new_register', methods =['GET', 'POST'])
def new_register():
    mesage = ''
    if request.method == 'POST' and 'name' in request.form and 'password' in request.form and 'email' in request.form and 'userID' in request.form:
        userID=request.form['userID']
        userName = request.form['name']
        password = request.form['password']
        email = request.form['email']

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM user WHERE email = % s', (email, ))
        account = cursor.fetchone()
        cursor.execute('SELECT * FROM user WHERE userid = %s', (userID,))
        result=cursor.fetchone()

        if account:
            mesage = 'Account already exists !'
        elif result:
            mesage='This User Name is Already Exits..! Try Another'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            mesage = 'Invalid email address !'
        elif not userName or not password or not email:
            mesage = 'Please fill out the form !'
        elif not userName.isalpha():
            mesage='Please Enter Only Alphabets in Name !'    
        else:
            cursor.execute('INSERT INTO user VALUES (% s, % s, % s, % s)', ( userID, userName, email, password, ))
            mysql.connection.commit()
            mesage = 'You have successfully registered !'
    elif request.method == 'POST':
        mesage = 'Please fill out the form !'
    return render_template('new_register.html', mesage = mesage)

def get_completion(prompt):
    print(prompt)
    with open("chat_history.txt", "a") as chat_file:
        chat_file.write(f"User:{prompt}\n")
    query = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a chatbot, Also At end of response make sentence complete"},
            {"role": "user", "content": prompt},
        ],
        max_tokens=100, 
        temperature=1,
        stop=["."],
    )
        # stop=None,
        # temperature=0.2,
    response=query.choices[0].message["content"]
    with open("chat_history.txt", "a") as chat_file:
        chat_file.write(f"Chabot:{response} \n")
    return response

@app.route("/query_view", methods=['POST', 'GET'])
def query_view():
    prompt = request.form['prompt']
    if request.method=='GET':
        print(arr)
        return render_template('chat.html')
    if request.method =='POST' and prompt.find('GET_RESOURCE') or bool(prompt.find('##')):
        if 'GET_RESOURCE' in prompt or '##' in prompt:
            if prompt=='GET_RESOURCE':
                with open("chat_history.txt", "a") as chat_file:
                    chat_file.write(f"User:{prompt} \n")
                link='<b>Select Course:</b><br><p>1.BBACA</p><br><p>2.BBA</p><br><p>3.BBAIB</p><br><p>Type ## and Course Name</p>'
                with open("chat_history.txt", "a") as chat_file:
                    chat_file.write(f"Chatbot:{link} \n")
                return jsonify({'response': link})
            if '##BBACA' in prompt or '##BBA' in prompt or '##BBAIB' in prompt:
                with open("chat_history.txt", "a") as chat_file:
                    chat_file.write(f"User:{prompt} \n")
                arr.append(prompt[2:])
                link1='<b>Select Course:</b><br><p>1.First Year</p><br><p>2.Second Year</p><br><p>3.Third Year</p><br><p>Type ## and send Year</p>'
                with open("chat_history.txt", "a") as chat_file:
                    chat_file.write(f"Chatbot:{link1} \n")
                return jsonify({'response': link1})
            if '##First' in prompt or '##Second' in prompt or '##Third' in prompt:
                with open("chat_history.txt", "a") as chat_file:
                    chat_file.write(f"User:{prompt} \n")
                arr.append(prompt[2:])
                link2='<b>Select Course:</b><br><p>1.1st SEM</p><br><p>2.2nd SEM</p><br><p>Type ## and send 1 or 2</p>'
                with open("chat_history.txt", "a") as chat_file:    
                    chat_file.write(f"Chatbot:{link2} \n")
                return jsonify({'response': link2})
            if '##1' in prompt or '##2' in prompt:
                with open("chat_history.txt", "a") as chat_file:    
                    chat_file.write(f"User:{prompt} \n")
                arr.append(prompt[2:])
                link3="<a href='/download_file' download>Download File</a><br><p>You Can Download Other Resources By Sending GET_RESOURCE or Ask Queries</p>"
                with open("chat_history.txt", "a") as chat_file:    
                    chat_file.write(f"Chatbot:{link3} \n")
                return jsonify({'response':link3})
    if request.method =='POST' and 'GET_CHAT' in prompt:
        download_link="<a href='/download_chat' download>Download Chat</a></p>"
        return jsonify({'response':download_link})
    if request.method == 'POST':
        print('step1')
        response = get_completion(prompt)
        print(response)
        return jsonify({'response': response})

@app.route('/download_chat')
def download_chat():
    chat_filename = 'chat_history.txt'

    if os.path.exists(chat_filename):
        return send_file(chat_filename, as_attachment=True, download_name='chat_history.txt')
    
    
@app.route('/download_file')
def download_file():
    print('this is downloadfile',arr)
    if arr[0]=='BBACA':
        if arr[1]=='First':
            if arr[2]=='1':
                file_path = 'BBACA_Sem1.zip'
                arr.clear()
                with open("chat_history.txt", "a") as chat_file:
                    chat_file.write(f'::::User Downloaded File {file_path}::::\n')
                return send_file(file_path, as_attachment=True)
            elif arr[2]=='2':
                file_path='BBACA_Sem2.zip'
                arr.clear()
                with open("chat_history.txt", "a") as chat_file:
                    chat_file.write(f'::::User Downloaded File {file_path}::::\n')
                return send_file(file_path,as_attachment=True)
        if arr[1]=='Second':
            if arr[2]=='1':
                file_path = 'BBACA_Sem3.zip'
                arr.clear()
                with open("chat_history.txt", "a") as chat_file:
                    chat_file.write(f'::::User Downloaded File {file_path}::::\n')
                return send_file(file_path, as_attachment=True)
            elif arr[2]=='2':
                file_path='BBACA_Sem4.zip'
                arr.clear()
                with open("chat_history.txt", "a") as chat_file:
                    chat_file.write(f'::::User Downloaded File {file_path}::::\n')
                return send_file(file_path,as_attachment=True)
        if arr[1]=='Third':
            if arr[2]=='1':
                file_path = 'BBACA_Sem5.zip'
                arr.clear()
                with open("chat_history.txt", "a") as chat_file:
                    chat_file.write(f'::::User Downloaded File {file_path}::::\n')
                return send_file(file_path, as_attachment=True)
            elif arr[2]=='2':
                file_path='BBACA_Sem6.zip'
                arr.clear()
                with open("chat_history.txt", "a") as chat_file:
                    chat_file.write(f'::::User Downloaded File {file_path}::::\n')
                return send_file(file_path,as_attachment=True) 
            

if __name__ == "__main__":
    app.run(debug=True)
