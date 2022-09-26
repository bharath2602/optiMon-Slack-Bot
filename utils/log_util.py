import logging

logging.basicConfig(format='%(asctime)s [%(pathname)s:%(filename)s - %(lineno)s ] %(message)s',
                    datefmt='%m/%d/%Y %I:%M:%S %p')
logger = logging.getLogger()
logger.setLevel(logging.INFO)
