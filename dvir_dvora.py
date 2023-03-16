from Api.api_function import check_level_new_lead
from Api.protocol import m_app, get_random_key, LOGIN_FAILED, LOGIN_SUCCESS, UN_ERROR, EMPTY_LEAD_T, T404, TMP_DENIED
from flask import render_template, request, render_template_string, session, jsonify, redirect, url_for
from Api.databases import Users, DBase, signup, new_lead, SUPPLY


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
    print(pwd, key, user)
    in_db = Users.query.filter_by(user=user).first()
    if key == session['sess-login'] and in_db and in_db.pwd == pwd:
        session['is_admin'] = True
        session['user']     = user
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
    # /* <    *---MAIN TAB TEMPLATE---*    >
    if tmp == "0":
        res_tmp = "/dash_tmp/leads.html"
    elif tmp == "1":
        res_tmp = "/dash_tmp/history.html"
    elif tmp == "2":
        res_tmp = "/dash_tmp/money.html"
    elif tmp == "3":
        res_tmp = "/dash_tmp/setting.html"
        return jsonify({"success":True,
                        "template":render_template(res_tmp)})
    elif tmp == '15':
        res_tmp = "/dash_tmp/add_lead.html"
        return jsonify({"success":True,
                        "template":render_template(res_tmp,
                                                   welcome=render_template("/dash_tmp/wel_add_lead"),
                                                   user=session['user']),
                        "supply":SUPPLY})

    return jsonify({"success":True, "template":render_template(res_tmp, empty_lead=EMPTY_LEAD_T)})



@m_app.route("/new_lead", methods=["POST"])
def add_lead():
    if not session.get("is_admin"):
        return jsonify(TMP_DENIED)

    level    = request.form.get("level", "-1")
    value    = request.form.get('value', "error")
    print(level, value)
    return check_level_new_lead(level, value)



if __name__ == "__main__":
    with m_app.app_context():
        DBase.create_all()

        from json import dumps
        from time import ctime, time
        # signup(user='דבי', pwd='משי', ip='2.55.187.108')
        # new_lead(write_by="אברהם", full_name="משה רועי", phone="0585005617", ID="324104173",
        #          event_supply=dumps(['0', '12', '56', '2']), event_date=time() + 10000,
        #          event_place="31.783203, 34.625719", determine_money=4850, pay_sub=True, money_left=4850 / 2,
        #          is_open=True)


    m_app.run(host="0.0.0.0", port=45000, debug=True)
