import datetime
import time
import logging
import schedule
import subprocess
# Pass an pytz timezone object
# from pytz import timezone
from data_algos import TradeConfig as cfg

t_now = datetime.datetime.now()
y_m_d = str(t_now.strftime('%Y-%m-%d'))
LOG_FILE = f'{cfg.LOG_PATH}/ControllerLog_{y_m_d}.log'

logger = logging.getLogger()
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s| %(message)s')
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)
file_handler = logging.FileHandler(LOG_FILE)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

logger.info('= = Starting Trading Controller')


def execute_kor_trade():
    logger.info("= = 한국 데이터 업데이트 시작")
    GetYfDataPy = f'{cfg.DATA_ALGOS_PATH}/GetYfData.py'
    InsertMovingAvgDataPy = f'{cfg.DATA_ALGOS_PATH}/InsertMovingAvgData.py'
    subprocess.run(["python3", GetYfDataPy])
    subprocess.run(["python3", InsertMovingAvgDataPy])

    logger.info("= = 한국 거래 시작")
    KorAPIPy = f'{cfg.ROOT_PATH}/KorAPI.py'
    KorStockAutoTradePy = f'{cfg.ROOT_PATH}/KorStockAutoTrade.py'
    subprocess.run(["python3", KorAPIPy])
    subprocess.run(["python3", KorStockAutoTradePy])


KOR_TRADE_START_TIME = "15:20"
schedule.every().monday.at(KOR_TRADE_START_TIME).do(execute_kor_trade)
schedule.every().tuesday.at(KOR_TRADE_START_TIME).do(execute_kor_trade)
schedule.every().wednesday.at(KOR_TRADE_START_TIME).do(execute_kor_trade)
schedule.every().thursday.at(KOR_TRADE_START_TIME).do(execute_kor_trade)
schedule.every().friday.at(KOR_TRADE_START_TIME).do(execute_kor_trade)


try:
    while True:
        schedule.run_pending()
        time.sleep(1)

except Exception as e:
    logger.info(f'= = 에러 발생 e:{e}')
    time.sleep(1)