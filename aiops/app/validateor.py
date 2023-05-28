from wtforms.validators import StopValidation
from datetime import datetime
import requests
import logging

logger = logging.getLogger(__name__)


class StartTimeValidator(object):
    def __call__(self, form, field):
        if not (datetime.now() < field.data < form['end_time'].data):
            raise StopValidation(f'时间必须是大于当前，小于结束时间')


class OrderIDValidtor(object):

    def __call__(self, form, field):
        try:
            response = requests.get(url=f'http://127.0.0.1:4523/m1/2415682-0-default/order/{field.data}').json()
            print(response)
            if response['retCode'] != '0000':
                raise StopValidation('order校验失败')
        except Exception as ex:
            logger.exception(ex)
            raise StopValidation('校验失败')
