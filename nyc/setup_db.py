from sqlalchemy import create_engine,Column, Integer, String, ForeignKey, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Link(Base):
    __tablename__ = 'links'

    id = Column(Integer, primary_key=True)
    link_id = Column(Integer)
    name = Column(String)
    link_points = Column(String)
    enc_poly = Column(String)
    enc_poly_lvls = Column(String)
    borough = Column(String)

    #def __repr__(self):

class Traffic(Base):
    __tablename__= 'traffic'

    id = Column(Integer, primary_key=True)
    link_id = Column(Integer, ForeignKey('links.link_id'))
    link = relationship(Link)
    speed = Column(Float)
    travel_time = Column(Float)
    timestamp = Column(DateTime)

engine = create_engine('sqlite:///nyc_traffic.db',echo=True)
Base.metadata.create_all(engine)

