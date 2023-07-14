import binascii
import os
import pdfkit
import sys
from json import dumps, loads
from time import ctime, time
from Api.api_function import FormatTime, generate_invoice_path, \
    check_level_new_lead, XOR
from Api.protocol import DBase, m_app, PDF_OPTIONS, PATH_PDFKIT_EXE, BASEDIR, UPDATE_LEAD_ERROR


class Users(DBase.Model):
    __tablename__ = "users"
    index       = DBase.Column(DBase.Integer, primary_key=True)
    user        = DBase.Column(DBase.String(20), nullable=False)
    pwd         = DBase.Column(DBase.String(10), nullable=False)
    ip          = DBase.Column(DBase.String(22), nullable=False)
    is_admin    = DBase.Column(DBase.Boolean, unique=False, default=False)

    def __repr__(self):
        return f"<{self.__tablename__}> {self.index}"


class Client(DBase.Model):
    __tablename__ = 'client'
    # for API
    index           = DBase.Column(DBase.Integer,       primary_key=True)
    write_by        = DBase.Column(DBase.String,        nullable=False)
    last_write      = DBase.Column(DBase.Float, nullable=False, default=time())
    is_open         = DBase.Column(DBase.Boolean,       nullable=False, default=True)
    is_garbage      = DBase.Column(DBase.Boolean,       nullable=False, default=False)
    invoice_id      = DBase.Column(DBase.String,        nullable=False, default="")
    client_id       = DBase.Column(DBase.String,        nullable=False, default=lambda:"C"+binascii.b2a_hex(os.urandom(5)).decode())
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
    # for API bool


class Supply(DBase.Model):
    __tablname__    = "supply"
    index           = DBase.Column(DBase.Integer,       primary_key=True)
    name            = DBase.Column(DBase.String(500),   nullable=False)
    price           = DBase.Column(DBase.Integer,       nullable=False)
    desc            = DBase.Column(DBase.String(1000),  nullable=False)
    _id             = DBase.Column(DBase.String(20),    nullable=False)
    exist           = DBase.Column(DBase.Integer,       nullable=False)
    count           = DBase.Column(DBase.Integer,       nullable=False)


class Invoice(DBase.Model):
    __tablename__ = 'invoice'

    index           = DBase.Column(DBase.Integer,       primary_key=True)
    invoice_id      = DBase.Column(DBase.Integer,       nullable=False)


class OwnerInformation(DBase.Model):

    __tablename__ = "owner"

    index       = DBase.Column(DBase.Integer, primary_key=True)
    full_name  = DBase.Column(DBase.String,  nullable=False)
    email       = DBase.Column(DBase.String,  nullable=False)
    identify    = DBase.Column(DBase.Integer,  nullable=False)
    phone       = DBase.Column(DBase.Integer,  nullable=False)


class ClientAgreement(DBase.Model):
    __tablename__ = "agreement"
    index         = DBase.Column(DBase.Integer, primary_key=True)
    path          = DBase.Column(DBase.String, nullable=False)
    client_id     = DBase.Column(DBase.String, nullable=False)
    is_accepted   = DBase.Column(DBase.Boolean, nullable=False, default=False)
    agree_id      = DBase.Column(DBase.String, nullable=False)


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

def get_all_supply():
    _all = {}
    supplies:list[Supply] = Supply.query.all()
    for s in supplies:
        _all[s._id] = {"id":s._id, "name":s.name, "price":s.price, "exist":s.exist, "count":s.count}

    return _all


def get_supply_by_id(_id) -> Supply:
    return Supply.query.filter_by(_id=_id).first()

def generate_id_supply() ->str:
    return "E"+str(len(Supply.query.all()))+binascii.b2a_hex(os.urandom(5)).decode()


def verify_supply(supp: dict) -> tuple[bool, dict]:
    _supply_lead = {}
    try:
        for key, supply in supp.items():
            # db
            db_supply = get_supply_by_id(supply["id"])
            # if int(supply['count']) > db_supply.exist:
            #     return False, db_supply.name, {}
            if int(supply["count"]):
                _supply_lead[key] = supply
    except (KeyError,Exception) as error:
        return False, {}

    return True, _supply_lead

# signup(user='דבי', pwd='משי', ip='2.55.187.108')


