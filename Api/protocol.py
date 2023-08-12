import sys
from datetime import timedelta

from flask import Flask
import os, binascii
from flask_sqlalchemy import SQLAlchemy


# /* db:name
FILE_NAME_DB = "dvir"

# /* first configuration db:save file, config:flask
m_app = Flask("dvir_dvora", template_folder="tmp")
m_app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{FILE_NAME_DB}"
m_app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False  # // default
m_app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=30)
m_app.secret_key = binascii.hexlify(os.urandom(25)).decode()
DBase: SQLAlchemy = SQLAlchemy(m_app)


# /* conf

get_random_key: callable = lambda: binascii.b2a_hex(os.urandom(5)).decode()
APP = {0:"android"}
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
INVOICE_ACTION_ERR      = {"success":False,"title":"שגיאה בתהליך", "notice":"פרטי עוסק פטור שגויים או שהלקוח שגוי"}
UPDATE_LEAD_ERROR       = {"success":False,"title": "שגיאה בעדכון", "notice":""}
IMPORT_TXT_ERROR        = {"success":False,"title":"שגיאה בייבוא","notice":""}
AGREE_ERROR             = {"success":False,"title": " משהו השתבש", "notice":"צור קשר עם המערכת"}
SUCCESS_AGREE           = {"success":True, "title":"חוזה השכרה", "notice":"חוזה השכרה נקלט בהצלחה!"}
MAX_IMPORT_TXT          = 1000*100
FILENAME_IMPORT_TXT     = "equipment.txt"
FILENAME_EXPORT_TXT     = "equipment.txt"
AGREE_SESS_LIFE         = 960
# /** empty lead
EMPTY_LEAD_T            = "אין אירועים קרובים"
EMPTY_HISTORY           = "ההיסטוריה ריקה"
# /** templates
T404                    = "/error_tmp/404.html"

# time
DAY       = 3600*24
MONTH     = DAY*30
SIX_MONTH = MONTH*6
PDF_OPTIONS = {
    'encoding': 'UTF-8',
    'margin-left': '0mm',
    'margin-right': '0mm',
    'margin-bottom': '0mm',
    'margin-top': '0mm',
    'page-size': 'A4',
}
PATH_PDFKIT_EXE = r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe"
if sys.platform == "win32":
    BASEDIR         = "\\".join(os.getcwd().split("\\")[0:-1]) if os.getcwd().split("\\")[-1] !="dvora-dash" else os.getcwd()
else:
    BASEDIR         = "/home/dror/dvir-dvora"

DOMAIN_NAME     = "dror.pythonanywhere.com"
