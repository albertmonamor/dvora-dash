import binascii
import os
from copy import deepcopy

import pdfkit
from json import dumps, loads
from time import time
from Api.api_function import XOR
from Api.protocol import DBase, m_app, PDF_OPTIONS, PATH_PDFKIT_EXE, BASEDIR


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


class Client(DBase.Model):
    __tablename__ = 'client'
    # for API
    index           = DBase.Column(DBase.Integer,       primary_key=True)
    write_by        = DBase.Column(DBase.String,        nullable=False)
    last_write      = DBase.Column(DBase.Float, nullable=False, default=time())
    is_open         = DBase.Column(DBase.Boolean,       nullable=False, default=True)
    is_garbage      = DBase.Column(DBase.Boolean,       nullable=False, default=False)
    is_signature   = DBase.Column(DBase.Boolean,        nullable=False, default=False)
    date_closed     = DBase.Column(DBase.Float,         nullable=True,  default=time())
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


