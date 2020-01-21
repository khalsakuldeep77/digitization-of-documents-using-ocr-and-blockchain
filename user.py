from flask import Flask, render_template, request, session, redirect, url_for
import sqlite3 as sql
from werkzeug import secure_filename
from flask import Flask, render_template, request,make_response,Response
from werkzeug import secure_filename
from hashlib import sha256
import os, io
import requests
import json
from google.cloud import vision
import pandas as pd
import hashlib
import base64
import nltk
from google.cloud import language_v1
from google.cloud.language_v1 import enums
import os
addcaseglobal=""
policecaseglobal=""
def sample_analyze_entities(text_content):
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = r"SIH2020-36eec6e923ed.json"
    total_output=""
    client = language_v1.LanguageServiceClient()
    type_ = enums.Document.Type.PLAIN_TEXT
    language = "en"
    document = {"content": text_content, "type": type_, "language": language}
    encoding_type = enums.EncodingType.UTF8
    response = client.analyze_entities(document, encoding_type=encoding_type)
    for entity in response.entities:
        total_output+=u"Representative name for the entity: {}".format(entity.name)+"\n"
        total_output+=u"Entity type: {}".format(enums.Entity.Type(entity.type).name)+"\n"
        for metadata_name, metadata_value in entity.metadata.items():
            total_output+=u"{}: {}".format(metadata_name, metadata_value)+"\n"
    return total_output

app = Flask(__name__)
app.secret_key = "hello"
global_mega_user=""
add_doc_list=[]

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = r"ServiceAccountToken.json"
client = vision.ImageAnnotatorClient()
def write_to_documents(ocr_path,hash,original_path,block,new_file_path):
    conn = sql.connect('database1.db')
    c = conn.cursor()
    c.execute("INSERT INTO  documents(case_id,ocr_path, hash, original_path, block,important_path) VALUES (?,?, ?, ?, ?,?)",
          (addcaseglobal,ocr_path, hash, original_path, block,new_file_path))

    conn.commit()
    c.close()
    conn.close()

@app.route('/')
def home():
   return render_template('index.html')

@app.route('/register')
def register():
   return render_template('register.html')

@app.route('/adduser',methods = ['POST', 'GET'])
def adduser():
    if request.method == 'POST':
        try:
            fname = request.form['fname']
            lname = request.form['lname']
            position = request.form['position']
            address = request.form['address']
            contact = request.form['contact']
            email = request.form['email']
            password = request.form['password']
         
            with sql.connect("database2.db") as con:
                cur = con.cursor()
            
                cur.execute("INSERT INTO users (fname,lname,position,address,email,password,contact) VALUES (?,?,?,?,?,?,?)",(fname,lname,position,address,email,password,contact) )
            
                con.commit()
                cur.close()
            msg = "Record successfully added"
        except:
            con.rollback()
            msg = "error in insert operation"
      
        finally:
            return render_template("index.html",msg = msg)
            con.close()

def query_designation(email):
    #return row[0]
    conn=sql.connect('database2.db')
    c=conn.cursor()
    statement='SELECT position FROM users WHERE email = "{}"'.format(email)
    #print(statement)
    c.execute(statement)
    data=c.fetchall()
    #for row in data:
        #print(row)

    c.close()
    conn.close()
    return data[0]

def verify_from_database(username,password):
    users=dict()
    conn=sql.connect('database2.db')
    c=conn.cursor()
    var=False
    c.execute('SELECT * FROM users')
    data=c.fetchall()
    for row in data:
        users[row[5]]=row[6]
    for key,value in users.items():
        if username == key and password == value:
            return query_designation(username)
    if var == False:
        return False

def read_for_police_officer(officer):
    conn=sql.connect('database2.db')
    c=conn.cursor()
    statement='SELECT * FROM cases WHERE assignedBy = "{}"'.format(officer)
    c.execute(statement)
    data=c.fetchall()
    #for row in data:
        #print(row)
    return data

def read_for_investigation_officer(officer):
    conn=sql.connect('database2.db')
    c=conn.cursor()
    statement='SELECT * FROM cases WHERE assignedTo = "{}"'.format(officer)
    c.execute(statement)
    data = c.fetchall()
    #for row in data:
        #print('From Database:')
        #print(row)
    return data

@app.route('/loginresult',methods=['POST','GET'])
def loginresult():
    global global_mega_user
    if request.method == 'POST':
        username=request.form['email']
        session["username"] = username
        global_mega_user=username
        print(global_mega_user)
        password=request.form['password']
        #print(read_for_investigation_officer(global_mega_user))
        if "username" in session:
            if verify_from_database(username,password)[0] == 'policeOff':
                return render_template('police_dashboard.html',data = read_for_police_officer(username))
            elif verify_from_database(username,password)[0] == 'investigationOff':
                return render_template('investigation_dashboard.html',data=read_for_investigation_officer(username))
        else:
            #return 'Login Unsuccessful!'
            return render_template('index.html')

