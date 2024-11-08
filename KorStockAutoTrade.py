import json
import datetime
import time
import logging
from data_algos import TradeConfig as cfg
from data_algos import CurrentStrategy as cs
import KorAPI

SYMBOL_LIST = []
BUY_PERCENT = []
SYMBOL_LIST_NAME = []
TARGET_BUY_COUNT = cfg.TARGET_BUY_COUNT
for num in range(len(cfg.STOCKS)):
    SYMBOL_LIST.append((cfg.STOCKS[num][0]).split('.KS')[0])
    BUY_PERCENT.append(cfg.STOCKS[num][1])
    SYMBOL_LIST_NAME.append(cfg.STOCKS[num][2])

t_now = datetime.datetime.now()
y_m_d = str(t_now.strftime('%Y-%m-%d'))
LOG_FILE = f'{cfg.LOG_PATH}/KorAutoTrdLog_{y_m_d}.log'

logger = logging.getLogger()
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s| %(message)s')
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)
file_handler = logging.FileHandler(LOG_FILE)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


def send_and_log_msg(msg):
    KorAPI.send_message(msg=msg)
    # logger.info(msg=msg)

def confirm_stock_held(stock_dict_with_name):
    stock_dict_with_name_vals = list(stock_dict_with_name.values())
    for i in range(len(stock_dict_with_name)):
        msg_str = f'{stock_dict_with_name_vals[i][0]} : {stock_dict_with_name_vals[i][1]}주'
        send_and_log_msg(f"{i+1}/{len(stock_dict_with_name)} : {msg_str}")

def get_stock_dict_with_name(stock_dict):
    stock_dict_with_name = {}
    stock_dict_keys = list(stock_dict.keys())
    stock_dict_values = list(stock_dict.values())
    symbol_dict = {}
    for i, sym in enumerate(SYMBOL_LIST):
        symbol_dict[sym] = SYMBOL_LIST_NAME[i]
    data_num = len(stock_dict_keys)
    for i in range(data_num):
        stock_dict_with_name[stock_dict_keys[i]] = [symbol_dict[stock_dict_keys[i]], stock_dict_values[i]]
    return stock_dict_with_name

