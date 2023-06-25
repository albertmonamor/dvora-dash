from contextlib import contextmanager

from flask import Flask
import http, os, binascii
from flask_sqlalchemy import SQLAlchemy


# /* db:name
FILE_NAME_DB = "dvir"

# /* first configuration db:save file, config:flask
m_app = Flask("dvir_dvora", template_folder="tmp")
m_app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{FILE_NAME_DB}"
m_app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False  # // default
m_app.secret_key = binascii.hexlify(os.urandom(25)).decode()
DBase: SQLAlchemy = SQLAlchemy(m_app)


# /* conf

get_random_key: callable = lambda: binascii.b2a_hex(os.urandom(5)).decode()

# /* api json
# /* global scope of flags
LOGIN_FAILED: dict      = {"success":False, "title":"שגיאה" , "notice": "הסיסמה או השם לא מוכרים"}
LOGIN_SUCCESS: dict     = {"success":True,  "title":None, "notice":None, 'location':'/dashboard'}
UN_ERROR: dict          = {"success":False, "title":"שגיאה", "notice":"תרענן את הדף"}
TMP_DENIED: dict        = {"success":False, "title":"שגיאת אימות","notice": "התחבר מחדש כדי להמשיך"}
LEAD_ERROR: dict        = {"success":False, "title":"שם לב!", "notice":None}
EQUIP_ERROR:dict        = {"success":False, "title":"שגיאת ציוד", "notice":"שגיאה בעת הוספת הציוד"}
EQUIP_SUCCESS:dict      = {"success":True, "title":"הושלם!", "notice":"הלקוח נוסף לרשימה"}
SEARCH_LEAD_ERR         = {"success":False,"title": "שגיאה בחיפוש", "notice":"לא נמצאו פרטים"}
# /** empty lead
EMPTY_LEAD_T            = "אין אירועים קרובים"
EMPTY_HISTORY           = "ההיסטוריה ריקה"
# /** templates
T404                    = "/error_tmp/404.html"



import pdfkit

# Specify the HTML content
html_content = """
<html>
<body>
    <h1>Hello, World!</h1>
    <p>This is a sample HTML content.</p>
</body>
</html>
"""

# Specify the output file path
output_path = "c:\\Users\\saban\\Desktop\\simple.pdf"

# Convert HTML to PDF
pdfkit.from_string(html_content, output_path)
pdfkit.from_string(html_content, output_path, configuration=pdfkit.configuration(wkhtmltopdf=r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'))
