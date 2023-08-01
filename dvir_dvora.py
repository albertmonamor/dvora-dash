from json import loads, dumps
from time import sleep

from werkzeug.datastructures import FileStorage

from Api.api_function import check_level_new_lead, check_equipment, verify_mail, idValid
from Api.protocol import *
from flask import render_template, request, session, jsonify, redirect, url_for, \
    send_from_directory
from Api.databases import DBase, signup, db_new_client, add_supply \
    , time, generate_id_supply, export_txt_equipment, import_txt_equipment

from Api.db_api import DBClientApi, DBUserApi, DBSupplyApi, DBAgreeApi, MoneyApi


# ==================== FILTER =========================
@m_app.template_filter('decimal')
def decimal_integer(value):
    return f"{value:,}"

#  ******************* ROUTES *************************

#@m_app.errorhandler(500)
@m_app.errorhandler(404)
def _404(n_error=None):
    sleep(2)
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
    user= request.form.get("user", "?").lower().replace(" ", "")
    pwd = request.form.get('pwd')
    key = request.form.get('key')
    usr = DBUserApi(user)
    if key == session['sess-login'] and usr.ok() and usr.u.pwd == pwd:
        session['is_admin'] = usr.u.is_admin
        session['user']     = user
        del session['sess-login']
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
    error = dict(UN_ERROR)

    if not session.get('is_admin'):
        return jsonify(TMP_DENIED)
    # /* default template */
    res_tmp:str = T404
    # /* default title */
    name = "404"
    # /* client id */
    cid = request.form.get("identify", "C0")
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
        return jsonify({"success": True,
                        "template": render_template(res_tmp, usr=usr.u),
                        "name": name})
    elif tmp == "10":
        capi.new(cid)
        client_info = capi.get_info_client()

        res_tmp = "/dash_tmp/client_info.html"
        return jsonify({"success":True, "template":render_template(res_tmp, ci=client_info)})
    elif tmp == '15':
        if not DBSupplyApi.equipment_exist():
            error["notice"] = "הוסף ציוד לפני הוספת לקוח"
            return jsonify(error)
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
        return jsonify(TMP_DENIED)

    level    = request.form.get("level", "-1") or "-1"
    value    = request.form.get('value', "error")
    return check_level_new_lead(level, value)[1]

@m_app.route("/add_lead", methods=["POST"])
def add_lead():
    res:dict = dict(LEAD_ERROR)
    if not session.get("is_admin"):
        return jsonify(TMP_DENIED)

    name       = request.form.get("name", 0)
    phone      = request.form.get("phone", 0)
    id_client  = request.form.get("id_lead", 0)
    equipment:str  = request.form.get("supply", "{}")
    date       = request.form.get("date", 0)
    location   = request.form.get("location", 0)
    sub_pay    = request.form.get("sub_pay", 0)
    payment    = request.form.get("payment", 0)
    exp_fuel   = request.form.get("exp_fuel", 0)
    exp_employee = request.form.get("exp_employee", 0)
    type_pay    = request.form.get("type_pay", -1)
    # /* Irrelevant
    if not any(request.form.values()) :
        res["notice"] = "אחד מהנתונים חסר או לא ברור!"
        return jsonify(res)

    # // SUCCESS
    for _index, (k, v) in enumerate(request.form.items()):
        result:tuple[int, jsonify] = check_level_new_lead(str(_index+2), v)
        if isinstance(v, dict):continue
        if not result[0]:
            return result[1]

    # // SUCCESS
    equipment_is_ok, s_lead = DBSupplyApi.verify_equipments(loads(equipment))

    if not DBSupplyApi.equipment_exist() or not equipment_is_ok :
        return jsonify(EQUIP_ERROR)
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
    return jsonify(EQUIP_SUCCESS)


@m_app.route("/search_lead/<data>", methods=["POST"])
def search_lead(data):
    error = dict(SEARCH_LEAD_ERR)
    res_tmp = ''
    if not session.get("is_admin"):
        return jsonify(TMP_DENIED)

    type_search = request.form.get("type_search")
    template    = request.form.get("template")
    if not data or not type_search or not template:
        return jsonify({error})

    # /* default template */
    if template == '0':
        res_tmp = "/dash_tmp/leads.html"
    elif template == '2':
        res_tmp = "/dash_tmp/history.html"

    capi = DBClientApi("none")
    client_found = capi.search_client(data, type_search)
    if not client_found:
        return jsonify(error)
    return jsonify({"success": True,
                    "template": render_template(res_tmp, leads=client_found, empty_lead=EMPTY_LEAD_T),
                    "name": "לקוחות"})


