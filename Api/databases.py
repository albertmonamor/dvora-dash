import binascii
import os
from copy import deepcopy

import pdfkit
import sys
from json import dumps, loads
from time import ctime, time
from Api.api_function import FormatTime, generate_invoice_path, \
    check_level_new_lead, XOR, generate_link_edit_agree, generate_link_show_agree
from Api.protocol import DBase, m_app, PDF_OPTIONS, PATH_PDFKIT_EXE, BASEDIR, UPDATE_LEAD_ERROR, AGREE_SESS_LIFE


class Users(DBase.Model):
    __tablename__ = "users"
    index       = DBase.Column(DBase.Integer, primary_key=True)
    user        = DBase.Column(DBase.String(20), nullable=False)
    pwd         = DBase.Column(DBase.String(10), nullable=False)
    ip          = DBase.Column(DBase.String(22), nullable=False)
    is_admin    = DBase.Column(DBase.Boolean, unique=False, default=False)
    email       = DBase.Column(DBase.String,  nullable=True)
    identify    = DBase.Column(DBase.Integer,  nullable=True)
    phone       = DBase.Column(DBase.Integer,  nullable=True)
    signature   = DBase.Column(DBase.String,    nullable=True)

    def __repr__(self):
        return f"<{self.__tablename__}> {self.index}"
class DBUserApi:

    def __init__(self, user:str):
        self.u:None | Users = None
        self._u: None | str = None
        self.new(user)

    def new(self, user):
        self.u = Users.query.filter_by(user=user).first()
        self._u = user

    def ok(self) -> bool:
        return bool(self.u)

    def admin(self) -> bool:
        return self.u.is_admin

    def info_exist(self) -> bool:
        return self.u.email and self.u.signature and self.u.identify


class Client(DBase.Model):
    __tablename__ = 'client'
    # for API
    index           = DBase.Column(DBase.Integer,       primary_key=True)
    write_by        = DBase.Column(DBase.String,        nullable=False)
    last_write      = DBase.Column(DBase.Float, nullable=False, default=time())
    is_open         = DBase.Column(DBase.Boolean,       nullable=False, default=True)
    is_garbage      = DBase.Column(DBase.Boolean,       nullable=False, default=False)
    is_signature   = DBase.Column(DBase.Boolean,        nullable=False, default=False)
    invoice_id      = DBase.Column(DBase.String,        nullable=False, default="")
    client_id       = DBase.Column(DBase.String,        nullable=False, default="")

    # datas
    full_name       = DBase.Column(DBase.String(20),    nullable=False)
    phone           = DBase.Column(DBase.String(20),    nullable=False)
    ID              = DBase.Column(DBase.String(11),    nullable=False)
    # id of item in other DB
    event_supply    = DBase.Column(DBase.String,   nullable=False)
    event_date      = DBase.Column(DBase.String,        nullable=False)
    event_place     = DBase.Column(DBase.String,        nullable=False)
    # expenditure
    expen_employee  = DBase.Column(DBase.Float,         nullable=False, default=0)
    expen_fuel      = DBase.Column(DBase.Float,         nullable=False, default=0)
    type_pay       = DBase.Column(DBase.Integer,       nullable=False, default=0)
    # מקדמה
    d_money         = DBase.Column(DBase.Float,         nullable=False, default=0)
    total_money     = DBase.Column(DBase.Float,         nullable=False)
    client_payment  = DBase.Column(DBase.Float,         nullable=False)
    # for API bool
