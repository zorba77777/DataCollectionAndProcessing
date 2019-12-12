from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import (Column, ForeignKey, String, Integer, Date)
from sqlalchemy.orm import relationship
from datetime import date

from lesson2.ApiFetcher import ApiFetcher

Base = declarative_base()


class PromoEntity(Base):
    __tablename__ = 'promos'
    id = Column(Integer, primary_key=True)
    date_begin = Column(Date)
    date_end = Column(Date)
    type = Column(String)
    description = Column(String)
    kind = Column(String)
    expired_at = Column(Integer)

    def __init__(self, id: int, date_begin: date, date_end: date, type: str, description: str, kind: str,
                 expired_at: int):
        self.id = id
        self.date_begin = date_begin
        self.date_end = date_end
        self.type = type
        self.description = description
        self.kind = kind
        self.expired_at = expired_at


class ProductEntity(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    img_link = Column(String)
    price_reg_min = Column(Integer)
    price_promo_min = Column(Integer)
    __promo = Column(Integer, ForeignKey('promos.id'))
    promo = relationship('PromoEntity', backref='products')

    def __init__(self, id: int, name: str, img_link: str, price_reg_min: int, price_promo_min: int, promo: PromoEntity):
        self.id = id
        self.name = name
        self.img_link = img_link
        self.price_reg_min = price_reg_min
        self.price_promo_min = price_promo_min
        self.promo = promo


class PyaterkaDb:
    __session: Session

    def __init__(self, base, db_url):
        engine = create_engine(db_url)
        base.metadata.create_all(engine)
        session_db = sessionmaker(bind=engine)
        self.__session = session_db()

    @property
    def session(self) -> Session:
        return self.__session


db_url = 'sqlite:///pyaterka.sqlite'
db = PyaterkaDb(Base, db_url)

api_fetcher = ApiFetcher()
url = 'https://5ka.ru/api/v2/special_offers/?records_per_page=20'

data = api_fetcher.fetch_from_api('https://5ka.ru/api/v2/special_offers/?records_per_page=20')

for item in data['results']:
    tmp_promo = db.session.query(PromoEntity).get(item['promo']['id'])
    if not tmp_promo:
        tmp_promo = PromoEntity(
            item['promo']['id'],
            date.fromisoformat(item['promo']['date_begin']),
            date.fromisoformat(item['promo']['date_end']),
            item['promo']['type'],
            item['promo']['description'],
            item['promo']['kind'],
            item['promo']['expired_at']
        )
    tmp_product = ProductEntity(
        item['id'],
        item['name'],
        item['img_link'],
        item['current_prices']['price_reg__min'],
        item['current_prices']['price_promo__min'],
        tmp_promo
    )
    db.session.add(tmp_product)

db.session.commit()
