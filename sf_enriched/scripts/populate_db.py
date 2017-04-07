"""Populates db with links from the network
"""

from __future__ import print_function
from sqlalchemy import create_engine, null
from sqlalchemy.orm import sessionmaker
from setup_database import SimData, SimStats, SubLinks, LinkStats, Base, Links
import sumolib

ENGINE = create_engine('sqlite:///test.db')
Base.metadata.bind = ENGINE
DBSession = sessionmaker(bind=ENGINE)
SESSION = DBSession()

def pop_db():
    links, link_lengths, num_lanes = extract_links()
    pop_links(links, link_lengths, num_lanes)
    
def pop_links(links, link_lengths, num_lanes):
    for link in links.keys():
        Link = Links(link=int(link),length=sum(link_lengths[link]))
        if link == "1":
            print(link_lengths[link])
            print(sum(link_lengths[link]))
            print(links[link])
        SESSION.add(Link)
        SESSION.commit()
        Link = SESSION.query(Links).filter(Links.link == link).first()
        for start_time in range(0, 86400, 3600):
            end_time = start_time + 3600
            Sim = SimData(link=Link.link_id, start_time=start_time, end_time=end_time)
            SESSION.add(Sim)
        SESSION.commit()
        for i,sublink in enumerate(links[link]):
            if link == "1":
                print(num_lanes[link])
            Sublink = SubLinks(link=Link.link_id, sublink=int(sublink), num_lanes=num_lanes[link], sublink_length=link_lengths[link][i])
            SESSION.add(Sublink)
        SESSION.commit()


def extract_links():
    net = sumolib.net.readNet('../network/SF_with_TLS.net.xml')
    links = {}
    link_lengths = {}
    num_lanes = {}
    for edge in net.getEdges():
        split_edges = edge.getID().split('_')
        if split_edges[0] not in links.keys():
            links[split_edges[0]] = [split_edges[1]]
            link_lengths[split_edges[0]] = [edge.getLength()]
            num_lanes[split_edges[0]] = edge.getLaneNumber()
        else:
            links[split_edges[0]].append(split_edges[1])
            link_lengths[split_edges[0]].append(edge.getLength())
            num_lanes[split_edges[0]] = edge.getLaneNumber()
    return links,link_lengths, num_lanes


if __name__=="__main__":
    pop_db()
    Link = Links(link=null(),length=0)
    SESSION.add(Link)
    SESSION.commit()
    Sim = SimData(link=Link.link_id, start_time=0, end_time=0)
    SESSION.add(Sim)
    SESSION.commit()
    #link = SESSION.query(Links).filter(Links.link == null()).one()
    #print(link.link)