class DBClientApi:

    def __init__(self, cid:str):
        self.cid:Client| None  = None
        self._cid = cid
        self.new(cid)

    def new(self, cid):
        self.cid = Client.query.filter_by(client_id=cid).first()
        self._cid = cid


    def ok(self):
        return bool(self.cid)

    def get_all_client_by_mode(self, mode:str = "open", **kwargs):
        # which mode?
        if mode == "open":
            _client: list[Client] = Client.query.filter_by(is_open=True, **kwargs).all()
        elif mode == "close":
            _client: list[Client] = Client.query.filter_by(is_open=False, is_garbage=False, **kwargs).all()
        elif mode == "garbage":
            _client: list[Client] = Client.query.filter_by(is_garbage=True, **kwargs).all()
        elif mode == "both":
            _client: list[Client] = Client.query.filter_by(is_open=False, **kwargs).all()
        else:
            # undefined
            _client: list[Client] = Client.query.all()

        # start indexing
        return self.get_client_indexing(_client)


    def is_pay_down_payment(self) -> bool:
        return bool(self.cid.d_money)

    def is_order_equipment(self) -> bool:
        equipments = loads(self.cid.event_supply)
        return bool(len(equipments))

    def is_low_expenses(self, c:Client):
        return self.get_net_all(c) >= 1000

    def get_gross_all(self, c:Client) -> float | int:
        money_equipments = self.get_info_equipment()["money"]
        return c.expen_fuel+c.expen_employee+money_equipments

    def get_gross_client(self, c:Client) -> float | int:
        money_equipments = self.get_info_equipment()["money"]
        return money_equipments

    def get_net_all(self, c:Client) -> float | int:
        result = self.get_info_equipment()["money"] - c.expen_fuel - c.expen_employee

        return result

    def get_client_equipment(self):
        equip = loads(self.cid.event_supply)
        return equip

    def get_info_equipment(self) -> dict:
        equipments = {"money":0, "count":0}
        if self.is_order_equipment():
            for index, equip in self.get_client_equipment().items():
                equipments["money"]+= int(equip["price"] * int(equip["count"]))
                equipments["count"]+= int(equip["count"])


        return equipments

    def search_client(self, data:str, mode:str="open") -> dict:
        if not data:
            return {}

        # /* by name of client */
        _clients:dict = {}
        if data.isalpha():
            _clients = self.get_all_client_by_mode(mode, full_name=data)
        elif data.isdigit():
            _clients = self.get_all_client_by_mode(mode, phone=data)

        return _clients

    def get_client_indexing(self, _client:list[Client]):
        client = {}
        for index, c in enumerate(_client):
            self.new(c.client_id)
            client[index] = {"wb": c.write_by,
                             "lw": FormatTime(c.last_write).get_format_before_time(),
                             "fn": c.full_name,
                             "phone": c.phone,
                             "id": c.ID,
                             "ci":c.client_id,
                             "es": c.event_supply,
                             "ed":FormatTime.get_name_day_and_date(c.event_date),
                             "ep": c.event_place,
                             "dm": c.d_money,
                             "ps": self.is_pay_down_payment(),
                             "tm": f"{self.get_gross_client(c) :,}",
                             "oe": self.is_order_equipment(),
                             "cm": f"{self.get_net_all(c) :,}",
                             'low_e': self.is_low_expenses(c),
                             'ea':c.is_open,
                             "eg":c.is_garbage,
                             "cs":DBAgreeApi.is_agreement_signed_by_cid(c.client_id),
                             "iee":self.is_event_expired_date()
                           }
        return client

    def get_info_client(self) -> dict:
        if not self.ok():
            return {}

        dc = self.clientdb_to_dict()
        info_equip = self.get_info_equipment()
        date = FormatTime.get_name_day_and_date(self.cid.event_date)
        date_full = date.split(" ")[2::][0].split(".")
        date_full.reverse()

        dc["event_supply"] = loads(self.cid.event_supply)
        dc["net"] = self.get_net_all(self.cid)
        dc["gross"] = self.get_gross_all(self.cid)
        dc["pay_for_equipment"] = info_equip["money"]
        dc["count_of_equipment"] = info_equip["count"]
        dc["date_str"] = ".".join(date_full)
        dc["name_day"] = " ".join(date.split(" ")[0:2])
        dc["days_left"] = FormatTime.get_days_left("".join(date.split(" ")[2::]))
        dc["expen_fuel_i"] = str(float(self.cid.expen_fuel)).split(".")[0]
        dc["expen_fuel_d"] = str(float(self.cid.expen_fuel)).split(".")[1]
        dc["expen_employee_i"] = str(float(self.cid.expen_employee)).split(".")[0]
        dc["expen_employee_d"] = str(float(self.cid.expen_employee)).split(".")[1]
        dc["is_signature"] = DBAgreeApi.is_agreement_signed_by_cid(self._cid)
        # client.total_money
        # client.is_open
        # client.event_date
        # client.event_place
        # client.d_money
        # client.expen_employee
        # client.is_garbage
        # client.last_write
        # client.phone
        # client.write_by

        return dc

    def clientdb_to_dict(self):
        dict_cid = deepcopy(self.cid.__dict__)
        dict_cid.pop("_sa_instance_state")
        return dict_cid

    def get_total_client_payment(self):
        # /* TODO:
        pass


    def get_name_type_payment(self):
        tp = int(self.cid.type_pay)
        if tp == 0:
            return "מזומן"
        elif tp == 1:
            return "העברה בנקאית"
        elif tp == 2:
            return "צ'ק"
        # /* something broken! */
        return "לא צויין"

    def is_type_payment_valid(self):
        return 0 <= self.cid.type_pay <=2

    def set_event_status(self, status) -> bool:
        if status == 0:
            self.cid.is_garbage = True
            self.cid.is_open = False
            DBase.session.commit()
            return True
        elif status == 1:
            self.cid.is_open = False
            self.cid.is_garbage = False
            DBase.session.commit()
            return True
        elif status == 2:
            self.cid.is_open = True
            self.cid.is_garbage = False
            DBase.session.commit()
            return True

        return False

    def create_invoice_event(self, admin):
        res = False
        client = self.get_info_client()
        invoice = Invoice.query.first()
        if not invoice:
            num_invoice = Invoice(invoice_id=1000, client_id=self._cid)
            DBase.session.add(num_invoice)
            DBase.session.commit()
            invoice = Invoice.query.first()
            invoice.invoice_id = invoice.invoice_id+1
        else:
            invoice.invoice_id =  invoice.invoice_id+1


        self.cid.invoice_id = generate_invoice_path(client["phone"])
        usr = DBUserApi(admin)
        if not usr.ok() or not usr.info_exist():
            return False

        file_data = open(BASEDIR+"/tmp/invoice_tmp/invoice_client.html", "r", encoding="utf-8").read()
        style, body = file_data.split("<body>")

        tmp_format = body.format(owner_id=usr.u.identify,
                                     email=usr.u.email,
                                     number_invoice=invoice.invoice_id,
                                     client_name=client["full_name"],
                                     date=ctime(),
                                     type_pay=self.get_name_type_payment(),
                                     info_pay="לא צויין",
                                     date_pay=client["event_date"].replace("-","/"),
                                     total_money=client["client_payment"],
                                     total_money2=client["client_payment"])

        if sys.platform == "win32":
            res = pdfkit.from_string(style + tmp_format,
                                     self.cid.invoice_id, configuration=pdfkit.configuration(wkhtmltopdf=PATH_PDFKIT_EXE),
                                     options=PDF_OPTIONS)
        elif sys.platform == "linux":
            res = pdfkit.from_string(style + tmp_format,
                               self.cid.invoice_id,
                               options=PDF_OPTIONS)

        if res:
            DBase.session.commit()

        return self.get_invoice_client()

    def get_invoice_client(self) -> str | bool:
        return self.cid.invoice_id

    def reinvoice_client(self) -> bool:

        if os.path.exists(self.cid.invoice_id):
            os.remove(self.cid.invoice_id)
        self.cid.invoice_id = ""
        DBase.session.commit()
        return True


    def get_invoice_number(self) -> int:
        invoice = Invoice.query.filter_by(client_id=self.cid.client_id).first()
        if not  invoice:
            return 0

        return invoice.invoice_id


    def update_lead_information(self, kind:str, data:...):
        error = dict(UPDATE_LEAD_ERROR)
        # /* valid: id or is closed/garbage */
        if not self.ok():
            error["notice"] = "מזהה לא ידוע"
            return error
        elif not self.cid.is_open or self.cid.is_garbage:
            error["notice"] = "לא ניתן לעדכן אירוע סגור"
            return error

        if kind == "0":
            new_equip = loads(data)
            last_equip = self.get_client_equipment()
            for neq in new_equip:
                if not neq["count"].replace(" ", "").isdigit():
                    error["notice"] = f"{last_equip[neq['equip_id']]['name']} עם כמות שגויה "
                    return error
                last_equip[neq['equip_id']]["count"] = int(neq["count"])

            self.cid.event_supply = dumps(last_equip)
            DBase.session.commit()

        elif kind == "1":
            status, _ = check_level_new_lead('6', data)
            if not status:
                error["notice"] = "תאריך לא תקין"
                return error
            self.cid.event_date = data
            DBase.session.commit()

        elif kind == "2":
            status, _ = check_level_new_lead('7', data)
            if not status:
                error["notice"] = "המיקום לא תקין"
                return error
            self.cid.event_place = data
            DBase.session.commit()

        elif kind == "3":
            new_expense = loads(data)
            error['notice'] = "הוצאה לא תקינה"
            for index, exp in enumerate(new_expense):
                try:
                    new_expense[index] = int(float(exp.replace("₪", "")))
                except (TypeError,ValueError):
                    return error

            self.cid.expen_fuel = int(new_expense[0])
            self.cid.expen_employee = int(new_expense[1])
            DBase.session.commit()

        elif kind == "4":
            data = loads(data)
            dmoney = data["dmoney"].replace(" ", "").replace("₪", "")
            status, _ = check_level_new_lead('8', dmoney)
            if not status:
                error['notice'] = "מקדמה לא תקינה"
                return error
            # /* sec:bug <bypass less -1>
            if not data["type_pay"].isdigit() or not self.is_type_payment_valid():
                error["notice"] = "סוג תשלום לא תקין"
                return error

            self.cid.d_money = float(dmoney)
            self.cid.type_pay = int(data["type_pay"])
            DBase.session.commit()

        # /* important */
        self.reinvoice_client()

        return {"success":True}

    def create_agreement(self, admin, override) -> tuple:
        if not self.ok():
            return "לקוח לא קיים",0

        aapi = DBAgreeApi(self._cid, by_cid=True)
        return aapi.create_agreement(admin=admin, is_order=self.is_order_equipment(), override=override)


    def is_event_expired_date(self):
        date:list = self.cid.event_date.replace("-", ".").split(".")
        date.reverse()
        return FormatTime.get_days_left(".".join(date)) < 0

