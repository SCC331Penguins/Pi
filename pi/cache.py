import sys, os, sqlite3, urllib, logging, calendar, datetime
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
            cursor.execute('''CREATE TABLE status (
                `id` INT AUTO_INCREMENT PRIMARY KEY,`timestamp`, `userlocation`, `armed`)''')
            cursor.execute('''CREATE TABLE configButtons (
                `id` INT AUTO_INCREMENT PRIMARY KEY,`timestamp`, `1`, `2`,`3`,`4`)''')
            self.setStatus({'userlocation':'Unknown', 'armed':False})
            self.conn.commit()
        pass
    def dict_factory(self, cursor, row):
        d = {}
        for idx,col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d
    def getCurrentStatus(self):
        # get sensorData from DB given a device_id
        sql = "SELECT * FROM status ORDER BY timestamp DESC LIMIT 1"
        cursor = self.conn.cursor()
        cursor.execute(sql)
        return cursor.fetchone()

    def setStatus(self, status):
        try:
            cursor = self.conn.cursor()
            currentStatus = self.getCurrentStatus()
            sql = 'INSERT INTO status (timestamp, userlocation, armed) VALUES(?,?,?)';
            toAdd = []
            toAdd.append(calendar.timegm(datetime.datetime.utcnow().timetuple()))
            if(status['userlocation']is None):
                status['userlocation'] = currentStatus['userlocation']
            toAdd.append(status['userlocation'])
            if(status['armed']is None):
                status['armed'] = currentStatus['armed']
            toAdd.append(status['armed'])
            cursor.execute(sql,toAdd)
            self.conn.commit()
            return True
        except Exception as e:
            logger.error(e)
            return False

    def getButtonConfig(self):
        sql = "SELECT * FROM configButtons ORDER BY timestamp DESC LIMIT 1"
        cursor = self.conn.cursor()
        cursor.execute(sql)
        config = cursor.fetchone()
        if(config is None):
            return {'timestamp':None, '1':None, '2':None, '3':None, '4':None}
        return config

    def toCommand(self, obj):
        payload = obj
        pythonCode = ""
        if(payload['command']=='sendNotification'):
            pythonCode = """for item in actuators:
            if item['mac'] == '{}':
                {}(item,'{}')
            """.format(payload['MAC'],payload['command'], payload['message'])
        else:
            pythonCode = """for item in actuators:
            if item['mac'] == '{}':
                {}(item)
            """.format(payload['MAC'],payload['command'])
        return pythonCode;

    def updateButtons(self, buttons):
        try:
            cursor = self.conn.cursor()
            currentConfig = self.getButtonConfig()
            sql = 'INSERT INTO configButtons (`timestamp`, `1`, `2`,`3`,`4`) VALUES(?,?,?,?,?)';
            toAdd = []
            toAdd.append(calendar.timegm(datetime.datetime.utcnow().timetuple()))
            if(buttons['1']is None):
                buttons['1'] = currentConfig['1']
            toAdd.append(self.toCommand(buttons['1']))
            if(buttons['2']is None):
                buttons['2'] = currentConfig['2']
            toAdd.append(self.toCommand(buttons['2']))
            if(buttons['3']is None):
                buttons['3'] = currentConfig['3']
            toAdd.append(self.toCommand(buttons['3']))
            if(buttons['4']is None):
                buttons['4'] = currentConfig['4']
            toAdd.append(self.toCommand(buttons['4']))
            cursor.execute(sql,toAdd)
            self.conn.commit()
            return True
        except Exception as e:
            logger.error(e)
            return False
    def dumpStatus(self):
        # get sensorData from DB given a device_id
        sql = "SELECT * FROM status ORDER BY timestamp DESC"
        cursor = self.conn.cursor()
        cursor.execute(sql)
        return cursor.fetchmany()

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
                if(sensor == 'motion'):
                    val = True
                toAdd.append(val)
            except ValueError:
                return False
        sql = 'INSERT INTO sensorData (SENSORID, '+','.join(sensors)+') VALUES(?,?,?,?,?,?,?,?,?,?,?)';
        logger.info(4378)
        logger.info(toAdd)
        cursor.execute(sql,toAdd)
        self.conn.commit()
        return True

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
        sql = "SELECT 'time' FROM sensorData WHERE 'time' NOT NULL  ORDER BY time DESC LIMIT 1;"
        cursor = self.conn.cursor()
        cursor.execute(sql)
        return cursor.fetchone()
    def getSensorIDs(self):
        sql = "SELECT DISTINCT SENSORID from sensorData;"
        cursor = self.conn.cursor()
        cursor.execute(sql)
        return cursor.fetchall()
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
            its.append(item['script'])
        return its
    def close(self):
        self.conn.close()