@app.route('/addcase',methods=['POST','GET'])
def addcase():
    global addcaseglobal
    if "username" in session:
        global add_doc_list
        username = session["username"]
        if request.method == 'POST':
            case_number = request.form['case_id']
            addcaseglobal=case_number
            case_title = request.form['case_title']
            investigation_officer = request.form['inv_off_name']
            conn=sql.connect('database2.db')
            c=conn.cursor()
            #statement='''INSERT INTO cases (cid,title,officer) VALUES (?,?,?) ,({},"{}","{}")'''.format(case_number,case_title,investigation_officer)
            #print(statement)
            
            
            c.execute("INSERT INTO cases (cid,title,assignedBy,assignedTo) VALUES (?,?,?,?)",(case_number,case_title,username,investigation_officer) )
            #c.execute(statement)
            conn.commit()
            c.close()
            conn.close()
            #print('Inserted Successfully')
            add_doc_list=[case_number,case_title,investigation_officer]
            return render_template('addDoc.html',case_number=case_number,case_title=case_title,investigation_officer=investigation_officer)
    else:
        return render_template('index.html')

@app.route('/addDoc',methods=['POST','GET'])
def addDoc():
    #global policecaseglobal
    if request.form == 'POST':
        case_number1=request.form['case_number']
        case_title1=request.form['case_title']
        investigation_officer1 = request.form['investigation_officer']
        #print(case_number1)
        return render_template('addDoc.html',case_number=case_number1,case_title=case_title1,investigation_officer=investigation_officer1)

@app.route('/police_dashboard')
def police_dashboard():
    if "username" in session:
        username = session["username"]
        #print (f"{username}")
        return render_template('police_dashboard.html')

    else:
        return render_template('index.html')
    #return render_template('police_dashboard.html')

@app.route('/investigation_dashboard')
def investigation_dashboard():
    if "username" in session:
        username = session["username"]
        #print (f"{username}")
        return render_template('investigation_dashboard.html')

    else:
        return render_template('index.html')
    #return render_template('police_dashboard.html')



@app.route('/uploader', methods = ['GET', 'POST'])
def upload_file2():
    if request.method == 'POST':
        #f = request.files['file']
        uploaded_files = request.files.getlist("file[]")
        #print(type(uploaded_files[0]))
        filenames=[]
        for f in uploaded_files:
            filenames.append(f.filename)


        total_data= ""
        for f in uploaded_files:
            filename=secure_filename(f.filename)
            image_path='sample_texts/'+str(filename)
            with io.open(image_path,'rb') as image_file:
                content=image_file.read()
            #content = f.read()
            image = vision.types.Image(content=content)

            response = client.text_detection(image=image)
            df = pd.DataFrame(columns=['locale', 'description'])
            texts = response.text_annotations
            for text in texts:
                df=df.append(dict(locale=text.locale,description=text.description),ignore_index=True)
            #print(df['description'][0])
            hashed_document=sha256(df['description'][0].encode()).hexdigest()
            #print(hashed_document)
            dictToSend = {'sender':'1ae00b38ac744f25b579247b911ed0ce','recipient':'someone-other-address','amount':hashed_document}
            res = requests.post('http://localhost:8000/transactions/new',json=dictToSend)
            #print('response from server:',res.text)
            res1 = requests.get('http://localhost:8000/mine')
            #print(res1)
            data=res1.json()
            text_file=open('saved_documents/'+filename+'.txt',"w")
            n=text_file.write(df['description'][0])
            text_file.close()
            ocr_path='saved_documents/'+filename+'.txt'
            f = open(ocr_path, "r")
            new =f.readlines()
            x=[]
            for i in range(len(new)):
                x.append(new[i].rstrip('\n'))
            new_string=''.join(x)
            #print(new_string)
            new_file_path='saved_documents/modified_'+filename+'.txt'
            file1 = open(new_file_path,"a")
            file1.write(new_string)
            file1.close()
            new_file_path='critical_information/'+filename+'.txt'
            file2=open(new_file_path,"a")
            file2.write(sample_analyze_entities(new_string))
            file2.close()
                        #generate_summary(ocr_path, 2)
            original_path='sample_texts/'+filename
            block=res.text
            write_to_documents(ocr_path,hashed_document,original_path,block,new_file_path)
            i=data['transactions'][0]
            #print(i)

            total_data += df['description'][0]+"<br><br><br>"
        return total_data

@app.route("/logout")
def logout():
    session.pop("username", None)
    return render_template('index.html')

@app.route("/investigationView", methods=['POST','GET'])
def investigationView():
    return render_template('investigationView.html')

@app.route("/certificate")
def certificate():
    return render_template('certificate.html')

if __name__ == '__main__':
    app.run(debug = True)
        