class Supply(DBase.Model):
    __tablname__    = "supply"
    index           = DBase.Column(DBase.Integer,       primary_key=True)
    name            = DBase.Column(DBase.String(500),   nullable=False)
    price           = DBase.Column(DBase.Integer,       nullable=False)
    desc            = DBase.Column(DBase.String(1000),  nullable=False)
    _id             = DBase.Column(DBase.String(20),    nullable=False)
    exist           = DBase.Column(DBase.Integer,       nullable=False)
    count           = DBase.Column(DBase.Integer,       nullable=False)
class DBSupplyApi:

    def __init__(self, ei:str):
        self.ei: None | Supply = None
        self._ei: str | None = None
        self.new(ei)

    def new(self, ei:str):
        self.ei = Supply.query.filter_by(_id=ei).first()
        self._ei= ei

    def ok(self) -> bool:
        return bool(self.ei)

    @staticmethod
    def verify_equipments(equip: dict) -> tuple[bool, dict]:
        equip_lead = {}
        try:
            for key, supply in equip.items():
                # db
                # self.new(supply['id'])
                # if int(supply['count']) > self.ei.exist:
                #     return False, db_supply.name, {}
                if int(supply["count"]):
                    equip_lead[key] = supply
        except (KeyError, Exception) as error:
            return False, {}

        return True, equip_lead

    @staticmethod
    def get_all_supply():
        _all = {}
        supplies: list[Supply] = Supply.query.all()
        for s in supplies:
            _all[s._id] = {"id": s._id, "name": s.name, "price": s.price, "exist": s.exist, "count": s.count}

        return _all

    @staticmethod
    def equipment_exist() -> bool:
        _all_ = Supply.query.all()
        return bool(_all_.__len__())