@m_app.route("/add_equipment", methods=["POST"])
def add_equipment():
    error = dict(EQUIP_ERROR)

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
    error = dict(EQUIP_ERROR)

    if not session.get("is_admin"):
        return jsonify(TMP_DENIED)

    result = check_equipment(request.form)
    if not result[0]:
        error["notice"] = result[1]
        return jsonify(error)


    equip = DBSupplyApi(eq_id)
    if not equip.ok():
        error["notice"] = "ציוד לא מוכר"
        return jsonify(error)

    equip.name = request.form["name"]
    equip.price = int(request.form["price"])
    equip.exist = int(request.form["exist"])
    # update db
    DBase.session.commit()
    return jsonify({"success":True})


@m_app.route("/del_equipment/<eq_id>", methods=["POST"])
def del_equipment(eq_id):
    error = dict(EQUIP_ERROR)

    if not session.get("is_admin"):
        return jsonify(TMP_DENIED)
    equip = DBSupplyApi(eq_id)
    if not equip.ok():
        error["notice"] = "נמחק או לא קיים"
        return jsonify(error)
    # delete
    DBase.session.delete(equip.ei)
    DBase.session.commit()
    # SUCCESS
    return jsonify({"success":True})


@m_app.route("/event_lead_action/<action>", methods=["POST", "GET"])
def event_actions(action:str):
    error = dict(LEAD_ERROR)
    if not session.get("is_admin"):
        if request.method == "GET":
            return redirect(url_for("index"),302)

        return jsonify(TMP_DENIED)

    client_id = request.form.get("client_id")
    capi = DBClientApi(client_id)

    if not capi.ok() and request.method == "POST":return jsonify(error)
    if action == "0":
        # delete event
        if not capi.set_event_status(0):
           return jsonify(error)

    elif action == "1":
        aapi = DBAgreeApi(client_id, by_cid=True)
        if not aapi.ok() or not aapi.is_agreement_singed():
            error["notice"] = "הלקוח לא חתם על החוזה"
            return jsonify(error)

        if not capi.set_event_status(1):
            return jsonify(error)
    elif action == "2":
        # create invoice
        if not capi.create_invoice_event(session['user']):
            return jsonify(INVOICE_ACTION_ERR)

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
            error["notice"] = "הגדר חתימה ופרטי עוסק!"
            return jsonify(error)

        capi.new(client_id)
        override = request.form.get("override", "0")
        params, status = capi.create_agreement(capi.cid.write_by, override)

        if not status:
            error["notice"] = params
            return jsonify(error)

        return jsonify({"success":True, "url_params":params, "ctime":DBAgreeApi.get_ctime_agree_sess_by_cid(client_id)})

    elif action == "5":
        if not capi.set_event_status(2):
            error["notice"] = "שיחזור האירוע נכשל"
            return jsonify(error)

    elif action == "6":
        aapi = DBAgreeApi(client_id, by_cid=True)
        error["notice"] = "שגיאה במזהה לקוח"
        if not aapi.ok():
            return jsonify(error)

        si = aapi.set_show_agreement()
        return jsonify({"success":True, "url_params":si})

    return jsonify({"success":True})



@m_app.route("/update_lead/<kind>", methods=["POST"])
def update_lead(kind):
    if not session.get("is_admin"):
        return jsonify(TMP_DENIED)

    data = request.form.get("data")
    cid = request.form.get("client_id")
    status = DBClientApi(cid).update_lead_information(kind, data)
    return jsonify(status)

