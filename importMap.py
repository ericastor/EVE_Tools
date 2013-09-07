import networkx as nx
import pickle, psycopg2

f = open('databaseLogin.txt')
host = f.readline().strip()
db = f.readline().strip()
user = f.readline().strip()
password = f.readline().strip()
f.close()

conn = psycopg2.connect(host=host, database=db, user=user, password=password)
cur = conn.cursor()

cur.execute("""
SELECT systems."solarSystemID" as system,
    systems."solarSystemName" as "systemName",
    systems."constellationID" as constellation,
    systems."regionID" as region,
    systems.security as security,
    systems."securityClass" as "securityClass",
    constellations."constellationName" as "constellationName",
    regions."regionName" as "regionName"
FROM public."mapSolarSystems" AS systems
    LEFT JOIN public."mapConstellations" as constellations
        ON constellations."constellationID"=systems."constellationID"
    LEFT JOIN public."mapRegions" as regions
        ON regions."regionID"=systems."regionID";
""")
d = cur.description

eveMap = nx.Graph()
sysID = {}
for row in cur:
    eveMap.add_node(row[0], {c.name: value for c, value in zip(d[1:], row[1:])})
    sysID[row[1]] = row[0]

cur.execute("""
SELECT "fromSolarSystemID", "toSolarSystemID"
FROM public."mapSolarSystemJumps"
WHERE "fromSolarSystemID"<"toSolarSystemID";
""")
for row in cur:
    eveMap.add_edge(row[0], row[1])

cur.close()
conn.close()

f = open("eveMap.pickle", "wb")
pickle.dump(eveMap, f)
f.close()
