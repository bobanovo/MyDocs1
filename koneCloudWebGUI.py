from  MyDocs_config import * #configuration for all
from flask import Flask
from flask import render_template
from flask import request
from flask import session
from flask import redirect

import sqlite3

conn = sqlite3.connect(DB_DBNAME_SQLITE)
print ("Opened database successfully")
conn.close()

app= Flask (__name__)

@app.route('/')
def index():
    return render_template('GUIv1.html')
    

@app.route('/list')
def list():
    con = sqlite3.connect(DB_DBNAME_SQLITE)
    con.row_factory = sqlite3.Row

    cur = con.cursor()
    cur.execute("select * from "+DB_TBLNAME_SQLITE)

    rows = cur.fetchall(); 
    return render_template('GUIv1.html',rows = rows)

if __name__=='__main__':
    app.run(debug=True)