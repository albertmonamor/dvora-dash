from Api.protocol import DBase, m_app
from datetime import datetime


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
    last_write      = DBase.Column(DBase.DateTime,      nullable=False,default=datetime.utcnow)
    full_name       = DBase.Column(DBase.String(20),    nullable=False)
    phone           = DBase.Column(DBase.String(20),    nullable=False)
    ID              = DBase.Column(DBase.String(11),    nullable=False)
    event_supply    = DBase.Column(DBase.String(500),   nullable=False)
    event_date      = DBase.Column(DBase.Float,         nullable=False)
    event_place     = DBase.Column(DBase.String,        nullable=False)
    determine_money = DBase.Column(DBase.Float,         nullable=False)
    pay_sub         = DBase.Column(DBase.Boolean,       default=False, unique=False)
    money_left      = DBase.Column(DBase.Float,         nullable=False)
    is_open         = DBase.Column(DBase.Boolean,       nullable=False)



def signup(**kwargs):
    user = Users(**kwargs)
    DBase.session.add(user)
    DBase.session.commit()


def new_lead(**kwargs):
    n_lead = Leads(**kwargs)
    DBase.session.add(n_lead)
    DBase.session.commit()


# from json import dumps
# from time import ctime, time
#
# new_lead(write_by="אברהם", full_name="משה רועי", phone="0585005617", ID="324104173",
#          event_supply=dumps(['0', '12', '56', '2']), event_date=time() + 10000,
#          event_place="31.783203, 34.625719", determine_money=4850, pay_sub=True, money_left=4850 / 2,
#          is_open=True)



# /* supply for events

SUPPLY = [
    {"name":"הגברה", "price": "800", "id":"s1"},
    {"name":"מיקסר", "price":"299", "id":"s2"},
    {"name":"צליה", "price":"700", "id":"s3"},
    {"name":"גנרטור", "price":"500", "id":"s4"},
    {"name":"ספסל ישיבה", "price":"40", "id":"s5"},
    {"name":"שולחן ישיבה", "price":"40", "id":"s6"},

]