@m_app.route("/import_txt", methods=["POST"])
def upload_equipment_txt():
    error = dict(IMPORT_TXT_ERROR)
    if not session.get("is_admin"):
        return jsonify(TMP_DENIED)

    file_s:FileStorage = request.files.get("txt")
    nonce = request.form.get("nonce")

    if session.get("nonce_import") != nonce:
        return jsonify(UN_ERROR)

    if not file_s:
        error["notice"] = "detected: burpsuite/proxy"
        return jsonify(error)

    file_s.filename = FILENAME_IMPORT_TXT

    binary = file_s.stream.read()
    key_xor = DBUserApi(session['user']).u.pwd
    if binary.__len__() > MAX_IMPORT_TXT:
        error["notice"] = "קובץ גדול מידיי"
        return jsonify(error)

    if not import_txt_equipment(binary, key_xor):
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
    error = dict(AGREE_ERROR)
    page_error = "/error_tmp/agreement_error.html"

    client_id = request.args.get("cid")
    agree_id  = request.args.get("aid")
    show_id   = request.args.get("si")

    aapi = DBAgreeApi(agree_id)
    capi = DBClientApi(client_id)

    if not any(request.args):
        error["notice"] = "הקישור לא תקין"
        return render_template(page_error, msg=error)

    if not show_id and ( not capi.ok() or not aapi.ok()):
        error["notice"] = "מזהה חוזה לא תקין"
        return render_template(page_error, msg=error)

    usr = DBUserApi(capi.cid.write_by)

    if not show_id:
        if aapi.is_expired():
            error["notice"] = "פג תוקף הקישור"
            return render_template(page_error, msg=error)
        elif aapi.is_accept():
            error["notice"] = "מסמך זה נחתם ורשום במערכת"
            return render_template(page_error, msg=error)

    elif show_id and not aapi.new(show_id, by_si=1) or not capi.ok():
        error["notice"] = "לא ניתן לפתוח את חוזה השכרה"
        return render_template(page_error, msg=error)

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
    error = dict(AGREE_ERROR)
    error["notice"] = "קישור לא תקין"
    page_error = "/error_tmp/agreement_error.html"

    if not any(request.args) or not any(request.form):
        return jsonify(error)

    client_id = request.args.get("cid")
    agree_id = request.args.get("aid")

    capi = DBClientApi(client_id)
    aapi = DBAgreeApi(agree_id)
    if not capi.ok() or not aapi.ok():
        return jsonify(error)

    fname = request.form.get("fname") or capi.cid.full_name
    location = request.form.get("_location")
    identify = request.form.get("identify") or capi.cid.ID
    phone = request.form.get("phone") or capi.cid.phone
    udate = request.form.get("udate") or capi.cid.event_date
    signature = request.form.get("signature")

    if not signature or signature.__len__() < 4000:
        error["notice"] = "החתימה קצרה מידיי"
        return jsonify(error)

    desc = aapi.add_agreement(signature, [fname,location, identify, phone, udate], capi, error)
    if not desc["success"]:
        error["notice"] = desc["notice"]
        return error

    return jsonify({"success":True, "template": render_template(page_error, msg=SUCCESS_AGREE)})


@m_app.route("/setting/<ac>", methods=["POST"])
def setting(ac:str):

    error = dict(UN_ERROR)
    if not session.get("is_admin"):
        return jsonify(TMP_DENIED)

    if not ac or not ac.isdigit() or not any(request.form) or not session.get("user"):
        return jsonify(error)

    usr = DBUserApi(session['user'])

    if ac == "0":
        signature = request.form.get("signature", str())
        if signature.__len__() < 3500:
            error["notice"] = "חתימה קצרה מידיי"
            return jsonify(error)

        if not usr.ok():#or not usr.admin():
            error["notice"] = "שגיאה בזיהוי המנהל"
            return jsonify(error)

        usr.u.signature = signature
    elif ac == "1":
        email = request.form.get('email', str())
        if not verify_mail(email):
            error["notice"] = "דואר לא תקין"
            return jsonify(error)

        usr.u.email = email

    elif ac == "2":
        identify = request.form.get("identify", str())
        if not idValid(identify):
            error["notice"] = "תעודת זהות שגויה"
            return jsonify(error)

        usr.u.identify = identify

    DBase.session.commit()
    return jsonify({"success":True})


@m_app.route("/money/<ac>", methods=["POST"])
def money_api(ac:str):

    error = dict(UN_ERROR)
    json_graph = []
    if not session.get("is_admin"):
        return jsonify(TMP_DENIED)

    if not ac or not any(request.form):
        return jsonify(error)

    month = request.form.get("month", 0)
    if ac == '0':
        pass
    elif ac == '1':
        mapi = MoneyApi()
        json_graph = mapi.get_e_and_p_month(month)

    elif ac == '2':
        mapi = MoneyApi()
        json_graph = mapi.get_e_and_p_year()


    return jsonify({"success":True, "json":json_graph})



if __name__ == "__main__":
    with m_app.app_context():
        DBase.create_all()

        #signup(user='דבורה', pwd='משי', ip='2.55.187.108', is_admin=True)
        #signup(user='דביר', pwd='משי', ip='2.55.187.108', is_admin=True)
    m_app.run(host="0.0.0.0", port=80, debug=True)


