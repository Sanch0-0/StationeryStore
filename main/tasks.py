from celery import shared_task
import logging

logger = logging.getLogger('Stationery_Store')

@shared_task
def log_task(message, level='info'):
    """Async logging"""
    level = level.lower()
    if level == 'debug':
        logger.debug(message)
    elif level == 'info':
        logger.info(message)
    elif level == 'warning':
        logger.warning(message)
    elif level == 'error':
        logger.error(message)
    elif level == 'critical':
        logger.critical(message)
    else:
        logger.info(message)  
