import binascii
import os
from json import loads, dumps
from time import sleep

from werkzeug.datastructures import FileStorage

from Api.api_function import check_level_new_lead, check_equipment
from Api.protocol import m_app, get_random_key, LOGIN_FAILED, LOGIN_SUCCESS, UN_ERROR, EMPTY_LEAD_T, T404, TMP_DENIED, \
    LEAD_ERROR, EQUIP_ERROR, EQUIP_SUCCESS, SEARCH_LEAD_ERR, EMPTY_HISTORY, INVOICE_ACTION_ERR, IMPORT_TXT_ERROR, \
    MAX_IMPORT_TXT, FILENAME_IMPORT_TXT, BASEDIR, FILENAME_EXPORT_TXT, AGREE_ERROR, SUCCESS_AGREE
from flask import render_template, request, session, jsonify, redirect, url_for, \
    send_from_directory
from Api.databases import Users, DBase, signup, db_new_client, add_supply, get_all_supply, verify_supply \
    , time, get_supply_by_id, generate_id_supply, DBClientApi, export_txt_equipment, import_txt_equipment,\
    DBAgreementApi


#  ******************* ROUTES *************************

@m_app.errorhandler(404)
def _404(n_error):
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
        client_open = DBClientApi().get_all_client_by_mode("open")
        res_tmp = "/dash_tmp/leads.html"
        return jsonify({"success":True,
                        "template":render_template(res_tmp, leads=client_open,empty_lead=EMPTY_LEAD_T),
                        "name":"לקוחות"})
    elif tmp == "1":
        res_tmp = "/dash_tmp/equipment.html"
        session["nonce_import"] = get_random_key()
        return jsonify({"success":True,
                        "template":render_template(res_tmp, equipment=get_all_supply(),
                                                   nonce_import=session["nonce_import"]),
                        "name":"ציוד"})
    elif tmp == "2":
        client_open = DBClientApi().get_all_client_by_mode("both")
        res_tmp = "/dash_tmp/history.html"
        return jsonify({"success":True,
                        "template":render_template(res_tmp, leads=client_open,empty_history=EMPTY_HISTORY),
                        "name":"היסטוריה"})
    elif tmp == "3":
        res_tmp = "/dash_tmp/money.html"
        name = "הוצאות/הכנסות"
    elif tmp == "4":
        res_tmp = "/dash_tmp/setting.html"
        name = "הגדרות"
    elif tmp == "10":
        client_info = DBClientApi().get_info_client(request.form.get("identify", "C0"))

        res_tmp = "/dash_tmp/client_info.html"
        return jsonify({"success":True, "template":render_template(res_tmp, ci=client_info)})
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
    equipment_is_ok, s_lead = verify_supply(loads(equipment))

    if not equipment_is_ok:
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
    if not session.get("is_admin"):
        return jsonify(TMP_DENIED)

    type_search = request.form.get("type_search")
    if not data or not type_search:
        return jsonify({error})

    res_tmp = "/dash_tmp/leads.html"
    client_found = DBClientApi().search_client(data, type_search)
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


@m_app.route("/del_equipment/<eq_id>", methods=["POST"])
def del_equipment(eq_id):
    error = dict(EQUIP_ERROR)

    if not session.get("is_admin"):
        return jsonify(TMP_DENIED)
    equip = get_supply_by_id(eq_id)
    if not equip:
        error["notice"] = "נמחק או לא קיים"
        return jsonify(error)
    # delete
    DBase.session.delete(equip)
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
    if not client_id and request.method == "POST":return jsonify(error)
    if action == "0":
        # delete event
        if not DBClientApi.set_event_status(0, client_id):
           return jsonify(error)

    elif action == "1":
        # move event to history
        if not DBClientApi.set_event_status(1, client_id):
            return jsonify(error)
    elif action == "2":
        # create invoice
        sleep(1)
        if not DBClientApi().create_invoice_event(client_id, None):
            return jsonify(INVOICE_ACTION_ERR)

    elif action == "3":
        client_id = request.args.get('client_id')
        pathfile = DBClientApi().get_invoice_client(client_id)
        if not pathfile or not os.path.exists(pathfile):
            DBClientApi().reinvoice_client(client_id)
            return redirect(url_for("dashboard"), 302)

        return send_from_directory("invoices", os.path.basename(pathfile), as_attachment=True)

    elif action == "4":
        override = request.form.get("override", "0")
        params, status = DBClientApi().create_agreement(client_id, override)

        if not status:
            error["notice"] = params
            return jsonify(error)

        return jsonify({"success":True, "url_params":params, "ctime":DBAgreementApi.get_ctime_agree_sess_by_cid(client_id)})

    elif action == "5":
        if not DBClientApi().set_event_status(2, client_id):
            error["notice"] = "שיחזור האירוע נכשל"
            return jsonify(error)


    return jsonify({"success":True})

