from flask import Flask, render_template, request
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
current_user="Yash"
appointed_police='Gaurav'
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = r"ServiceAccountToken.json"
client = vision.ImageAnnotatorClient()
def write_to_documents(ocr_path,hash,original_path,block,new_file_path):
    conn = sql.connect('database1.db')
    c = conn.cursor()
    c.execute("INSERT INTO  documents(case_id,ocr_path, hash, original_path, block,important_path) VALUES (?,?, ?, ?, ?,?)",
          (1,ocr_path, hash, original_path, block,new_file_path))

    conn.commit()
    c.close()
    conn.close()


def query_designation(email):
    #return row[0]
    conn=sql.connect('database1.db')
    c=conn.cursor()
    statement='SELECT position FROM users WHERE email = "{}"'.format(email)
    print(statement)
    c.execute(statement)
    data=c.fetchall()
    #for row in data:
        #print(row)

    c.close()
    conn.close()
    return data[0]

def verify_from_database(username,password):
    users=dict()
    conn=sql.connect('database1.db')
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

def read_for_investigation_officer(officer):
    conn=sql.connect('database1.db')
    c=conn.cursor()
    statement='SELECT * FROM cases WHERE appointedto = "{}"'.format(officer)
    data=c.execute(statement)
    #for row in data:
        #print(row)
    return data



        #return 'Login Successful!'

@app.route('/')
def home():
   return render_template('index.html')

def read_for_police_officer(officer):
    conn=sql.connect('database1.db')
    c=conn.cursor()
    statement='SELECT * FROM cases WHERE appointedby = "{}"'.format(officer)
    c.execute(statement)
    data=c.fetchall()
    for row in data:
        print(row)
    return data

@app.route('/register')
def new_student():
   return render_template('register.html')

@app.route('/loginresult',methods=['POST','GET'])
def loginresult():
    global current_user
    if request.method == 'POST':
        username=request.form['email']
        password=request.form['password']
        print(verify_from_database(username,password)[0])
        if verify_from_database(username,password)[0] == 'policeOff':
            print(read_for_investigation_officer(appointed_police))
            return render_template('police_dashboard.html',data=read_for_police_officer(appointed_police))
        elif verify_from_database(username,password)[0] == 'investigationOff':
            print(read_for_investigation_officer(current_user))
            return render_template('investigation_dashboard.html',data=read_for_investigation_officer(current_user))
        else:
            return 'Login Unsuccessful!'



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

         with sql.connect("database1.db") as con:
            cur = con.cursor()

            cur.execute("INSERT INTO users (fname,lname,position,address,email,password,contact) VALUES (?,?,?,?,?,?,?)",(fname,lname,position,address,email,password,contact) )

            con.commit()
            msg = "Record successfully added"
      except:
         con.rollback()
         msg = "error in insert operation"

      finally:
         return render_template("index.html",msg = msg)
         con.close()



#    return render_template("addDoc.html")

@app.route('/addCase',methods=['POST','GET'])
def addCase():
    if request.method == 'POST':
        case_number = request.form['case_id']
        case_title = request.form['case_title']
        investigation_officer = request.form['inv_off_name']
        conn=sql.connect('database1.db')
        c=conn.cursor()
        #statement='''INSERT INTO cases (cid,title,officer) VALUES (?,?,?) ,({},"{}","{}")'''.format(case_number,case_title,investigation_officer)
        #print(statement)
        c.execute("INSERT INTO cases (cid,title,officer) VALUES (?,?,?)",(case_number,case_title,investigation_officer) )
        #c.execute(statement)
        conn.commit()
        c.close()
        conn.close()
        print('Inserted Successfully')
        return render_template('addDoc.html')
@app.route('/addDoc')
def addDoc():
    return render_template('addDoc.html')


@app.route('/uploader', methods = ['GET', 'POST'])
def upload_file2():
   if request.method == 'POST':
      #f = request.files['file']
      uploaded_files = request.files.getlist("file[]")
      print(type(uploaded_files[0]))
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
          print(df['description'][0])
          hashed_document=sha256(df['description'][0].encode()).hexdigest()
          print(hashed_document)
          dictToSend = {'sender':'1ae00b38ac744f25b579247b911ed0ce','recipient':'someone-other-address','amount':hashed_document}
          res = requests.post('http://localhost:8000/transactions/new',json=dictToSend)
          print('response from server:',res.text)
          res1 = requests.get('http://localhost:8000/mine')
          print(res1)
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
          print(new_string)
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
          print(i)

          total_data += df['description'][0]+"<br><br><br>"
      return total_data

def get_documents_from_db(case_id):
    conn=sql.connect('database1.db')
    cases=[]
    c=conn.cursor()
    query='SELECT * FROM documents WHERE case_id = '+case_id
    c.execute(query)
    data = c.fetchall()
    #print(data)
    for row in data:
        cases.append([row[0],row[1],row[3],row[5]])
        #cases_dict[str(row[0])]=row[1]
        #print(row)
    c.close()
    conn.close()
    return data

@app.route('/investigationView', methods=['POST', 'GET'])
def investigationView():
    if request.method == "POST":
        case_id = request.form['case_id']
        return render_template('investigationView.html', data=get_documents_from_db(case_id))


if __name__ == '__main__':
   app.run(debug = True)