class Invoice(DBase.Model):
    __tablename__ = 'invoice'

    index           = DBase.Column(DBase.Integer,       primary_key=True)
    invoice_id      = DBase.Column(DBase.Integer,       nullable=False)
    client_id       = DBase.Column(DBase.Integer,       nullable=False)


class ClientAgreement(DBase.Model):
    __tablename__ = "agreement"
    index         = DBase.Column(DBase.Integer, primary_key=True)
    path          = DBase.Column(DBase.String, nullable=True)
    client_id     = DBase.Column(DBase.String, nullable=False)
    is_accepted   = DBase.Column(DBase.Boolean, nullable=False, default=False)
    agree_id      = DBase.Column(DBase.String, nullable=False)
    sig_owner     = DBase.Column(DBase.String, nullable=True)
    sig_client    = DBase.Column(DBase.String, nullable=True)
    sig_date      = DBase.Column(DBase.Float, nullable=False)
    from_date     = DBase.Column(DBase.String, nullable=False, default="01.01.1970")
    to_date       = DBase.Column(DBase.String, nullable=False, default="01.01.1970")
    location_client = DBase.Column(DBase.String, nullable=True)
    agree_sesslife = DBase.Column(DBase.Float, nullable=False)
    show_id       = DBase.Column(DBase.String, nullable=True)
