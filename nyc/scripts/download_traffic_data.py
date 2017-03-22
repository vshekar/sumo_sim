import urllib2
import time
import csv
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker,scoped_session
from threading import Timer
from setup_db import Base, Link, Traffic

class NYCTrafficCollector:
    def __init__(self,Session):
        self.data = ""
        self.session = Session()

    def download(self):
        try:
            response = urllib2.urlopen('http://207.251.86.229/nyc-links-cams/LinkSpeedQuery.txt')
            self.data = response.readlines()
            #print self.data[1]
        except urllib2.HTTPError,e:
            print e.getcode()

    def parse_file(self):
        reader = csv.reader(self.data, delimiter='\t') 
        
        for i,row in enumerate(reader):
            if i !=0:        
                #print row
            
                dt = datetime.strptime(row[4],'%m/%d/%Y %H:%M:%S')
                
                if datetime.now().date() == dt.date():
                    links = self.session.query(Link).filter_by(link_id=int(row[0])).all()
                    if len(links) == 0:
                        link = Link(link_id=int(row[0]),name=row[12],link_points=row[6],enc_poly=row[7],enc_poly_lvls=row[8],borough=row[11])
                        self.session.add(link)
                        self.session.commit()
                    else:
                    #    print link[0]
                        link = links[0]
                    #print link
                    traffic = Traffic(link = link,speed = float(row[1]), travel_time = float(row[2]),timestamp=dt)
                    self.session.add(traffic)
                    self.session.commit()
        self.session.close()
            

    def run(self):
        print "Collecting data at : " + str(datetime.now())
        self.download()
        self.parse_file()
        #self.store_data()

def collect(args):
    
    ntc = NYCTrafficCollector(args)
    ntc.run()
    t = Timer(5*60.0,collect,args=[Session])
    t.start()

#def start():
sqlite_file = 'nyc_traffic.db'
engine = create_engine('sqlite:///'+sqlite_file)
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
Session =scoped_session(DBSession)

collect(Session)
#time.sleep(1)
#collect(DBSession)


