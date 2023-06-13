import random

from Api.api_function import get_format_last_write, get_name_date_by_str
from Api.protocol import DBase, m_app
from time import time, ctime, gmtime, sleep
from flask_migrate import Migrate

db_migrate = Migrate(m_app, DBase)

class Users(DBase.Model):
    __tablename__ = "users"
    index       = DBase.Column(DBase.Integer, primary_key=True)
    user        = DBase.Column(DBase.String(20), nullable=False)
    pwd         = DBase.Column(DBase.String(10), nullable=False)
    ip          = DBase.Column(DBase.String(22), nullable=False)
    is_admin    = DBase.Column(DBase.Boolean, unique=False, default=False)

    def __repr__(self):
        return f"<{self.__tablename__}> {self.index}"


class Leads(DBase.Model):
    __tablename__   = "leads"
    index           = DBase.Column(DBase.Integer,       primary_key=True)
    write_by        = DBase.Column(DBase.String,        nullable=False)
    last_write      = DBase.Column(DBase.Float,         nullable=False,default=time())
    full_name       = DBase.Column(DBase.String(20),    nullable=False)
    phone           = DBase.Column(DBase.String(20),    nullable=False)
    ID              = DBase.Column(DBase.String(11),    nullable=False)
    event_supply    = DBase.Column(DBase.String(500),   nullable=False)
    event_date      = DBase.Column(DBase.String,        nullable=False)
    event_place     = DBase.Column(DBase.String,        nullable=False)
    determine_money = DBase.Column(DBase.Float,         nullable=False)
    pay_sub         = DBase.Column(DBase.Boolean,       default=False, unique=False)
    total_money     = DBase.Column(DBase.Float,         nullable=False)
    order_equip     = DBase.Column(DBase.Boolean,       default=False, unique=False)
    is_open         = DBase.Column(DBase.Boolean,       nullable=False, default=True)
    clear_money     = DBase.Column(DBase.Float,         nullable=False)



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


def db_new_lead(**kwargs):
    n_lead = Leads(**kwargs)
    DBase.session.add(n_lead)
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


def get_all_leads_open()-> dict[int, dict]:
    _all = {}
    leads:list[Leads] = Leads.query.filter_by(is_open=True).all()
    for index, lead in enumerate(leads):
        _all[index] = {"wb":lead.write_by,   "lw":get_format_last_write(lead.last_write),
                       "fn":lead.full_name,  "phone":lead.phone,
                       "id":lead.ID,         "es":lead.event_supply,
                       "ed":get_name_date_by_str(lead.event_date), "ep":lead.event_place,
                       "dm":lead.determine_money, "ps":lead.pay_sub,
                       "tm":f"{lead.total_money:,}",  "oe":lead.order_equip,
                       "cm":f"{lead.clear_money:,}"
                       }
    return _all
def get_supply_by_id(_id) -> Supply:
    return Supply.query.filter_by(_id=_id).first()


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
            db_supply.exist = db_supply.exist - int(supply["count"])
            DBase.session.commit()
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

from json import dumps
from time import ctime, time

# new_lead(write_by="אברהם", full_name="משה רועי", phone="0585005617", ID="324104173",
#          event_supply=dumps(['0', '12', '56', '2']), event_date=time() + 10000,
#          event_place="31.783203, 34.625719", determine_money=4850, pay_sub=True, money_left=4850 / 2,
#          is_open=True)
"""

"""
# signup(user='דבי', pwd='משי', ip='2.55.187.108')
# add_supply(name="הגברה", price=800, desc="",    _id="s1", exist=0, count=0)
# add_supply(name="מיקסר", price=299, desc="",    _id="s2", exist=0, count=0)
# add_supply(name="צליה", price=700, desc="",     _id="s3", exist=0, count=0)
# add_supply(name="גנרטור", price=500, desc="",    _id="s4", exist=0, count=0)
# add_supply(name="ספסל ישיבה", price=40, desc="", _id="s5", exist=0, count=0)
# add_supply(name="שולחן ישיבה", price=40, desc="",_id="s6", exist=0, count=0)


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