@m_app.route("/update_lead/<kind>", methods=["POST"])
def update_lead(kind):
    if not session.get("is_admin"):
        return jsonify(TMP_DENIED)

    data = request.form.get("data")
    client_id = request.form.get("client_id")
    status = DBClientApi().update_lead_information(kind, data, client_id)
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
    key_xor = Users.query.filter_by(user=session['user']).first().pwd
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
    key_xor = Users.query.filter_by(user=session["user"]).first().pwd
    if not key_xor or not export_txt_equipment(fp, key_xor):
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

    if not any(request.args):
        error["notice"] = "הקישור לא תקין"
        return render_template(page_error, msg=error)

    aid = DBAgreementApi.get_agreement_by_aid(agree_id)
    if not aid:
        error["notice"] = "מזהה חוזה לא תקין"
        return render_template(page_error, msg=error)
    if DBAgreementApi().is_expired(aid):
        error["notice"] = "פג תוקף הקישור"
        return render_template(page_error, msg=error)
    elif aid.is_accepted:
        error["notice"] = "מסמך זה נחתם ורשום במערכת"
        return render_template(page_error, msg=error)

    # /* extract client by cid */
    cid = DBClientApi().get_client_by_id(client_id)
    if not cid:
        error["notice"] = "הקישור לא תקין"
        return render_template(page_error, msg=error)

    # /* analyze equipment on this client */
    equipment = DBClientApi.get_client_equipment(cid)
    invoice_num = DBClientApi.get_invoice_number(cid) or "000000"
    cid.invc_n = invoice_num
    equip_policy:list[str] = open(BASEDIR+"/tmp/dash_tmp/equipment_policy.txt", 'r', encoding="utf8").read().split("\n")
    return render_template("/doc_tmp/agreement.html", equipment_p=equip_policy,
                           cid=cid, equipment=equipment)

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

    cid = DBClientApi.get_client_by_id(client_id)
    aid = DBAgreementApi.get_agreement_by_aid(agree_id)
    if not cid or not aid:
        return jsonify(error)
    if DBAgreementApi.is_expired(aid):
        error["notice"] = "הקישור פג תוקף"
        return jsonify(error)



    fname = request.form.get("fname") or cid.full_name
    location = request.form.get("_location")
    identify = request.form.get("identify") or cid.ID
    phone = request.form.get("phone") or cid.phone
    udate = request.form.get("udate") or cid.event_date
    signature = request.form.get("signature")
    for i, v in zip([2, 7, 4, 3, 6], [fname,location, identify, phone, udate]):
        b, r = check_level_new_lead(str(i), v)
        if not b:
            return r

    if not signature or signature.__len__() < 4000:
        error["notice"] = "החתימה קצרה מידיי"
        return jsonify(error)

    aid.sig_client = signature
    aid.sig_date = time()
    aid.from_date = cid.event_date
    aid.to_date = cid.event_date
    aid.location_client = location
    aid.is_accepted = True
    # /* success
    cid.is_signature = True
    DBase.session.commit()


    return jsonify({"success":True, "template": render_template(page_error, msg=SUCCESS_AGREE)})



if __name__ == "__main__":
    with m_app.app_context():
        DBase.create_all()
        # signup(user='דבי', pwd='משי', ip='2.55.187.108')
    m_app.run(host="0.0.0.0", port=80, debug=True)