class DBAgreeApi:

    def __init__(self, aid:str, by_cid=False):
        self.aid:None|ClientAgreement    = None
        self._aid:None|str   = None
        self.new(aid, by_cid=by_cid)

    def new(self, aid, by_cid=False, by_si=False):
        kwargs = {}
        if by_cid:
            kwargs['client_id'] = aid
        elif by_si:
            kwargs['show_id'] = aid
        else:
            kwargs["agree_id"] = aid
        self.aid: ClientAgreement = ClientAgreement.query.filter_by(**kwargs).first()
        self._aid = aid
        return self.ok()

    def ok(self):
        return bool(self.aid)
    def is_expired(self):
        return not (time() - self.aid.agree_sesslife) < 960

    @staticmethod
    def get_agreement_by_cid(cid:str):
        agree: ClientAgreement = ClientAgreement.query.filter_by(client_id=cid).first()
        if not agree:
            return False
        return agree

    def get_ctime_agree_sess(self):
        return ctime(self.aid.agree_sesslife+AGREE_SESS_LIFE)
    @staticmethod
    def get_ctime_agree_sess_by_cid(cid:str) -> str:
        a:ClientAgreement = DBAgreeApi.get_agreement_by_cid(cid)
        if not a:
            return "0"
        return ctime(a.agree_sesslife+AGREE_SESS_LIFE)

    def is_agreement_singed(self):
        return self.aid.sig_client and self.aid.sig_owner

    def is_accept(self):
        return self.aid.is_accepted

    @staticmethod
    def is_agreement_signed_by_cid(cid:str):
        a:ClientAgreement = DBAgreeApi.get_agreement_by_cid(cid)
        if not a:
            return False

        return bool(a.sig_client)

    def add_agreement(self, sig_client, data:list, capi:"DBClientApi" ,_e) -> dict:
        if self.is_expired():
            _e["notice"] = "הקישור פג תוקף"
            return  _e

        for i, v in zip([2, 7, 4, 3, 6], data):
            b, r = check_level_new_lead(str(i), v)
            if not b:
                return loads(r.get_data(True))

        self.aid.sig_client = sig_client
        self.aid.sig_date = time()
        self.aid.from_date = capi.cid.event_date
        self.aid.to_date = capi.cid.event_date
        self.aid.location_client = data[1]
        self.aid.is_accepted = True
        # /* success
        capi.cid.is_signature = True
        DBase.session.commit()

        return {"success":True}

    def create_agreement(self, admin,  is_order, override) -> tuple[str, int]:
        agree_id = generate_id_agree()
        usr = DBUserApi(admin)
        if not usr.ok():
            return "שיגאה בזיהוי המנהל", 0
        if self.ok() and self.aid.is_accepted:
            return "הלקוח חתם על החוזה", 0
        elif not is_order:
            return "אין ציוד בהזמנה", 0
        elif self.ok() and not self.aid.is_accepted:
            # /* update signature time and key */
            if override == "1":
                self.aid.agree_sesslife = time()
                self.aid.agree_id = agree_id
            else:
                agree_id = self.aid.agree_id
        elif not self.ok():
            # /* new signature */
            new_sig = ClientAgreement(
                client_id=self._aid,
                agree_id=agree_id,
                sig_date=time(),
                agree_sesslife=time(),
                sig_owner=usr.u.signature
            )
            DBase.session.add(new_sig)

        DBase.session.commit()

        return generate_link_edit_agree(self._aid, agree_id), True

    def set_show_agreement(self) -> str:
        if not self.aid.show_id and self.is_accept():
            self.aid.show_id = generate_ascii(10)
            DBase.session.commit()

        return generate_link_show_agree(self.aid.show_id, self.aid.client_id)

    def get_ctime_client_singed(self):
        if self.aid.sig_date:
            return ctime(self.aid.sig_date)
        return ctime(time())



