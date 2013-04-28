from multiprocessing import Pool
import operator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, PickleType
from sqlalchemy.ext.declarative import declarative_base

import cPickle as pickle

files = ["gQuery_onelab3.info.ucl.ac.be.db",
        "gQuery_pl1.6test.edu.cn.db",
        "gQuery_planet-lab4.uba.ar.db",
        "gQuery_planetlab-13.e5.ijs.si.db",
        "gQuery_planetlab-2.cmcl.cs.cmu.edu.db",
        "gQuery_planetlab-coffee.ait.ie.db",
        "gQuery_planetlab01.tkn.tu-berlin.de.db",
        "gQuery_planetlab1.cs.ucla.edu.db",
        "gQuery_planetlab1.cs.uoregon.edu.db",
        "gQuery_planetlab1.lkn.ei.tum.de.db",
        "gQuery_planetlab1.xeno.cl.cam.ac.uk.db",
        "gQuery_planetlab2.csg.uzh.ch.db",
        "gQuery_planetlab2.iitkgp.ac.in.db",
        "gQuery_planetlab2.ionio.gr.db",
        "gQuery_planetlab4.wail.wisc.edu.db",
        "gQuery_ple01.fc.univie.ac.at.db",
        "gQuery_pnode1.pdcc-ntu.singaren.net.sg.db"]

def extract(db_name):
    try:
        print db_name
        results = []
        engine = create_engine('sqlite:///' + db_name, echo=False)
        Base = declarative_base(bind=engine)

        class Query(Base):
            __tablename__ = 'data'

            id = Column(Integer, primary_key=True)
            index = Column(PickleType)
            query = Column(PickleType)
            return_ip = Column(PickleType)
            queryTime = Column(PickleType)
            googleTime = Column(PickleType)
            pingTime = Column(PickleType)
            tcpEntries = Column(PickleType)


        Session = sessionmaker(bind=engine)
        s = Session()
        for r in s.query(Query).all():
            results.append((r.index, r.query, r.return_ip,
                            r.queryTime, r.googleTime, r.pingTime))
        print db_name, 'Done'
        return results
    except:
        print db_name, 'Error'
        return []

p = Pool(20)

results = reduce(operator.add, p.map(extract, files))

cPickle.dump(results, open('querydb.pickle'))
