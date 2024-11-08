import yfinance as yf
import datetime
import logging
import TradeConfig as cfg


t_now = datetime.datetime.now()
y_m_d = str(t_now.strftime('%Y-%m-%d'))
LOG_FILE = f'{cfg.LOG_PATH}/GetYfDataLog.log'

logger = logging.getLogger()
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s| %(message)s')
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)
file_handler = logging.FileHandler(LOG_FILE)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


stock_data = cfg.STOCKS

for i, data in enumerate(stock_data):
    code = stock_data[i][0]
    date_start = cfg.DATA_START_DATE
    file_name = stock_data[i][2]
    df = yf.download(code, date_start) # date_end 값도 추가 가능함. 없으면 오늘까지임.
    download_file = f"{cfg.DATA_FILES_PATH}/{file_name}.xlsx"
    df.to_excel(download_file)
    logger.info(f'{i+1}/{len(stock_data)} - {download_file}')

