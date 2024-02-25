import sys
from datetime import timedelta

from flask import Flask
import os, binascii
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# /* db:name
FILE_NAME_DB = "dvir"

# /* first configuration db:save file, config:flask
m_app = Flask("dvir_dvora", template_folder="tmp")
m_app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{FILE_NAME_DB}"
m_app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False  # // default
m_app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=30)
m_app.secret_key = binascii.hexlify(os.urandom(25)).decode()
DBase: SQLAlchemy = SQLAlchemy(m_app)
migrate = Migrate(m_app, DBase)


# /* conf

get_random_key: callable = lambda: binascii.b2a_hex(os.urandom(5)).decode()
APP = {0:"IOS",
    1:"android"}
# /* api json
# /* global scope of flags
SESSIONS                = [{"ip":0, "session":"", "gone":False}]

# //** errors and notices **/

def getX(_id:int, suc=0, n=False) -> dict | str:
    _error = dict(success=bool(suc), title=TYPE_TITLE[suc], notice=BASE_NOTICE[_id])
    if n:
        return _error['notice']
    return _error

TYPE_TITLE = {
    0:"שגיאה",
    1:"הושלם",
    2:"שם לב",
    3:"משהו השתבש"
}
BASE_NOTICE = {
    0:"הסיסמה או השם לא מוכרים",
    1:"תרענן את הדף",
    2:"התחבר מחדש כדי להמשיך",
    3:"שגיאה בעת הוספת הציוד",
    4:"הלקוח נוסף לרשימה",
    5:"לא נמצאו פרטים",
    6: "פרטי עוסק פטור שגויים או שהלקוח שגוי",
    7: "צור קשר עם המערכת",
    8:"חוזה השכרה נקלט בהצלחה!",
    9:"הוסף ציוד לפני הוספת לקוח",
    10:"אחד מהנתונים חסר או לא תקין!",
    11: "ציוד לא מוכר",
    12: "נמחק או לא קיים",
    13:"משהו השתבש בציוד או בלקוח",
    14:"הלקוח לא חתם על החוזה",
    15: "הגדר חתימה ופרטי עוסק!",
    16:"שיחזור האירוע נכשל",
    17: "שגיאה במזהה לקוח",
    18:"detected: burpsuite/proxy",
    19: "קובץ גדול מידיי",
    20: "ייבוא הקובץ נכשל",
    21: "הקישור לא תקין",
    22: "מזהה חוזה לא תקין",
    23:"מזהה חוזה לא תקין",
    24:"פג תוקף הקישור",
    25:"מסמך זה נחתם ורשום במערכת",
    26:"לא ניתן לפתוח את חוזה השכרה",
    27:"החתימה קצרה מידיי",
    28:"התחבר מחדש",
    29:"שגיאה בזיהוי המנהל",
    30:"דואר לא תקין",
    31:"תעודת זהות שגויה",
    32:"השם קצר/ארוך מידיי",
    33:"מספר פלאפון לא קיים",
    34:"התאריך שהוגדר עבר",
    35:"הכתובת שצויינה לא ברורה",
    36:"מקדמה לא תקינה",
    37:"סך כולל לא תקין",
    38:'הוצאת דלק שגויה',
    39:"הוצאות עובדים לא תקין",
    40:'אמצעי תשלום לא תקין',
    41:"שם ארוך מידיי",
    42:"מחיר לא תקין",
    43:"כמות לא תקינה",
    44:"מזהה לא ידוע",
    45:"לא ניתן לעדכן אירוע סגור",
    46:"ציוד לא קיים",
    47:"תאריך לא תקין",
    48:"המיקום לא תקין",
    49:"הוצאה לא תקינה",
    50:"זוהה שינוי מכוון בחבילת המידע",
    51:'סכום לתשלום לא תקין',
    52:"שגיאה בעת מחיקת הציוד",
    53:"לקוח לא קיים",
    54:"הקישור פג תוקף",
    55:"הלקוח חתם על החוזה",
    56:"אין ציוד בהזמנה",
    57:"מזהה לקוח שגוי",
    58:"שגיאה בייבוא"






}



LOGIN_SUCCESS: dict     = {"success":True,  "title":None, "notice":None, 'location':'/dashboard'}

MAX_IMPORT_TXT          = 1000*100
FILENAME_IMPORT_TXT     = "equipment.txt"
FILENAME_EXPORT_TXT     = "equipment.txt"
AGREE_SESS_LIFE         = 960
# /** empty lead
EMPTY_LEAD_T            = "אין אירועים קרובים"
EMPTY_HISTORY           = "ההיסטוריה ריקה"
UNKNOWN:str = "unknown"
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
D_SETTING = {"ge":{"delete":False, "after":MONTH},
             "ce":{"complete":False}
             }


CON_FORM = "application/x-www-form-urlencoded"
CON_JSON = "application/json"
CON_ARGS = "a"
