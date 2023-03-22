from flask import jsonify
import time

from Api.databases import get_supply_by_id
from Api.protocol import UN_ERROR, LEAD_ERROR


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
        if not (4 <= value.__len__() < 10) :
            __err['notice'] = "השם קצר/ארוך מידיי"
            return 0, jsonify(__err)


    elif level == "3":
        if value.__len__() != 10 or not value.isdigit():
            __err['notice'] = "מספר הפלאפון לא קיים"
            return 0, jsonify(__err)
    elif level == "4":
        # /* id : pass now
        if value.__len__() > 10:
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
        if not (2 < value.__len__() < 100):
            __err["notice"] = "המיקום שהוכנס לא ברור"
            return 0, jsonify(__err)
    elif level == "8":
        if not value.isdigit() and value.__len__() != 0:
            __err['notice'] = "מקדמה לא תקינה"
            return 0, jsonify(__err)
    elif level == "9":
        if not value.isdigit():
            __err['notice'] = "סכום לא תקין"
            return 0, jsonify(__err)

    return 1, jsonify(__suc)


def verify_date(value):
    _time = time.gmtime()
    value = value.split("-")
    year:bool   = int(value[0]) >= _time.tm_year
    month       = int(value[1]) >= _time.tm_mon
    month_equal = int(value[1]) == _time.tm_mon
    day         = int(value[2]) >= _time.tm_mday
    if (not year) or (not month) or (not day and month_equal):
        return False

    return True





