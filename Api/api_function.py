from flask import jsonify
from time import gmtime, time, ctime, strptime, mktime
from Api.protocol import UN_ERROR, LEAD_ERROR


DAYS_HEBREW = {
    "Sun": "ראשון",
    "Mon": "שני",
    "Tue": "שלישי",
    "Wed": "רביעי",
    "Thu": "חמישי",
    "Fri": "שישי",
    "Sat": "שבת"
}



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
        if not (2 <= value.__len__() < 20) :
            __err['notice'] = "השם קצר/ארוך מידיי"
            return 0, jsonify(__err)


    elif level == "3":
        if value.__len__() != 10 or not value.isdigit():
            __err['notice'] = " מספר פלאפון לא קיים"
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
        if not value or not value.isdigit():
            __err['notice'] = "מקדמה לא תקינה"
            return 0, jsonify(__err)
    elif level == "9":
        if not value.isdigit():
            __err['notice'] = "סך כולל לא תקין"
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


def get_format_last_write(date:float):
    __now       = gmtime(time())
    date        = gmtime(date)
    is_year     = date.tm_year == __now.tm_year
    is_month    = date.tm_mon == __now.tm_mon
    week        = is_year and is_month
    today       = is_year and is_month and date.tm_mday == __now.tm_mday
    half_hour   = today and date.tm_hour == __now.tm_hour and ((60-__now.tm_min)+date.tm_min) > 30

    if half_hour:
        return "ממש עכשיו"
    elif today:
        return f"לפני {__now.tm_hour-date.tm_hour} שעות"
    elif week:
        return f"לפני {(__now.tm_mday-date.tm_mday)} ימים"
    elif is_year:
        return f"לפני {__now.tm_mon-date.tm_mon} חודשים"


def get_name_date_by_str(_time:str):
    """

    :param _time: from time()
    :return:
    """
    time_float = float(mktime(strptime(_time, "%Y-%m-%d")))+(3400*24)
    day = DAYS_HEBREW[ctime(time_float).split(" ")[0]]
    date_l = gmtime(time_float)
    return f"{day} {date_l.tm_mday}.{date_l.tm_mon}.{date_l.tm_year}"


def get_clear_money(payment:int|str):
    return int(payment)-990.90