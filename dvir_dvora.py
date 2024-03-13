from json import dumps
from werkzeug.datastructures import FileStorage

from Api.api_function import check_level_new_lead, check_equipment, verify_mail, idValid, getPostData
from Api.protocol import *
from flask import render_template, request, session, jsonify, redirect, url_for, \
    send_from_directory
from Api.databases import DBase, db_new_client, add_supply \
    , time, generate_id_supply, export_txt_equipment, import_txt_equipment

from Api.db_api import DBClientApi, DBUserApi, DBSupplyApi, DBAgreeApi, MoneyApi, DBSettingApi
from Api.jinja_function import *


# =============== MOBILE *********************

@m_app.route("/m/get_supply", methods=["POST"])
def mGetSupply():
    if not session.get("is_admin"):
        return jsonify(getX(DENIED))

    return jsonify({"success":True, "supply":DBSupplyApi.get_all_supply()})


# =========== END MOBILE *********************
@m_app.route("/l0g0ut", methods=["GET"])
def logout():
    if not session.get("is_admin"):
        return jsonify(LOGIN_SUCCESS)
    session.clear()
    return jsonify({"success":True})

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
    if session.get('is_admin'):return jsonify(LOGIN_SUCCESS)
    bdict = getPostData(request)
    user = bdict.get("user", "?").lower().replace(" ", "")
    pwd = bdict.get('pwd')
    key = bdict.get('key', 1)
    usr = DBUserApi(user)

    if (key == session.get('sess-login') or APP.get(key)) and usr.ok() and usr.u.pwd == pwd:
        session['is_admin'] = usr.u.is_admin
        session['user']     = user
        if session.get('sess-login'):
            del session['sess-login']
        return jsonify(LOGIN_SUCCESS)
    else:
        return jsonify(getX(E_AUTH))

# response: <html template>                  << HTML
@m_app.route("/dashboard", methods=['GET'])
def dashboard():
    if not session.get("is_admin"):
        return redirect(url_for("index"))

    return render_template('dashboard.html')

