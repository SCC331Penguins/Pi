import logging
from pi import *

# Setup logging config
LOG_FORMAT = "%(asctime)s (%(levelname)s) - %(message)s @ [%(pathname)s(%(lineno)d)]"
logging.basicConfig(filename='pi.log',
                    level = logging.DEBUG,
                    format = LOG_FORMAT,
                    filemode = 'w')
logging.getLogger().addHandler(logging.StreamHandler())

p = Pi([])
p.start()
p.run()
