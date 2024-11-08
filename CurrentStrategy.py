import pandas as pd
import os
import numpy as np
# from pytz import timezone
import datetime
import time
import logging
import sys
current_script_path = os.path.realpath(__file__)
current_script_directory = os.path.dirname(current_script_path)
sys.path.append(current_script_directory)
import TradeConfig as cfg


def maemae_status_by_kullamagi_gradient(stock_name):

    data_file = f"{cfg.DATA_FILES_PATH}/{stock_name}.xlsx"

    df = pd.read_excel(data_file)
    df = df.dropna()
    new_df = df[df['Volume'] !=0]

    date = new_df['Date']
    close = new_df['Close']
    ema10_gradient = new_df['EMA10_GRADIENT']
    ema20_gradient = new_df['EMA20_GRADIENT']
    ema50_gradient = new_df['EMA50_GRADIENT']

    date = date.tolist()
    close = close.tolist()
    ema10_gradient = ema10_gradient.tolist()
    ema20_gradient = ema20_gradient.tolist()
    ema50_gradient = ema50_gradient.tolist()

    data_num = len(close)
    maemae_status = []
    for i in range(data_num) :
        all_upward = (ema10_gradient[i] > 0) and (ema20_gradient[i] > 0) and (ema50_gradient[i] > 0)
        twenty_fifty_upward = (ema20_gradient[i] > 0) and (ema50_gradient[i] > 0)
        ten_twenty_downward = (ema10_gradient[i] <= 0) and (ema20_gradient[i] <= 0)
        all_downward = (ema10_gradient[i] < 0) and (ema20_gradient[i] < 0) and (ema50_gradient[i] < 0)
        if i == 0 :
            maemae_status.append(0)
        elif all_upward :
            maemae_status.append(1)
        elif all_downward :
            maemae_status.append(0)
        elif maemae_status[-1] == 1 and twenty_fifty_upward:
            maemae_status.append(1)
        elif maemae_status[-1] == 1 and ten_twenty_downward:
            maemae_status.append(0)
        elif maemae_status[-1] == 0 :
            maemae_status.append(0)
        else :
            maemae_status.append(0)

    return maemae_status


def maemae_status_by_sma20_angle(stock_name):

    data_file = f"{cfg.DATA_FILES_PATH}/{stock_name}.xlsx"

    df = pd.read_excel(data_file)
    df = df.dropna()
    new_df = df[df['Volume'] !=0]

    angles = new_df['SMA20_ANGLES']
    angles = angles.tolist()
    yesterday_ang = angles[-1]

    if yesterday_ang < 0 and angles[-2] > 0 :
        today_maemae_status = 0
    elif yesterday_ang < 0 and angles[-2] <= 0 :
        today_maemae_status = 0
    elif yesterday_ang == 0 and angles[-2] <= 0 :
        today_maemae_status = 0
    elif yesterday_ang > 0 and angles[-2] < 0 :
        today_maemae_status = 1
    elif yesterday_ang > 0 and angles[-2] >= 0 :
        today_maemae_status = 1
    elif yesterday_ang == 0 and angles[-2] >= 0 :
        today_maemae_status = 1

    return today_maemae_status


def yesterday_close_is_higher_than_sma60(stock_name):

    data_file = f"{cfg.DATA_FILES_PATH}/{stock_name}.xlsx"

    df = pd.read_excel(data_file)
    new_df = df[df['Volume'] !=0]
    close = new_df['Close']
    sma60 = new_df['SMA60']
    yesterday_close = close.tolist()[-1]
    yesterday_sma60 = sma60.tolist()[-1]

    is_higher = yesterday_close > yesterday_sma60

    return is_higher