# ------------- API -------------------
@m_app.route("/template/<tmp>", methods=['POST'])
def get_template_dashboard(tmp):

    if not session.get('is_admin'):
        return jsonify(getX(DENIED))
    # /* default template */
    res_tmp:str = T404
    # /* default title */
    name = "404"
    # /* client id */
    bdict = getPostData(request)
    cid = bdict.get("identify", "C0")
    # /* Api Client */
    capi = DBClientApi(cid)
    # /* <    *---MAIN TAB TEMPLATE---*    >
    if tmp == "0":
        client_open = capi.get_all_client_by_mode("open")
        res_tmp = "/dash_tmp/leads.html"
        return jsonify({"success":True,
                        "template":render_template(res_tmp, leads=client_open,empty_lead=EMPTY_LEAD_T),
                        "name":"לקוחות"})
    elif tmp == "1":
        res_tmp = "/dash_tmp/equipment.html"
        session["nonce_import"] = get_random_key()
        return jsonify({"success":True,
                        "template":render_template(res_tmp, equipment=DBSupplyApi.get_all_supply(),
                                                   nonce_import=session["nonce_import"]),
                        "name":"ציוד"})
    elif tmp == "2":
        client_open = capi.get_all_client_by_mode("both")
        res_tmp = "/dash_tmp/history.html"
        return jsonify({"success":True,
                        "template":render_template(res_tmp, leads=client_open,empty_history=EMPTY_HISTORY),
                        "name":"היסטוריה"})
    elif tmp == "3":
        res_tmp = "/dash_tmp/money.html"
        name = "הוצאות/הכנסות"
        mapi = MoneyApi('none')
        sapi = DBSupplyApi("none")
        return jsonify({"success": True,
                        "template": render_template(res_tmp,
                                                    equip_exist=sapi.get_n_equipment_exist(),
                                                    c_complete=mapi.get_n_c_complete_ut(),
                                                    all_p=mapi.get_p_until_now(),
                                                    all_e=mapi.get_e_until_now()),
                        "name": name})

    elif tmp == "4":
        res_tmp = "/dash_tmp/setting.html"
        name = "הגדרות"
        usr = DBUserApi(session['user'])
        sett = DBSettingApi()
        return jsonify({"success": True,
                        "template": render_template(res_tmp, usr=usr.u, sett=sett.get_setting_events()),
                        "name": name})
    elif tmp == "10":
        capi.new(cid)
        client_info = capi.get_info_client()
        if not client_info:
            return jsonify(getX(57))

        res_tmp = "/dash_tmp/client_info.html"
        return jsonify({"success":True, "template":render_template(res_tmp, ci=client_info)})
    elif tmp == '15':
        if not DBSupplyApi.equipment_exist():
            # // 9
            return jsonify(getX(9))
        res_tmp = "/dash_tmp/add_lead.html"
        return jsonify({"success":True,
                        "template":render_template(res_tmp,user=session['user']),
                        "supply":DBSupplyApi.get_all_supply(),
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
        return jsonify(getX(DENIED))

    bdict = getPostData(request)
    level    = bdict.get("level", "-1")
    value    = bdict.get('value', "error")
    return check_level_new_lead(level, value)[1]

@m_app.route("/exit_lead", methods=["POST"])
def exit_lead():
    if not session.get("is_admin"):
        return jsonify(getX(DENIED))


    bdict = getPostData(request)
    _id = bdict.get("id")
    result = check_level_new_lead("4", _id)
    client = DBClientApi(None).get_all_client_by_mode(mode="all",ID=_id)
    if not result[0]:
        return result[1]

    return jsonify({"success":True, "data":client})
@m_app.route("/add_lead", methods=["POST"])
def add_lead():
    if not session.get("is_admin"):
        return jsonify(getX(DENIED))

    bdict = getPostData(request)
    name       = bdict.get("name", 0)
    phone      = bdict.get("phone", 0)
    id_client  = bdict.get("id_lead", "000 000 000")
    equipment:str  = bdict.get("supply", "{}")
    date       = bdict.get("date", 0)
    location   = bdict.get("location", 0)
    sub_pay    = bdict.get("sub_pay", 0)
    payment    = bdict.get("payment", 0)
    exp_fuel   = bdict.get("exp_fuel", 0)
    exp_employee =bdict.get("exp_employee", 0)
    type_pay    = bdict.get("type_pay", -1)
    # /* Irrelevant
    if not any(bdict.values()):
        return jsonify(getX(10))

    # // SUCCESS
    for _index, (k, v) in enumerate(bdict.items()):
        result:tuple[int, jsonify] = check_level_new_lead(str(_index+2), v)
        if isinstance(v, dict):continue
        if not result[0]:
            return result[1]

    # // SUCCESS
    equipment_is_ok, s_lead = DBSupplyApi.verify_equipments(equipment)
    if not DBSupplyApi.equipment_exist() or not equipment_is_ok :
        return jsonify(getX(3))
    # // SUCCESS
    db_new_client(write_by=session['user'],
                  last_write=time(),
                  is_open=True,
                  is_garbage=False,
                  is_signature=False,
                  client_id="C"+binascii.b2a_hex(os.urandom(5)).decode(),
                  full_name=name,
                  phone=phone,
                  ID=id_client,
                  event_supply=dumps(s_lead),
                  event_date=date,
                  event_place=location,
                  expen_employee=exp_employee,
                  expen_fuel=exp_fuel,
                  d_money=sub_pay,
                  total_money=payment,
                  client_payment=int(payment)-(int(exp_fuel)+int(exp_employee)),
                  type_pay=type_pay)
    # SUCCESS
    return jsonify(getX(4, suc=1))


@m_app.route("/search_lead/<data>", methods=["POST"])
def search_lead(data):
    error = dict(getX(5))
    res_tmp = ''
    if not session.get("is_admin"):
        return jsonify(getX(DENIED))

    bdict = getPostData(request)
    type_search = bdict.get("type_search")
    template    = bdict.get("template")
    if not data or not type_search or not template:
        return jsonify(error)

    # /* default template */
    if template == '0':
        res_tmp = "/dash_tmp/leads.html"
    elif template == '2':
        res_tmp = "/dash_tmp/history.html"

    capi = DBClientApi("none")
    client_found = capi.search_client(data, type_search)
    print(client_found)
    if not client_found:
        return jsonify(error)
    return jsonify({"success": True,
                    "template": render_template(res_tmp, leads=client_found, empty_lead=EMPTY_LEAD_T),
                    "name": "לקוחות"})


@m_app.route("/filter", methods=["POST"])
def filter_az():
    error = dict(getX(5))
    res_tmp = ''
    if not session.get("is_admin"):
        return jsonify(getX(DENIED))

    bdict = getPostData(request)
    type_filter = bdict.get("type_filter")
    tmp    = bdict.get("tmp")
    if not tmp or not tmp.isdigit():
        return jsonify(error)

    kw = {}
    if tmp == '0':
        res_tmp = "/dash_tmp/leads.html"
        kw["empty_lead"] = EMPTY_LEAD_T
    elif tmp == '2':
        res_tmp = "/dash_tmp/history.html"
        kw["empty_history"] = EMPTY_HISTORY

    capi = DBClientApi("none")
    cf = capi.get_all_client_by_mode(type_filter)
    return jsonify({"success":True,
                    "template":render_template(res_tmp, leads=cf, **kw)})

@m_app.route("/add_equipment", methods=["POST"])
def add_equipment():
    error = dict(getX(3))

    if not session.get("is_admin"):
        return jsonify(getX(DENIED))

    bdict = getPostData(request)
    # noinspection PyTypeChecker
    result = check_equipment(bdict)
    if not result[0]:
        error["notice"] = result[1]
        return jsonify(error)

    # add to the database
    add_supply(name=bdict["name"],
               price=int(bdict["price"]),
               exist=int(bdict["exist"]),
               desc="",
               _id=generate_id_supply(),
               count=0)

    return jsonify({"success":True})


@m_app.route("/update_equipment/<eq_id>", methods=["POST"])
def update_equipment(eq_id):
    error = dict(getX(3))

    if not session.get("is_admin"):
        return jsonify(getX(DENIED))

    bdict = getPostData(request)
    result = check_equipment(bdict)
    if not result[0]:
        error["notice"] = result[1]
        return jsonify(error)

    print(bdict)
    equip = DBSupplyApi(eq_id)
    if not equip.ok():
        # // 11
        error["notice"] = "ציוד לא מוכר"
        return jsonify(error)

    equip.ei.name = bdict["name"]
    equip.ei.price = int(bdict["price"])
    equip.ei.exist = int(bdict["exist"])
    # update db
    DBase.session.commit()
    return jsonify({"success":True})


@m_app.route("/del_equipment/<eq_id>", methods=["POST"])
def del_equipment(eq_id):
    error = dict(getX(3))

    if not session.get("is_admin"):
        return jsonify(getX(DENIED))
    equip = DBSupplyApi(eq_id)
    if not equip.ok():
        # 12
        error["notice"] = "נמחק או לא קיים"
        return jsonify(error)
    # delete
    DBase.session.delete(equip.ei)
    DBase.session.commit()
    # SUCCESS
    return jsonify({"success":True})

@m_app.route("/add_equipment_client", methods=["POST"])
def add_equipment_client():
    error = dict(getX(3))
    if not session.get("is_admin"):
        return jsonify(getX(DENIED))
    bdict = getPostData(request)
    cid = bdict.get("cid")
    supply = bdict.get("supply", "{}")
    capi = DBClientApi(cid)

    status, equipment = DBSupplyApi.verify_equipments(supply)
    if not capi.ok() or not status:
        # 13
        error["notice"] = "משהו השתבש בציוד או בלקוח"
        return jsonify(error)

    return jsonify(capi.update_lead_information("6", equipment))


@m_app.route("/event_lead_action/<action>", methods=["POST", "GET"])
def event_actions(action:str):
    error = dict(getX(3))
    if not session.get("is_admin"):
        if request.method == "GET":
            return redirect(url_for("index"),302)

        return jsonify(getX(DENIED))
    bdict = getPostData(request)
    client_id = bdict.get("client_id")
    capi = DBClientApi(client_id)

    if not capi.ok() and request.method == "POST":return jsonify(error)
    if action == "0":
        # delete event
        if not capi.set_event_status(0):
           return jsonify(error)

    elif action == "1":
        aapi = DBAgreeApi(client_id, by_cid=True)
        if not aapi.ok() or not aapi.is_agreement_singed():
            return jsonify(getX(14))

        if not capi.set_event_status(1):
            return jsonify(error)
    elif action == "2":
        # create invoice
        if not capi.create_invoice_event(session['user']):
            return jsonify(getX(E_AUTH))

    elif action == "3":

        client_id = request.args.get('client_id')
        capi.new(client_id)
        pathfile = capi.get_invoice_client()
        if not pathfile or not os.path.exists(pathfile):
            capi.reinvoice_client()
            return redirect(url_for("dashboard"), 302)

        return send_from_directory("invoices", os.path.basename(pathfile), as_attachment=True)

    elif action == "4":
        usr = DBUserApi(session['user'])
        if not usr.ok() or not usr.info_exist():
            return jsonify(getX(15))

        capi.new(client_id)
        override = bdict.get("override", "0")
        params, status = capi.create_agreement(capi.cid.write_by, override)

        if not status:
            error["notice"] = params
            return jsonify(error)

        return jsonify({"success":True, "url_params":params, "ctime":DBAgreeApi.get_ctime_agree_sess_by_cid(client_id)})

    elif action == "5":
        if not capi.set_event_status(2):
            return jsonify(getX(16))

    elif action == "6":
        aapi = DBAgreeApi(client_id, by_cid=True)
        if not aapi.ok():
            return jsonify(getX(17))

        si = aapi.set_show_agreement()
        return jsonify({"success":True, "url_params":si})

    elif action == "7":

        capi.delete_me()
    return jsonify({"success":True})



@m_app.route("/update_lead/<kind>", methods=["POST"])
def update_lead(kind):
    if not session.get("is_admin"):
        return jsonify(getX(DENIED))
    bdict = getPostData(request)
    data = bdict.get("data")
    cid = bdict.get("client_id")
    status = DBClientApi(cid).update_lead_information(kind, data)
    return jsonify(status)

@m_app.route("/import_txt", methods=["POST"])
def upload_equipment_txt():
    error = getX(E_IMPORT_TXT)
    if not session.get("is_admin"):
        return jsonify(getX(DENIED))

    bdict = getPostData(request)
    file_s:FileStorage = request.files.get("txt")
    nonce = bdict.get("nonce")
    if not file_s:
        #  18
        error["notice"] = "detected: burpsuite/proxy"
        return jsonify(error)

    file_s.filename = FILENAME_IMPORT_TXT

    binary = file_s.stream.read()
    key_xor = DBUserApi(session['user']).u.pwd
    if binary.__len__() > MAX_IMPORT_TXT:
        # 19
        error["notice"] = "קובץ גדול מידיי"
        return jsonify(error)

    if not import_txt_equipment(binary, key_xor):
        # 20
        error["notice"] = "ייבוא הקובץ נכשל"
        return jsonify(error)

    # /* delete nonce */
    session["nonce_import"] = get_random_key()
    return jsonify({"success":True, nonce:session["nonce_import"]})

@m_app.route("/export_txt", methods=["GET"])
def download_equipment_txt():

    if not session.get("is_admin"):
        return redirect(url_for("dashboard"), 302)

    fp = BASEDIR+"\\exports\\"+FILENAME_EXPORT_TXT
    user = DBUserApi(session["user"])
    if not user.ok() or not export_txt_equipment(fp, user.u.pwd):
        return redirect(url_for("dashboard"), 302)

    return send_from_directory("exports", os.path.basename(FILENAME_EXPORT_TXT), as_attachment=True)

# /* access: *
@m_app.route("/agreement", methods=["POST", "GET"])
@m_app.route("/agreement/", methods=["POST", "GET"])
def agreement():
    error = dict(getX(7))
    page_error = "/error_tmp/agreement_error.html"

    client_id = request.args.get("cid")
    agree_id  = request.args.get("aid")
    show_id   = request.args.get("si")

    aapi = DBAgreeApi(agree_id)
    capi = DBClientApi(client_id)
    if not any(request.args):
        return render_template(page_error, msg=getX(21))
    if not show_id and (not capi.ok() or not aapi.ok()):
        return render_template(page_error, msg=getX(22))
    elif show_id and not capi.ok():
        return render_template(page_error, msg=getX(23))

    usr = DBUserApi(capi.cid.write_by)

    if not show_id:
        if aapi.is_expired():
            return render_template(page_error, msg=getX(24))
        elif aapi.is_accept():
            return render_template(page_error, msg=getX(25))

    elif show_id and not aapi.new(show_id, by_si=1) or not capi.ok():
        return render_template(page_error, msg=getX(26))

    # /* analyze equipment on this client */
    equipment = capi.get_client_equipment()
    invoice_num = capi.get_invoice_number() or "000000"
    capi.cid.invc_n = invoice_num
    aapi.aid.ctime_date = aapi.get_ctime_client_singed()
    equip_policy:list[str] = open(BASEDIR+"/tmp/dash_tmp/equipment_policy.txt", 'r', encoding="utf8").read().split("\n")
    return render_template("/doc_tmp/agreement.html", equipment_p=equip_policy,
                           cid=capi.cid, aid=aapi.aid, equipment=equipment, u=usr.u, edit=not bool(aapi.aid.show_id))

# /* access: *
@m_app.route("/add_agreement", methods=["POST"])
@m_app.route("/add_agreement/", methods=["POST"])
def add_agreement():
    error = getX(21)
    page_error = "/error_tmp/agreement_error.html"

    if not any(request.args) or not any(request.form):
        return jsonify(error)

    client_id = request.args.get("cid")
    agree_id = request.args.get("aid")

    capi = DBClientApi(client_id)
    aapi = DBAgreeApi(agree_id)
    if not capi.ok() or not aapi.ok() or capi.cid.is_signature:
        return jsonify(error)
    bdict = getPostData(request)
    identify = bdict.get("identify") or capi.cid.ID
    signature = bdict.get("signature")

    if not signature or signature.__len__() < 4000:
        return jsonify(getX(27))

    desc = aapi.add_agreement(signature, [identify ], capi, error)
    if not desc["success"]:
        error["notice"] = desc["notice"]
        return error

    return jsonify({"success":True, "template": render_template(page_error, msg=getX(8))})


@m_app.route("/setting/<ac>", methods=["POST"])
def setting(ac:str):

    error = dict(getX(RELOAD_PAGE))
    if not session.get("is_admin"):
        return jsonify(getX(DENIED))

    if not ac or not ac.isdigit() or not any(request.form):
        return jsonify(error)
    elif not session.get("user"):
        return jsonify(getX(28))

    usr = DBUserApi(session['user'])
    bdict = getPostData(request)
    # /* signature */
    if ac == "0":
        signature = bdict.get("signature", str())
        if signature.__len__() < 3500:
            return jsonify(getX(27))

        if not usr.ok():#or not usr.admin():
            return jsonify(getX(29))

        usr.u.signature = signature
    # /*  email */
    elif ac == "1":
        email = bdict.get('email', str())
        if not verify_mail(email):
            return jsonify(getX(30))

        usr.u.email = email
    # /* identify */
    elif ac == "2":
        identify = bdict.get("identify", str())
        if not idValid(identify):
            return jsonify(getX(31))

        usr.u.identify = identify
    # /* delete auto garbage */
    # /* finish auto old valid event */
    elif ac == "3" or ac == "4":
        ts = bdict.get("ts")
        value:bool = bool(int(bdict.get("value", "0")))
        sett = DBSettingApi()
        sett.events_setting(ts, value)

    elif ac == '5':
        ts = bdict.get("ts")
        value: bool = bool(int(bdict.get("value", "0")))
        sett = DBSettingApi()
        sett.events_setting(ts, value)

    DBase.session.commit()
    return jsonify({"success":True})


@m_app.route("/money/<ac>", methods=["POST"])
def money_api(ac:str):

    error = dict(getX(RELOAD_PAGE))
    json_graph = []
    max_e:int = MAX_IMPORT_TXT//30
    max_p:int = MAX_IMPORT_TXT//30
    if not session.get("is_admin"):
        return jsonify(getX(DENIED))
    bdict = getPostData(request)
    if not ac or not any(bdict):
        return jsonify(error)

    month = bdict.get("month", "0")
    if ac == '0':
        pass
    elif ac == '1':
        mapi = MoneyApi()
        json_graph = mapi.get_e_and_p_month(month)
        max_e = mapi.get_max_e_year()
        max_p = mapi.get_max_p_year()
        print(f"max e:{max_e} -- max p:{max_p}")
    elif ac == '2':
        mapi = MoneyApi()
        json_graph = mapi.get_e_and_p_year()
        max_e = mapi.get_max_e_year()
        max_p = mapi.get_max_p_year()


    return jsonify({"success":True, "json":json_graph, "maxp":max_p, "maxe":max_e})



if __name__ == "__main__":
    ssl_context = ('server.cert', 'server.key')
    with m_app.app_context():
        DBase.create_all()
        # /* __ initial DBase __ */
        DBSettingApi().create()
        #signup(user='דבורה', pwd='משי', ip='2.55.187.108', is_admin=True)
        #signup(user='דביר', pwd='משי', ip='2.55.187.108', is_admin=True)
    m_app.run(host="0.0.0.0", port=80, debug=True)


