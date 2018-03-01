import sys, os, sqlite3, urllib, logging
from HTMLParser import HTMLParser
sensors = ['light', 'sound', 'UV', 'IR', 'temp', 'motion', 'humid', 'tiltX', 'tiltY', 'time']
htmlParser = HTMLParser()
logger = logging.getLogger()
def isValidCache(cacheName):
    if(os.path.isfile(cacheName)):
        return True
    return False


class Cache:
    """
    This abstracts over the Database any Insertions and Updates should not happen in the main thread
    """
    def __init__(self,db, new=False):
        file = db+'.db'
        if(not os.path.isfile(file)):
            new = True
        if(new):
            try:
                os.remove(file)
            except OSError:
                pass
        self.conn = sqlite3.connect(file)
        self.conn.row_factory = self.dict_factory
        if(new):
            cursor =self.conn.cursor()
            cursor.execute('''CREATE TABLE sensorData (
                `id` INT AUTO_INCREMENT PRIMARY KEY,`SENSORID`,'''+','.join(sensors) + ' )')
            cursor.execute('''CREATE TABLE scripts (
                `id` INT AUTO_INCREMENT PRIMARY KEY,`script`)''')

            self.conn.commit()
        pass
    def dict_factory(self, cursor, row):
        d = {}
        for idx,col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d

    def updateScripts(self, scripts):
        # DELETE ALL Scripts and INSERT new Scripts
        sql = ''' DELETE FROM scripts; '''
        cursor = self.conn.cursor()
        cursor.execute(sql)

        for script in scripts:
            sql = 'INSERT INTO scripts (script) VALUES (\''+script+'\')'
            cursor.execute(sql)
        self.conn.commit()
        pass
    def addSensorData(self, device_id, data):
        # INSERTs into sensorData table
        cursor = self.conn.cursor()
        toAdd = []
        toAdd.append(device_id)
        for sensor in sensors:
            try:
                val = data.get(sensor,'NULL')
                if(val != 'NULL' and val != None and sensor!= "SENSORID"):
                    val = float(val)
                toAdd.append(val)
            except ValueError:
                return False
        sql = 'INSERT INTO sensorData (SENSORID, '+','.join(sensors)+') VALUES(?,?,?,?,?,?,?,?,?,?,?)';
        cursor.execute(sql,toAdd)
        self.conn.commit()
        return True
        pass
    def getSensorDataFromID(self, device_id, Limit=None):
        # get sensorData from DB given a device_id
        if Limit<=0 and Limit != None:
            raise ValueError('Limit Invalid')
        params = []
        sql = "SELECT * FROM sensorData WHERE SENSORID=?"
        params.append(device_id)
        cursor = self.conn.cursor()
        if(Limit!=None):
            sql = sql + " LIMIT ?"
            params.append(Limit)
        cursor.execute(sql,params)
        return cursor.fetchall()
    def getLastTime(self):
        # get sensorData from DB given a device_id
        sql = "SELECT time FROM sensorData WHERE time NOT NULL  ORDER BY time DESC LIMIT 1;"
        cursor = self.conn.cursor()
        cursor.execute(sql)
        return cursor.fetchone()

    def getSensorData(self):
        # get sensorData from DB given a device_id
        sql = "SELECT * FROM sensorData WHERE time%(5*60) = 0";
        cursor = self.conn.cursor()
        cursor.execute(sql)
        data = cursor.fetchall()
        return data;
    def getScripts(self, Limit=None):
        # get all scripts
        if Limit<=0 and Limit != None:
            raise ValueError('Limit Invalid')
        params = []
        sql = "SELECT * FROM scripts"
        cursor = self.conn.cursor()
        if(Limit!=None):
            sql = sql + " LIMIT ?"
            params.append(Limit)
        cursor.execute(sql,params)
        its = []
        for item in cursor.fetchall():
            its.append(item[1])
        return its
    def close(self):
        self.conn.close()