def signup(**kwargs):
    user = Users(**kwargs)
    DBase.session.add(user)
    DBase.session.commit()


def db_new_client(**kwargs):
    n_client = Client(**kwargs)
    DBase.session.add(n_client)
    DBase.session.commit()


def add_supply(**kwargs):
    n_supply = Supply(**kwargs)
    DBase.session.add(n_supply)
    DBase.session.commit()


def generate_ascii(length:int = 5) -> str:
    return binascii.b2a_hex(os.urandom(length)).decode()


def generate_id_supply() ->str:
    return "E"+generate_ascii()

def generate_id_agree() ->str:
    return "A"+generate_ascii()


def import_txt_equipment(d:bytes, pwd=None) -> bool:
    try:
        new_supply = loads(XOR(d.decode(encoding="utf8"), pwd).decode())
    except (Exception, UnicodeDecodeError):
        return False
    if not new_supply:
        return False

    for nsupply in new_supply:
        supply = Supply()
        supply.name = nsupply["name"]
        supply.price = int(nsupply["price"])
        supply.desc = nsupply["desc"]
        supply._id = nsupply["_id"]
        supply.exist = int(nsupply["exist"])
        supply.count = int(nsupply["count"])
        DBase.session.add(supply)
        DBase.session.commit()
    return True


def export_txt_equipment(fp, pwd=None) -> bool:
    new_supply:list[Supply] = Supply.query.all()
    result:list[dict] = []
    if not new_supply:
        return False

    for equip in new_supply:
        dict_equip = deepcopy(equip.__dict__)
        dict_equip.pop('_sa_instance_state')
        result.append(dict_equip)

    buffer = dumps(result)
    with open(fp, "wb") as fexport:
        fexport.write(XOR(buffer, pwd))

    return True


def create_agreement_pdf():
    file_data = open(BASEDIR + "/tmp/invoice_tmp/agreement.html", "r", encoding="utf-8").read()
    style, body = file_data.split("<body>")

    tmp_format = body

    res = pdfkit.from_string(style + tmp_format,
                             r"C:\Users\saban\Desktop\web-pro\dvora-dash\agreements\test.pdf",
                             configuration=pdfkit.configuration(wkhtmltopdf=PATH_PDFKIT_EXE),
                             options=PDF_OPTIONS)


