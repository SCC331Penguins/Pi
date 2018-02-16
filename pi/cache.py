import sys, os, sqlite3, urllib
from HTMLParser import HTMLParser
sensors = ['light', 'sound', 'UV', 'IR', 'temp', 'humid', 'tiltX', 'tiltY']
htmlParser = HTMLParser()
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
        if(new):
            cursor =self.conn.cursor()
            cursor.execute('''CREATE TABLE sensorData (
                `id` INT AUTO_INCREMENT PRIMARY KEY,`SENSORID`,'''+','.join(sensors) + ')')
            cursor.execute('''CREATE TABLE scripts (
                `id` INT AUTO_INCREMENT PRIMARY KEY,`script`)''')

            self.conn.commit()
        pass
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
        toAdd = []
        toAdd.append(device_id)
        cursor = self.conn.cursor()
        for sensor in sensors:
            try:
                val = data.get(sensor,'NULL')
                print(val)
                if(val != 'NULL' and val != None and sensor!= "SENSORID"):
                    val = float(val)
                toAdd.append(val)
            except ValueError:
                return False
        sql = 'INSERT INTO sensorData (SENSORID, '+','.join(sensors)+') VALUES(?,?,?,?,?,?,?,?,?)';
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
