from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship


Base = declarative_base()

class Links(Base):
    """Describes links of the table"""
    __tablename__ = 'links'
    link_id = Column(Integer, primary_key=True)
    link = Column(Integer)
    length = Column(Float)
    sublinks = relationship("SubLinks", backref="links")
    sim_data = relationship("SimData", backref="links")
    

class SimData(Base):
    """Describes sim table"""
    __tablename__ = 'sim_data'
    sim_id = Column(Integer, primary_key=True)
    link = Column(Integer, ForeignKey('links.link_id'))
    start_time = Column(Integer)
    end_time = Column(Integer)
    sim_stats = relationship("SimStats", backref="sim_data")
    link_stats = relationship("LinkStats", backref="sim_data")
    #links = relationship(Links)
    def __repr__(self):
        return "<SimData(id='{}', link='{}', start_time='{}', end_time='{}')>".format(self.sim_id, \
        self.link, self.start_time, self.end_time)

class SubLinks(Base):
    """Describes sublinks within a link"""
    __tablename__ = 'sublinks'
    sublink_id = Column(Integer, primary_key=True)
    link = Column(Integer, ForeignKey('links.link_id'))
    sublink = Column(Integer)
    num_lanes = Column(Integer)
    sublink_length = Column(Float)
    link_stats = relationship("LinkStats", backref="sublinks")
    #links = relationship(Links)

class SimStats(Base):
    """Describes the overall stats of a simulation"""
    __tablename__ = 'sim_stats'
    sim_stats_id = Column(Integer, primary_key=True)
    sim_num = Column(Integer, ForeignKey('sim_data.sim_id'))
    total_time = Column(Integer)
    total_cars = Column(Integer)
    

class LinkStats(Base):
    """Describes stats at the link level"""
    __tablename__ = 'link_stats'
    link_stats_id = Column(Integer, primary_key=True)
    sim_num = Column(Integer, ForeignKey('sim_data.sim_id'))
    sublink = Column(Integer, ForeignKey('sublinks.sublink_id'))
    density = Column(Float)
    CO2 = Column(Float)
    NO2 = Column(Float)
    fuel = Column(Float)
    start_time = Column(Integer)
    end_time = Column(Integer)
    #sim_data = relationship(SimData)


if __name__=="__main__":
    print("start")
    engine = create_engine("sqlite:///test.db", echo=True)
    Base.metadata.create_all(engine)

def create_db(num):
    engine = create_engine("sqlite:///test{}.db".format(num), echo=True)
    Base.metadata.create_all(engine)
