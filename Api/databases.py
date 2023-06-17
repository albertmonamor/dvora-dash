import binascii
import os
import random

from Api.api_function import get_format_last_write, get_name_date_by_str
from Api.protocol import DBase, m_app
from time import time, ctime, gmtime, sleep

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
    client_id       = DBase.Column(DBase.String,        nullable=False, default=lambda:"C"+binascii.b2a_hex(os.urandom(5)).decode())
    # datas
    full_name       = DBase.Column(DBase.String(20),    nullable=False)
    phone           = DBase.Column(DBase.String(20),    nullable=False)
    ID              = DBase.Column(DBase.String(11),    nullable=False)
    # id of item in other DB
    event_supply    = DBase.Column(DBase.String(100),   nullable=False)
    event_date      = DBase.Column(DBase.String,        nullable=False)
    event_place     = DBase.Column(DBase.String,        nullable=False)
    # expenditure
    expen_employee  = DBase.Column(DBase.Float,         nullable=False, default=0)
    expen_fuel      = DBase.Column(DBase.Float,         nullable=False, default=0)
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


# from json import dumps
# from time import ctime, time
#
# new_lead(write_by="אברהם", full_name="משה רועי", phone="0585005617", ID="324104173",
#          event_supply=dumps(['0', '12', '56', '2']), event_date=time() + 10000,
#          event_place="31.783203, 34.625719", determine_money=4850, pay_sub=True, money_left=4850 / 2,
#          is_open=True)

from json import dumps, loads
from time import ctime, time

# new_lead(write_by="אברהם", full_name="משה רועי", phone="0585005617", ID="324104173",
#          event_supply=dumps(['0', '12', '56', '2']), event_date=time() + 10000,
#          event_place="31.783203, 34.625719", determine_money=4850, pay_sub=True, money_left=4850 / 2,
#          is_open=True)
"""

"""
# signup(user='דבי', pwd='משי', ip='2.55.187.108')


# /* supply for events
# /* from static to database for dynamic actions
SUPPLY = {"s1":
              {"name":"הגברה", "price": "800", "desc":"", "id":"s1", "count":"0", "exist":"2"},
          "s2":
              {"name":"מיקסר", "price":"299", "desc":"", "id":"s2", "count":"0", "exist":"4"},
          "s3":
              {"name":"צליה", "price":"700", "desc":"", "id":"s3", "count":"0", "exist":"3"},
          "s4":
              {"name":"גנרטור", "price":"500", "desc":"", "id":"s4", "count":"0", "exist":"2"},
          "s5":
              {"name":"ספסל ישיבה", "price":"40", "desc":"", "id":"s5", "count":"0", "exist":"14"},
          "s6":
              {"name":"שולחן ישיבה", "price":"40", "desc":"", "id":"s6", "count":"0", "exist":"14"}
          }


class DBClientApi:

    def get_all_client_by_mode(self, mode:str = "open", **kwargs):
        # which mode?
        if mode == "open":
            _client: list[Client] = Client.query.filter_by(is_open=True, **kwargs).all()
        elif mode == "close":
            _client: list[Client] = Client.query.filter_by(is_open=False, **kwargs).all()
        elif mode == "garbage":
            _client: list[Client] = Client.query.filter_by(is_garbage=True, **kwargs).all()
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
        money_equipments = self.get_money_equipment(c)
        return c.expen_fuel+c.expen_employee+money_equipments

    def get_net(self, c:Client) -> float | int:
        result = self.get_money_equipment(c)-c.expen_fuel-c.expen_employee

        return result

    def get_money_equipment(self, c:Client) -> float | int:
        money_equipments = 0
        if self.is_order_equipment(c.event_supply):
            equipment = loads(c.event_supply)
            for index, equip in equipment.items():
                money_equipments+= int(equip["price"]*int(equip["count"]))

        return money_equipments

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
                             "lw": get_format_last_write(c.last_write),
                             "fn": c.full_name,
                             "phone": c.phone,
                             "id": c.ID,
                             "es": c.event_supply,
                             "ed":get_name_date_by_str(c.event_date),
                             "ep": c.event_place,
                             "dm": c.d_money,
                             "ps": self.is_pay_down_payment(c.d_money),
                             "tm": f"{self.get_gross(c):,}",
                             "oe": self.is_order_equipment(c.event_supply),
                             "cm": f"{self.get_net(c):,}",
                             'low_e': self.is_low_expenses(c)
                           }
        return client