from flask import jsonify

from Api.protocol import UN_ERROR, LEAD_ERROR


def check_level_new_lead(level:str, value:str) -> jsonify:
    __err = dict(LEAD_ERROR)
    __suc = {"success":True}
    return jsonify(__suc)
    # /* first
    if value == "error" or level == "-1":
        return jsonify(UN_ERROR)

    # /* from 1 to 10
    if level == "1":
        return jsonify(__suc)
    elif level == "2":
        if value.__len__() < 4:
            __err['notice'] = "השם קצר מידיי"
            return jsonify(__err)


    elif level == "3":
        if value.__len__() != 10 or not value.isdigit():
            __err['notice'] = "מספר הפלאפון לא קיים"
            return jsonify(__err)
    elif level == "4":
        # /* id : pass now
        pass
    elif level == "5":
        pass
    elif level == "6":
        pass
    elif level == "7":
        pass
    elif level == "8":
        pass
    elif level == "9":
        pass
    elif level == "10":
        pass

    return jsonify(__suc)
