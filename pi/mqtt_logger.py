import logging, time, json, calendar
import paho.mqtt.client as mqtt
logger = logging.getLogger()
class MQTTLogger(logging.StreamHandler):
    on_same_line = False
    level = logging.WARNING
    def __init__(self):
        logging.StreamHandler.__init__(self)
        self.client = mqtt.Client()
        self._config = json.load(
            open('id.json')
        )
        self.client.connect("localhost",1883,60)
        logger.error('ggg')
        # token shouldn't be hardcoded


        # time.sleep(30)
        # client.disconnect()
    def doMessage(self,pl):
        msg = {
            'type':'LOGDATA',
            'token':'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IlNDQzMzMTAyX1IwMSJ9.XopN05KKB6am2sbuEl9kXPji-Z11bgxK8MdzAac1XPw',
            'payload':pl
        }
        self.client.publish(self._config['RouterID'], str(json.dumps(msg)))
    def emit(self, record):
        if(record.levelno<30):
            return
        try:
            rec = {
                "level":str(record.levelno),
                "message":"%(message)s @ [%(pathname)s(%(lineno)d)]" % {"message": record.message, "pathname": record.pathname, "lineno": record.lineno},
                "time": str(calendar.timegm(time.strptime(record.asctime,"%Y-%m-%d %H:%M:%S,%f"))),
                "R_id": self._config['RouterID'],
            }
            self.doMessage(rec)
            self.flush()
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)
