import logging
from pyeeg.io.getdir import set_logdir

logger = logging.getLogger(__name__)
logger.propagate = False
handler = logging.FileHandler(set_logdir('test.log'))
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel('DEBUG')