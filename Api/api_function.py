import sys

from flask import jsonify
from time import gmtime, time, ctime, strptime, mktime
from Api.protocol import UN_ERROR, LEAD_ERROR, BASEDIR, DOMAIN_NAME
import calendar

DAYS_HEBREW = {
    "Sun": "ראשון",
    "Mon": "שני",
    "Tue": "שלישי",
    "Wed": "רביעי",
    "Thu": "חמישי",
    "Fri": "שישי",
    "Sat": "שבת"
}


def contain_html_entities(_str:str)-> bool:
    return "<" in _str or ">" in _str or "</" in _str



def check_level_new_lead(level:str, value:str) -> tuple[int, jsonify]:
    __err = dict(LEAD_ERROR)
    __suc = {"success":True}
    # /* first
    if value == "error" or level == "-1":
        return 0, jsonify(UN_ERROR)

    # /* from 1 to 10
    if level == "1":
        return 1, jsonify(__suc)
    elif level == "2":
        if not (2 <= value.__len__() < 20) and not contain_html_entities(value):
            __err['notice'] = "השם קצר/ארוך מידיי"
            return 0, jsonify(__err)


    elif level == "3":
        if value.__len__() != 10 or not value.isdigit():
            __err['notice'] = " מספר פלאפון לא קיים"
            return 0, jsonify(__err)
    elif level == "4":
        # /* id : pass now
        if value.__len__() > 10 or not idValid(value):
            __err["notice"] = "תז לא תקינה"
            return 0, jsonify(__err)
    elif level == "5":
        # /* irrelevant
        pass
    elif level == "6":
        __err["notice"] = "התאריך שהוגדר עבר"
        try:
            if not value or not verify_date(value):
                return 0, jsonify(__err)
        except (ValueError, Exception):
            return 0, jsonify(__err)
    elif level == "7":
        if not (2 < value.__len__() < 100) and not contain_html_entities(value):
            __err["notice"] = "הכתובת שצויינה לא ברורה"
            return 0, jsonify(__err)
    elif level == "8":
        try:
            value = float(value)
        except ValueError:
            # /* float error */
            value = ""
        if not isinstance(value, float):
            __err['notice'] = "מקדמה לא תקינה"
            return 0, jsonify(__err)
    elif level == "9":
        if not value.isdigit():
            __err['notice'] = "סך כולל לא תקין"
            return 0, jsonify(__err)
    elif level == "10":
        if not value.isdigit():
            __err["notice"] = 'הוצאות דלק שגוי'
            return 0, jsonify(__err)
    elif level == "11":
        if not value.isdigit():
            __err["notice"] = "הוצאות עובדים לא תקין"
            return 0, jsonify(__err)
    elif level == "12":
        if not value.isdigit() or int(value) > 3:
            __err["notice"] = 'אמצעי תשלום לא תקין'
            return 0, jsonify(__err)
    return 1, jsonify(__suc)

def verify_date(value):
    _time = gmtime()
    value = value.split("-")
    year:bool   = int(value[0]) >= _time.tm_year
    month       = int(value[1]) >= _time.tm_mon
    month_equal = int(value[1]) == _time.tm_mon
    day         = int(value[2]) >= _time.tm_mday
    if (not year) or (not month) or (not day and month_equal):
        return False

    return True


