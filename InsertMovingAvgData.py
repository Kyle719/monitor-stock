import pandas as pd
import numpy as np
# from pytz import timezone
import datetime
import time
import logging
import TradeConfig as cfg

t_now = datetime.datetime.now()
y_m_d = str(t_now.strftime('%Y-%m-%d'))
LOG_FILE = f'{cfg.LOG_PATH}/MovingAvgLog_{y_m_d}.log'

logger = logging.getLogger()
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s| %(message)s')
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)
file_handler = logging.FileHandler(LOG_FILE)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


def get_gradient(ma):
    ma_gradient = np.gradient(ma)
    return ma_gradient

def get_angels(ma):
    ma_gradient = np.gradient(ma)
    ma_angles = []
    for grd in ma_gradient.tolist() :
        ma_angles.append(np.degrees(np.arctan(grd)))
    ma_angles = pd.Series(ma_angles)
    return ma_angles

def simple_moving_average(code, file_name):
    code = code.split('.KS')[0]
    file_path = f"{cfg.DATA_FILES_PATH}/{file_name}.xlsx"
    df = pd.read_excel(file_path)
    new_df = df[df['Volume'] !=0]

    sma20 = new_df['Close'].rolling(window=20).mean()
    sma20_gradient = np.gradient(sma20)
    sma20_angles = []
    for grd in sma20_gradient.tolist() :
        sma20_angles.append(np.degrees(np.arctan(grd)))
    sma20_angles = pd.Series(sma20_angles)
    new_df.insert(len(new_df.columns), "SMA20", sma20)
    new_df.insert(len(new_df.columns), "SMA20_ANGLES", sma20_angles)

    # sma5 = new_df['Close'].rolling(window=5).mean()
    # sma20 = new_df['Close'].rolling(window=20).mean()
    # sma60 = new_df['Close'].rolling(window=60).mean()
    # sma120 = new_df['Close'].rolling(window=120).mean()
    # new_df.insert(len(new_df.columns), "SMA5", sma5)
    # new_df.insert(len(new_df.columns), "SMA20", sma20)
    # new_df.insert(len(new_df.columns), "SMA60", sma60)
    # new_df.insert(len(new_df.columns), "SMA120", sma120)

    with pd.ExcelWriter(file_path) as w:
        new_df.to_excel(w, index=False)

    logger.info(f'= = {file_name} {y_m_d} 일자 SMA 데이터 업데이트 완료')

def exponential_moving_average(code, file_name):
    code = code.split('.KS')[0]
    file_path = f"{cfg.DATA_FILES_PATH}/{file_name}.xlsx"
    df = pd.read_excel(file_path)
    new_df = df[df['Volume'] !=0]

    ema10 = new_df['Close'].ewm(10).mean()
    ema20 = new_df['Close'].ewm(20).mean()
    ema50 = new_df['Close'].ewm(50).mean()
    ema10_gradient = get_gradient(ema10)
    ema20_gradient = get_gradient(ema20)
    ema50_gradient = get_gradient(ema50)

    new_df.insert(len(new_df.columns), "EMA10", ema10)
    new_df.insert(len(new_df.columns), "EMA10_GRADIENT", ema10_gradient)
    new_df.insert(len(new_df.columns), "EMA20", ema20)
    new_df.insert(len(new_df.columns), "EMA20_GRADIENT", ema20_gradient)
    new_df.insert(len(new_df.columns), "EMA50", ema50)
    new_df.insert(len(new_df.columns), "EMA50_GRADIENT", ema50_gradient)

    with pd.ExcelWriter(file_path) as w:
        new_df.to_excel(w, index=False)

    logger.info(f'= = {file_name} {y_m_d} 일자 EMA 데이터 업데이트 완료')


def main():
    stock_data = cfg.STOCKS
    for i, data in enumerate(stock_data):
        logger.info(f'= = {i+1}/{len(stock_data)} data 업데이트 시작 : {stock_data[i]}')
        # simple_moving_average(
        #     code = stock_data[i][0],
        #     file_name = stock_data[i][2]
        # )
        exponential_moving_average(
            code = stock_data[i][0],
            file_name = stock_data[i][2]
        )

if __name__ == '__main__':
    try:
        main()

    except Exception as e:
        logger.info(f'= = 에러 발생 e:{e}')
        time.sleep(1)
