import sys, os, sqlite3, urllib
from HTMLParser import HTMLParser
sensors = ['light', 'sound', 'UV', 'IR', 'temp', 'humid', 'tiltX', 'tiltY']
htmlParser = HTMLParser()
def isValidCache(cacheName):
    if(os.path.isfile(cacheName)):
        return True
    return False


class Cache:
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
        # cursor as part of class maybe a bad idea
        if(new):
            cursor =self.conn.cursor()
            cursor.execute('''CREATE TABLE sensorData (
                `id` INT AUTO_INCREMENT PRIMARY KEY,`SENSORID`,'''+','.join(sensors) + ')')
            cursor.execute('''CREATE TABLE scripts (
                `id` INT AUTO_INCREMENT PRIMARY KEY,`script`)''')

            self.conn.commit()
        pass
    def updateScripts(self, scripts):
        # DELETE ALL Scripts
        sql = ''' DELETE FROM scripts; '''
        cursor = self.conn.cursor()
        cursor.execute(sql)
        for script in scripts:
            sql = 'INSERT INTO scripts (script) VALUES (\''+script+'\')'
            cursor.execute(sql)
        # INSERT Scripts
        self.conn.commit()
        pass
    def addSensorData(self, device_id, data):
        toAdd = []
        toAdd.append(device_id)
        cursor = self.conn.cursor()
        for sensor in sensors:
            try:
                val = data.get(sensor,'NULL')
                if(val != 'NULL'):
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
        if Limit<=0 and Limit != None:
            raise ValueError('Limit Invalid')
        params = []
        sql = "SELECT * FROM scripts"
        cursor = self.conn.cursor()
        if(Limit!=None):
            sql = sql + " LIMIT ?"
            params.append(Limit)
        cursor.execute(sql,params)
        return cursor.fetchall()
    def close(self):
        self.conn.close()