class FormatTime:
    def __init__(self, _time:float, _now:float=0):
        self.original = _time
        self.date = gmtime(_time)
        if not _now or _now < _time:
            self.now = gmtime(time())
            self._now = _now
        else:
            self.now = gmtime(_now)
            self._now = _now

        self.text = "{type} {BOL} {ft}"

    def is_year(self):
        nm = self.now.tm_mon
        dm = self.date.tm_mon
        return self.date.tm_year == self.now.tm_year or (self.date.tm_year+1 == self.now.tm_year and nm < dm)

    def is_six_month(self):
        sm = 6 * 30 * 24 * 60 * 60
        result = abs(self._now - self.original)
        return result <= sm

    def is_month(self):
        nm = self.now.tm_mon
        dm = self.date.tm_mon
        nd = self.now.tm_mday
        dd = self.date.tm_mday
        return self.is_year() and dm == nm or (dm+1 == nm and nd<dd)

    def is_today(self):
        nd = self.now.tm_mday
        dd = self.date.tm_mday
        nh = self.now.tm_hour
        dh = self.date.tm_hour
        return self.is_month() and nd==dd or (dd+1 == nd and nh <dh)

    def is_year_abs(self):
        return self.date.tm_year == self.now.tm_year

    def is_month_abs(self):
        nm = self.now.tm_mon
        dm = self.date.tm_mon
        return self.is_year_abs() and dm == nm

    def is_today_abs(self):
        nd = self.now.tm_mday
        dd = self.date.tm_mday
        return self.is_month_abs() and nd==dd

    def is_hour(self):
        nh = self.now.tm_hour
        dh = self.date.tm_hour
        nm = self.now.tm_min
        dm = self.date.tm_min
        return self.is_today() and nh == dh or (dh+1 == nh and nm<dm)

    def get_minute(self) -> int:
        return (self.now.tm_min - self.date.tm_min)%60

    def get_hour(self):
        return (self.now.tm_hour - self.date.tm_hour)%24

    def get_day(self):
        return (self.now.tm_mday - self.date.tm_mday)%30

    def get_month(self):
        return (self.now.tm_mon - self.date.tm_mon)%12

    def get_year(self):
        if not self.is_year():
            return self.now.tm_year - self.date.tm_year

    def get_format_before_time(self, t="לפני"):
        
        if self.is_hour():
            return self.text.format(type=t, BOL=self.get_minute(), ft="דקות")
        elif self.is_today():
            return self.text.format(type=t, BOL=self.get_hour(), ft="שעות")
        elif self.is_month():
            return self.text.format(type=t, BOL=self.get_day(), ft="ימים")
        elif self.is_year():
            return self.text.format(type=t, BOL=self.get_month(), ft="חודשים")
        elif not self.is_year():
            return self.text.format(type=t, BOL=self.get_year(), ft="שנים")


    @staticmethod
    def make_time(date:str):
        """
        required format %Y-%m-%d
        :param date:
        :return:
        """
        _format = '%Y-%m-%d'
        return float(mktime(strptime(date, _format)))

    @staticmethod
    def get_name_day_and_date(_time):
        """

        :param _time: format YYYY.MM.DD
        :return:
        """
        time_float = float(mktime(strptime(_time, "%Y-%m-%d"))) + (3400 * 24)
        day = "יום " + DAYS_HEBREW[ctime(time_float).split(" ")[0]]
        date_l = gmtime(time_float)
        return f"{day} {date_l.tm_mday}.{date_l.tm_mon}.{date_l.tm_year}"

    @staticmethod
    def get_days_left(date):
        day, month, year = date.split(".")
        year = int(year)
        month = int(month)
        day = int(day)

        # israel
        tn = gmtime(time())
        if tn.tm_year == year and tn.tm_mon  == month:
            if tn.tm_mday <= day:
                return day - tn.tm_mday
        elif tn.tm_year == year or tn.tm_mon <month:
            return 30
        return -1

    def get_days_month(self) -> int:
        return calendar.monthrange(self.date.tm_year, self.date.tm_mon)[1]
def get_clear_money(payment:int|str):
    return int(payment)-990.90


def check_equipment(data:dict[str]) -> tuple[bool, str]:
    name:str = data.get("name")
    price:str = data.get("price", "")
    exist:str = data.get("exist", "")

    if not name or name.__len__() > 15 or contain_html_entities(name):
        return False, "שם ארוך מידיי"
    if not price or not price.isdigit():
        return False, "מחיר לא תקין"
    if not exist or not exist.isdigit():
        return False, "כמות לא תקינה"

    # SUCCESS
    return True, ""


def generate_invoice_path(client_phone):
    now = gmtime(time())
    if sys.platform == 'linux':
        base = f"{BASEDIR}/invoices/"
    elif sys.platform == 'win32':
        base = f"{BASEDIR}\\invoices\\"

    return f"{base}{client_phone.replace(' ', '_')}_{now.tm_mon}-{now.tm_year}.pdf"


def generate_link_edit_agree(cid:str, aid:str) -> str:
    return f"/agreement/?cid={cid}&aid={aid}"

def generate_link_show_agree(si, cid) -> str:
    return f"/agreement/?si={si}&cid={cid}"

def XOR(value , key:str) -> bytes:
    key = key + (key[0] * (value.__len__() - key.__len__()))
    if isinstance(value, str):
        return xor_from_str(value, key)
    elif isinstance(value, bytes):
        return xor_from_bytes(value, key)

    return bytes()

def xor_from_bytes(value:bytes, key:str):
    re = b""
    for v, k in zip(value, key):
        re += (v ^ ord(k)).to_bytes(1, "big")
    return re

def xor_from_str(value:str, key:str):
    re = b""
    for v, k in zip(value, key):
        re += chr(ord(v) ^ ord(k)).encode()
    return re


def idValid(_id: str):

    if _id.__len__() > 9 or not _id.isdigit():
        return 0

    size_of_id = 0
    for index, number in enumerate(_id):
        num_id = int(number)
        result = str(num_id * ((index % 2)+1))
        if result.__len__() % 2 == 0:
            result = str(int(result[0])+int(result[1]))
        size_of_id += int(result)

    return size_of_id % 10 == 0


def verify_mail(mail:str) -> int:
    lmail = mail.split("@")
    if '@' not in mail or " " in mail:
        return 0
    elif not len(lmail) == 2:
        return 0
    elif not lmail[0]:
        return 0
    elif "." not in lmail[1]:
        return 0

    return 1