# /* supply for events
# /* from static to database for dynamic actions


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
        equip.__dict__.pop('_sa_instance_state')
        result.append(equip.__dict__)

    buffer = dumps(result)
    with open(fp, "wb") as fexport:
        fexport.write(XOR(buffer, pwd))

    return True

class DBClientApi:

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

    def is_pay_down_payment(self, value:int) -> bool:
        return bool(value)

    def is_order_equipment(self, value:str) -> bool:
        equipments = loads(value)
        return bool(len(equipments))

    def is_low_expenses(self, c:Client):
        return self.get_net(c) >= 1000
    def get_gross(self, c:Client) -> float | int:
        money_equipments = self.get_info_equipment(c)["money"]
        return c.expen_fuel+c.expen_employee+money_equipments

    def get_net(self, c:Client) -> float | int:
        result = self.get_info_equipment(c)["money"] - c.expen_fuel - c.expen_employee

        return result

    def get_info_equipment(self, c:Client) -> dict:
        equipments = {"money":0, "count":0}
        if self.is_order_equipment(c.event_supply):
            equipment = loads(c.event_supply)
            for index, equip in equipment.items():
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
                             "ps": self.is_pay_down_payment(c.d_money),
                             "tm": f"{self.get_gross(c):,}",
                             "oe": self.is_order_equipment(c.event_supply),
                             "cm": f"{self.get_net(c):,}",
                             'low_e': self.is_low_expenses(c),
                             'ea':c.is_open,
                             "eg":c.is_garbage,
                           }
        return client

    def get_info_client(self,_id) -> dict:

        if not _id:
            return {}

        client:Client = Client.query.filter_by(client_id=_id).first()
        if not client:
            return {}

        dc = self.clientdb_to_dict(client)
        info_equip = self.get_info_equipment(client)
        date = FormatTime.get_name_day_and_date(client.event_date)
        date_full = date.split(" ")[2::][0].split(".")
        date_full.reverse()

        dc["event_supply"] = loads(client.event_supply)
        dc["net"] = self.get_net(client)
        dc["gross"] = self.get_gross(client)
        dc["pay_for_equipment"] = info_equip["money"]
        dc["count_of_equipment"] = info_equip["count"]
        dc["date_str"] = ".".join(date_full)
        dc["name_day"] = " ".join(date.split(" ")[0:2])
        dc["days_left"] = FormatTime.get_days_left("".join(date.split(" ")[2::]))
        dc["expen_fuel_i"] = str(float(client.expen_fuel)).split(".")[0]
        dc["expen_fuel_d"] = str(float(client.expen_fuel)).split(".")[1]
        dc["expen_employee_i"] = str(float(client.expen_employee)).split(".")[0]
        dc["expen_employee_d"] = str(float(client.expen_employee)).split(".")[1]
        client.total_money
        client.is_open
        client.event_date
        client.event_place
        client.d_money
        client.expen_employee
        client.is_garbage
        client.last_write
        client.phone
        client.write_by

        return dc

    def clientdb_to_dict(self, c:Client):

        c.__dict__.pop("_sa_instance_state")
        return dict(c.__dict__)

    def get_total_client_payment(self, c:Client | dict):
        # /* TODO:
        if isinstance(c, Client):
            dc = self.clientdb_to_dict(c)

    def get_name_type_payment(self, c:dict):
        if c["type_pay"] == 0:
            return "מזומן"
        elif c["type_pay"] == 1:
            return "העברה בנקאית"
        elif ["c.type_pay"] == 2:
            return "צ'ק"

        # /* something broken! */
        return "לא צויין"

    def set_event_status(self, status, client_id) -> bool:
        client = Client.query.filter_by(client_id=client_id).first()
        if not client:
            return False
        if status == 0:
            client.is_garbage = True
            client.is_open = False
            DBase.session.commit()
            return True
        elif status == 1:
            client.is_open = False
            client.is_garbage = False
            DBase.session.commit()
            return True

        return False

    def create_invoice_event(self, cid, name_owner):
        res = False
        client = self.get_info_client(cid)
        if not client:return False
        invoice = Invoice.query.first()
        if not invoice:
            num_invoice = Invoice(invoice_id=1000)
            DBase.session.add(num_invoice)
            DBase.session.commit()
            invoice = Invoice.query.first()
            invoice.invoice_id = invoice.invoice_id+1
        else:
            invoice.invoice_id =  invoice.invoice_id+1

        dbc = Client.query.filter_by(client_id=cid).first()
        dbc.invoice_id = generate_invoice_path(client["phone"])

        file_data = open(BASEDIR+"/tmp/invoice_tmp/invoice_client.html", "r", encoding="utf-8").read()
        style, body = file_data.split("<body>")

        tmp_format = body.format(owner_id="325576854",
                                     email="dvir@gmail.com",
                                     number_invoice=invoice.invoice_id,
                                     client_name=client["full_name"],
                                     date=ctime(),
                                     type_pay=self.get_name_type_payment(client),
                                     info_pay="לא צויין",
                                     date_pay=client["event_date"].replace("-","/"),
                                     total_money=client["net"],
                                     total_money2=client["net"])

        if sys.platform == "win32":
            res = pdfkit.from_string(style + tmp_format,
                                     dbc.invoice_id, configuration=pdfkit.configuration(wkhtmltopdf=PATH_PDFKIT_EXE),
                                     options=PDF_OPTIONS)
        elif sys.platform == "linux":
            res = pdfkit.from_string(style + tmp_format,
                               dbc.invoice_id,
                               options=PDF_OPTIONS)

        if res:
            DBase.session.commit()

        return dbc.invoice_id

    def get_invoice_client(self, cid:str) -> str | bool:
        client = Client.query.filter_by(client_id=cid).first()
        if not client:
            return False

        return client.invoice_id


    def reinvoice_client(self, cid:str) -> bool:
        dbc = Client.query.filter_by(client_id=cid).first()
        if not dbc:
            return False

        if os.path.exists(dbc.invoice_id):
            os.remove(dbc.invoice_id)
        dbc.invoice_id = ""
        DBase.session.commit()
        return True

    def update_lead_information(self, kind:str, data:..., client_id):
        error = dict(UPDATE_LEAD_ERROR)
        client = Client.query.filter_by(client_id=client_id).first()
        # /* valid: id or is closed/garbage */
        if not client:
            error["notice"] = "מזהה לא ידוע"
            return error
        elif not client.is_open or client.is_garbage:
            error["notice"] = "לא ניתן לעדכן אירוע סגור"
            return error

        if kind == "0":
            new_equip = loads(data)
            last_equip = loads(client.event_supply)
            for neq in new_equip:
                if not neq["count"].replace(" ", "").isdigit():
                    error["notice"] = f"{last_equip[neq['equip_id']]['name']} עם כמות שגויה "
                    return error
                last_equip[neq['equip_id']]["count"] = int(neq["count"])

            client.event_supply = dumps(last_equip)
            DBase.session.commit()

        elif kind == "1":
            status, _ = check_level_new_lead('6', data)
            if not status:
                error["notice"] = "תאריך לא תקין"
                return error
            client.event_date = data
            DBase.session.commit()

        elif kind == "2":
            status, _ = check_level_new_lead('7', data)
            if not status:
                error["notice"] = "המיקום לא תקין"
                return error
            client.event_place = data
            DBase.session.commit()

        elif kind == "3":
            new_expense = loads(data)
            error['notice'] = "הוצאה לא תקינה"
            for index, exp in enumerate(new_expense):
                try:
                    new_expense[index] = int(float(exp.replace("₪", "")))
                except (TypeError,ValueError):
                    return error

            client.expen_fuel = int(new_expense[0])
            client.expen_employee = int(new_expense[1])
            DBase.session.commit()


        self.reinvoice_client(client_id)

        return {"success":True}


def create_agreement_client():
    file_data = open(BASEDIR + "/tmp/invoice_tmp/agreement.html", "r", encoding="utf-8").read()
    style, body = file_data.split("<body>")

    tmp_format = body

    res = pdfkit.from_string(style + tmp_format,
                             r"C:\Users\saban\Desktop\web-pro\dvora-dash\agreements\test.pdf",
                             configuration=pdfkit.configuration(wkhtmltopdf=PATH_PDFKIT_EXE),
                             options=PDF_OPTIONS)


