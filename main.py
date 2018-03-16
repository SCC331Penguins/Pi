import logging
from pi import *
from pi.mqtt_logger import *
# Setup logging config
LOG_FORMAT = "%(asctime)s (%(levelname)s) - %(message)s @ [%(pathname)s(%(lineno)d)]"
logging.basicConfig(filename='pi.log',
                    level = logging.DEBUG,
                    format = LOG_FORMAT,
                    filemode = 'w')
logger = logging.getLogger()
logger.addHandler(logging.StreamHandler())
logger.addHandler(MQTTLogger())
p = Pi([])
p.start()
p.run()
# raw_input()
