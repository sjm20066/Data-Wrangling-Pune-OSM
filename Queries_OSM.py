#Number of 'Node' tags
import sqlite3
db = sqlite3.connect("pune.db")
c = db.cursor()
QUERY = '''SELECT count(*)as num from nodes;
'''
c.execute(QUERY)
rows = c.fetchall()
import pandas as pd    
df = pd.DataFrame(rows)
print df
db.close()


#Number of 'Way' tags
import sqlite3
db = sqlite3.connect("pune.db")
c = db.cursor()
QUERY = '''SELECT count(*)as num from ways;
'''
c.execute(QUERY)
rows = c.fetchall()
import pandas as pd    
df = pd.DataFrame(rows)
print df
db.close()


#Number of unique users:
import sqlite3
db = sqlite3.connect("pune.db")
c = db.cursor()
QUERY = '''SELECT DISTINCT(user) from (select user from nodes UNION ALL select user from ways);

'''
c.execute(QUERY)
rows = c.fetchall()
import pandas as pd    
df = pd.DataFrame(rows)
#print df
print len(df)

db.close()


#User Stats
import sqlite3
db = sqlite3.connect("pune.db")
c = db.cursor()
QUERY = '''SELECT user,count(user)  from (select user from nodes UNION ALL select user from ways)
group by user
order by  count(user) desc
;
'''
c.execute(QUERY) 
rows = c.fetchall()
import pandas as pd    
df = pd.DataFrame(rows)
print "Number of users : ",len(df)
print "\nTotal Number of Contributions : ",df[1].sum()

print "\nContribution Stats \n",df[1].describe()


db.close()


#Top 5 contributers
import sqlite3
db = sqlite3.connect("pune.db")
c = db.cursor()
QUERY = '''SELECT user,count(user)  from (select user from nodes UNION ALL select user from ways)
group by user
order by  count(user) desc
limit 5;
'''
c.execute(QUERY) 
rows = c.fetchall()
import pandas as pd    
df = pd.DataFrame(rows)
print df
db.close()


#Amenities and their count 
import sqlite3
db = sqlite3.connect("pune.db")
c = db.cursor()
QUERY = '''SELECT value,count(*)as num from (select value,key from nodes_tags  UNION ALL select value,key from ways_tags)
where key='amenity'
group by value
order by num desc
;
'''
c.execute(QUERY)
rows = c.fetchall()
import pandas as pd    
df = pd.DataFrame(rows)
print "Number of amenities  available in PUNE CITY :", len(df)
print (df)

db.close()


#Restaurant cusines available and their count 
import sqlite3
db = sqlite3.connect("pune.db")
c = db.cursor()
QUERY = '''SELECT value,count(*)as num from (select value,key from nodes_tags  UNION ALL select value,key from ways_tags)
where key='cuisine'
group by value
order by num desc
;
'''
c.execute(QUERY)
rows = c.fetchall()
import pandas as pd    
df = pd.DataFrame(rows)
print "Number of cuisines available in PUNE CITY :", len(df)
print (df)

db.close()
