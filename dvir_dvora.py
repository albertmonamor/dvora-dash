from json import loads, dumps
from time import sleep
from Api.api_function import check_level_new_lead, get_clear_money, check_equipment
from Api.protocol import m_app, get_random_key, LOGIN_FAILED, LOGIN_SUCCESS, UN_ERROR, EMPTY_LEAD_T, T404, TMP_DENIED, \
    LEAD_ERROR, EQUIP_ERROR, EQUIP_SUCCESS, UPDATE_EQUIP_ERR
from flask import render_template, request, render_template_string, session, jsonify, redirect, url_for
from Api.databases import Users, DBase, signup, db_new_lead, add_supply, get_all_supply, verify_supply, \
    get_all_leads_open, time, SUPPLY, get_supply_by_id, generate_id_supply


#  ******************* ROUTES *************************

@m_app.errorhandler(404)
def _404(n_error):
    return render_template("./error_tmp/404.html")


# @m_app.errorhandler(500)
# def _500(n_error):
#     pass


# response: <html template>                  << HTML
@m_app.route("/index",  methods=['GET'])
@m_app.route("/",       methods=['GET'])
@m_app.route("/home",   methods=['GET'])

def index():
    if session.get('sess-login') and session.get('is_admin', None):
        return redirect(url_for("dashboard"))
    session['sess-login'] = get_random_key()
    return render_template("login.html", key=session['sess-login'])


# response: <json>                           << API
@m_app.route('/login', methods=['POST'])
def login():
    if not session.get('sess-login'):
        return jsonify(UN_ERROR)

    if session.get('is_admin'):return jsonify(LOGIN_SUCCESS)
    user= request.form.get("user", "?").lower()
    pwd = request.form.get('pwd')
    key = request.form.get('key')
    in_db = Users.query.filter_by(user=user).first()
    if key == session['sess-login'] and in_db and in_db.pwd == pwd:
        session['is_admin'] = True
        session['user']     = user
        del session['sess-login']
        print(request.remote_user, request.remote_addr, request.environ['REMOTE_ADDR'], request.environ.get('HTTP_X_FORWARDED_FOR'))
        return jsonify(LOGIN_SUCCESS)
    else:
        return jsonify(LOGIN_FAILED)

# response: <html template>                  << HTML
@m_app.route("/dashboard", methods=['GET'])
def dashboard():
    if not session.get("is_admin"):
        return redirect(url_for("index"))

    return render_template('dashboard.html')

@m_app.route("/template/<tmp>", methods=['POST'])
def get_template_dashboard(tmp):
    if not session.get('is_admin'):
        return jsonify(TMP_DENIED)

    res_tmp:str = T404
    name = "404"
    # /* <    *---MAIN TAB TEMPLATE---*    >
    if tmp == "0":
        res_tmp = "/dash_tmp/leads.html"
        return jsonify({"success":True,
                        "template":render_template(res_tmp, leads=get_all_leads_open(),empty_lead=EMPTY_LEAD_T),
                        "name":"לקוחות"})
    elif tmp == "1":
        res_tmp = "/dash_tmp/equipment.html"
        return jsonify({"success":True,
                        "template":render_template(res_tmp, equipment=get_all_supply()),
                        "name":"ציוד"})
    elif tmp == "2":
        res_tmp = "/dash_tmp/history.html"
        name = "היסטוריה"
    elif tmp == "3":
        res_tmp = "/dash_tmp/money.html"
        name = "הוצאות/הכנסות"
    elif tmp == "4":
        res_tmp = "/dash_tmp/setting.html"
        name = "הגדרות"
    elif tmp == '15':
        res_tmp = "/dash_tmp/add_lead.html"
        return jsonify({"success":True,
                        "template":render_template(res_tmp,user=session['user']),
                        "supply":get_all_supply(),
                        "welcome":render_template("/dash_tmp/wel_add_lead")})
    elif tmp == '16':
        res_tmp = "/dash_tmp/add_equip.html"
        return jsonify({"success":True,
                        "template":render_template(res_tmp, user=session['user']),
                        "welcome":render_template("/dash_tmp/wel_add_equip")})

    return jsonify({"success":True, "template":render_template(res_tmp), "name":name})

@m_app.route("/new_lead", methods=["POST"])
def new_lead():
    if not session.get("is_admin"):
        return jsonify(TMP_DENIED)

    level    = request.form.get("level", "-1") or "-1"
    value    = request.form.get('value', "error")
    return check_level_new_lead(level, value)[1]

@m_app.route("/add_lead", methods=["POST"])
def add_lead():
    sleep(1)
    res:dict = dict(LEAD_ERROR)
    if not session.get("is_admin"):
        return jsonify(TMP_DENIED)

    name       = request.form.get("name")       or 0
    phone      = request.form.get("phone")      or 0
    id_lead    = request.form.get("id_lead")    or -1
    equipment:str  = request.form.get("supply", "{}")
    date       = request.form.get("date")       or 0
    location   = request.form.get("location")   or 0
    sub_pay    = request.form.get("sub_pay")    or 0
    payment    = request.form.get("payment")    or 0
    if not any(request.form.values()):
        res["notice"] = "אחד מהנתונים חסר או לא ברור!"
        return jsonify(res)

    # // SUCCESS
    for _index, (k, v) in enumerate(request.form.items()):
        result:tuple[int, jsonify] = check_level_new_lead(str(_index+2), v)
        if isinstance(v, dict):continue
        if not result[0]:
            return result[1]

    # // SUCCESS
    equipment_is_ok, s_lead = verify_supply(loads(equipment))
    if not equipment_is_ok:
        return jsonify(EQUIP_ERROR)
    # // SUCCESS
    db_new_lead(write_by=session['user'],
                full_name=name,
                phone=phone,
                ID=id_lead,
                last_write=time(),
                event_supply=dumps(s_lead),
                event_date=date,
                event_place=location,
                determine_money=sub_pay,
                pay_sub=bool(sub_pay),
                total_money=payment,
                order_equip=bool(s_lead),
                is_open=True,
                clear_money=get_clear_money(payment))
    # add data to database
    return jsonify(EQUIP_SUCCESS)

@m_app.route("/add_equipment", methods=["POST"])
def add_equipment():
    error = dict(UPDATE_EQUIP_ERR)

    if not session.get("is_admin"):
        return jsonify(TMP_DENIED)
    result = check_equipment(request.form)
    if not result[0]:
        error["notice"] = result[1]
        return jsonify(error)

    # add to the database
    add_supply(name=request.form["name"],
               price=int(request.form["price"]),
               exist=int(request.form["exist"]),
               desc="",
               _id=generate_id_supply(),
               count=0)
    return jsonify({"success":True})


@m_app.route("/update_equipment/<eq_id>", methods=["POST"])
def update_equipment(eq_id):
    error = dict(UPDATE_EQUIP_ERR)

    if not session.get("is_admin"):
        return jsonify(TMP_DENIED)

    result = check_equipment(request.form)
    if not result[0]:
        error["notice"] = result[1]
        return jsonify(error)

    equip = get_supply_by_id(eq_id)
    if not equip:
        error["notice"] = "ציוד לא מוכר"
        return jsonify(error)

    equip.name = request.form["name"]
    equip.price = int(request.form["price"])
    equip.exist = int(request.form["exist"])

    # update db
    DBase.session.commit()
    return jsonify({"success":True})


if __name__ == "__main__":
    with m_app.app_context():
        DBase.create_all()
    m_app.run(host="0.0.0.0", port=80, debug=True)

