import sys, os, sqlite3
sensors = ['light', 'sound', 'UV', 'IR', 'temp', 'humid', 'tiltX', 'tiltY', 'tiltZ']
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
        self.cursor =self.conn.cursor()
        if(new):
            self.cursor.execute('''CREATE TABLE sensorData (
                `id` INT AUTO_INCREMENT PRIMARY KEY,`SENSORID`,'''+','.join(sensors) + ')')
            self.conn.commit()
        pass
    def addSensorData(self, device_id,data):
        toAdd = []
        toAdd.append(device_id)
        for sensor in sensors:
            try:
                val = data.get(sensor,'NULL')
                if(val != 'NULL'):
                    val = float(val)
                toAdd.append(val)
            except ValueError:
                return False
        sql = 'INSERT INTO sensorData (SENSORID, '+','.join(sensors)+') VALUES(?,?,?,?,?,?,?,?,?,?)';
        self.cursor.execute(sql,toAdd)
        self.conn.commit()
        return True
        pass
    def getSensorDataFromID(self, device_id, Limit=None):
        if Limit<=0 and Limit != None:
            raise ValueError('Limit Invalid')
        params = []
        sql = "SELECT * FROM sensorData WHERE SENSORID=?"
        params.append(device_id)
        if(Limit!=None):
            sql = sql + " LIMIT ?"
            params.append(Limit)
        self.cursor.execute(sql,params)
        return self.cursor.fetchall()
        pass
    def close(self):
        self.conn.close()