def main():
    # 자동매매 시작
    try:
        send_and_log_msg('')
        send_and_log_msg('===한국주식 투자자동화 프로그램 시작===')


        # [1] 한투 API 토큰
        json_file_dir = f'{cfg.ROOT_PATH}/access_token_data.json'
        with open(json_file_dir, 'r') as json_file:
            access_token_data = json.load(json_file)

        # ACCESS_TOKEN = KorAPI.get_access_token()
        ACCESS_TOKEN = access_token_data["ACCESS_TOKEN"]


        # [2] 종목 정보 변수 세팅
        symbol_list = SYMBOL_LIST
        buy_percent = BUY_PERCENT
        total_cash = KorAPI.get_balance(ACCESS_TOKEN) # 보유 현금 조회
        stock_dict, total_amount = KorAPI.get_stock_balance(ACCESS_TOKEN)
        send_and_log_msg(f'총 평가금액 (보유주식 포함): {total_amount}원')
        send_and_log_msg(f'보유 현금 잔고: {total_cash}원')
        stock_dict_with_name = get_stock_dict_with_name(stock_dict)
        # {'000660': ['SK하이닉스', '1'], '005930': ['삼성전자', '2']}
        stock_dict_with_name_keys = list(stock_dict_with_name.keys())
        # ['000660','005930']
        logger.info('')
        send_and_log_msg(f"===보유주식 현황===")
        confirm_stock_held(stock_dict_with_name)
        logger.info('\n')


        # [3] 종목별 매매
        for i, sym in enumerate(symbol_list):
            send_and_log_msg(f"==={i+1}/{len(symbol_list)} {SYMBOL_LIST_NAME[i]} {sym} 시작===")

            # 1. 이미 보유 중인 주식인지 확인
            is_already_bought = False
            if sym in stock_dict_with_name_keys :
                is_already_bought = True
            send_and_log_msg(f'is_already_bought:{is_already_bought}')

            # 2. 알고리즘 maemae_status 결과
            maemae_status = cs.maemae_status_by_kullamagi_gradient(SYMBOL_LIST_NAME[i])
            today_mms = maemae_status[-1]
            yesterday_mms = maemae_status[-2]
            two_days_ago_mms = maemae_status[-3]
            send_and_log_msg(f'today_mms:{today_mms}')
            send_and_log_msg(f'yesterday_mms:{yesterday_mms}')

            # 3. 매수할지 매도할지 판단
            buy_condition = False
            sell_condition = False
            # 3-(1) 현재 매도 상태이고 어제(또는 이틀전) 0 -> 오늘 1 상태이면 매수
            if (is_already_bought==False) and (two_days_ago_mms==0 or yesterday_mms==0) and (today_mms==1) :
                buy_condition = True
            # 3-(2) 현재 매수 상태인데 today_mms==0 이면 매도
            elif is_already_bought and (today_mms==0) :
                sell_condition = True

            if is_already_bought :
                send_and_log_msg(f'sell_condition:{sell_condition}')
            else :
                send_and_log_msg(f'buy_condition:{buy_condition}')

            # 4. 실제 매수/매도
            if buy_condition :
                send_and_log_msg(f"매수(buy)를 시도합니다")
                buy_qty = 0
                current_price = KorAPI.get_current_price(sym, ACCESS_TOKEN)
                buy_qty = int(total_amount * buy_percent[i] // current_price)
                if buy_qty < 1 : buy_qty = 1
                send_and_log_msg(f'total_amount:{total_amount}')
                send_and_log_msg(f'buy_percent[i]:{buy_percent[i]}')
                send_and_log_msg(f'current_price:{current_price}')
                send_and_log_msg(f'buy_qty:{buy_qty}')
                send_and_log_msg(f'buy_qty = int(total_amount * buy_percent[i] // current_price)')

                result, res_detail = KorAPI.buy(sym, buy_qty, ACCESS_TOKEN)
                send_and_log_msg(f"매수(buy)시도결과 : {result}, {res_detail}")

            # 4. 실제 매수/매도
            if sell_condition :
                send_and_log_msg("매도(sell)를 시도합니다")
                last_bought_qty = stock_dict_with_name[sym][1]
                send_and_log_msg(f'stock_dict_with_name:{stock_dict_with_name}')
                send_and_log_msg(f'stock_dict_with_name[sym]:{stock_dict_with_name[sym]}')
                send_and_log_msg(f'last_bought_qty:{last_bought_qty}')

                result, res_detail = KorAPI.sell(sym, last_bought_qty, ACCESS_TOKEN)
                send_and_log_msg(f"매도(sell)시도결과 : {result}, {res_detail}")

            send_and_log_msg(f"==={i+1}/{len(symbol_list)} {SYMBOL_LIST_NAME[i]} {sym} 종료===")
            logger.info('\n')

        _, total_amount = KorAPI.get_stock_balance(ACCESS_TOKEN)
        total_cash = KorAPI.get_balance(ACCESS_TOKEN) # 보유 현금 조회
        send_and_log_msg('===한국주식 투자자동화 프로그램 종료합니다===')
        send_and_log_msg(f'보유 현금 잔고: {total_cash}원')
        send_and_log_msg(f'총 평가금액 (보유주식 포함): {total_amount}원')
        logger.info('\n')


    except Exception as e:
        send_and_log_msg(f"1 [오류 발생]{str(e)}■■■")
        send_and_log_msg("2 예외가 발생했습니다:", repr(e))
        import traceback
        traceback.print_exc()
        import sys
        exc_type, exc_value, exc_traceback = sys.exc_info()
        send_and_log_msg(f"3 에러 유형: {exc_type}")
        send_and_log_msg(f"4 에러 메시지: {exc_value}")        
        send_and_log_msg(f"5 에러 메시지: {exc_traceback}")        

if __name__ == '__main__':
	main()

