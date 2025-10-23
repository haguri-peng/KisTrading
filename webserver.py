from flask import Flask, request, jsonify
import logging, os, time, math
from logging.handlers import TimedRotatingFileHandler
import pandas as pd
from typing import Optional
from collections import defaultdict  # 캐시를 위한 defaultdict 추가

# Utils
from src.utils.utils import safe_api_call
from src.utils.email_utils import send_email

# KIS
import src.utils.kis_auth as ka
from src.overseas_stock.overseas_stock_functions import price_detail
from src.account.my_account import get_account_balance, get_buy_amount
from src.order.order import buy_overseas_stock, sell_overseas_stock

# Flask
app = Flask(__name__)

# logs 폴더 생성 (없으면 자동 생성)
os.makedirs('logs', exist_ok=True)

# TimedRotatingFileHandler 설정: 일자별 로테이션
handler = TimedRotatingFileHandler(
    filename='logs/app.log',  # 기본 파일명 (로테이션 시 변경됨)
    when='midnight',  # 자정에 로테이션
    interval=1,  # 1일 간격
    backupCount=30,  # 최대 30일치 백업 파일 유지 (필요 시 조정)
    encoding='utf-8'  # UTF-8 인코딩
)
handler.suffix = '%Y-%m-%d.log'  # 로테이션 파일명: app.log.YYYY-MM-DD
handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))  # 로그 형식

# 로거 설정
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(handler)

# TradingView에서 설정한 시크릿 키
SECRET_KEY = 'tradingview_haguri_peng_secret_key'

# 중복 검사 캐시: 키 = "ticker_value", 값 = 마지막 처리 timestamp
webhook_cache = defaultdict(float)  # 기본값 0.0 (float)

# 중복 검사 시간 창: 30초
DUPLICATE_WINDOW = 30


# Webhook
@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.get_json()
        if not data:
            raise ValueError("No JSON data.")

        logger.info(f"Received: {data}")

        ticker: str = data.get('ticker')
        value: str = data.get('value')
        if not all([ticker, value]):
            raise ValueError("Missing fields.")

        # 중복 검사 키 생성
        cache_key = f"{ticker}_{value}"

        current_time = time.time()
        last_processed = webhook_cache[cache_key]

        if last_processed > 0 and (current_time - last_processed) < DUPLICATE_WINDOW:
            logger.info(f"Duplicate signal ignored: {data}")
            return jsonify({"status": "duplicate_ignored"}), 200

        # 중복 아니면 바로 캐시 업데이트 (처리 시작 마킹)
        webhook_cache[cache_key] = current_time

        # 매매 로직 호출
        process_trade(ticker, value)

        return jsonify({"status": "success"}), 200

    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return jsonify({"error": str(e)}), 500


def process_trade(ticker: str, value: str):
    """ 매매(buy & sell) """
    logger.info(f"Process trading : {value} {ticker}")

    # 인증
    ka.auth()
    trenv = ka.getTREnv()

    ##############################################################################################
    # [해외주식] 기본시세 > 해외주식 현재가상세[v1_해외주식-029]
    ##############################################################################################
    price_detail_result: Optional[pd.DataFrame] = safe_api_call(price_detail, auth="", excd="NAS", symb=f"{ticker}")
    logger.info(price_detail_result)

    ticker_last = 0
    if price_detail_result is not None:
        if 'last' in price_detail_result.columns:
            ticker_last = price_detail_result['last'].iloc[0]

    logger.info(f"ticker_last : {ticker_last}")

    if value.lower() == 'buy':
        logger.info("++++++++++ buy ++++++++++")

        if float(ticker_last) > 0:
            # 매수가능금액 확인
            ticker_psamount = get_buy_amount(trenv, ticker, ticker_last)
            logger.info(ticker_psamount)

            if ticker_psamount is not None and not ticker_psamount.empty:
                max_psbl_qty = ticker_psamount.iloc[0]['ovrs_max_ord_psbl_qty']  # 해외최대주문가능수량

                logger.info(f"max_psbl_qty : {max_psbl_qty}")

                if max_psbl_qty is not None and int(max_psbl_qty) >= 10:
                    # 소수점 둘째 자리까지 floor 처리한 이후 .1을 더한 값으로 매수 지정가 설정
                    buy_ord_unpr = math.floor(float(ticker_last) * 100) / 100 + 0.1
                    logger.info(f"buy_ord_unpr : {buy_ord_unpr}")

                    # buy_result = buy_overseas_stock(trenv, ticker, max_psbl_qty)
                    buy_result = buy_overseas_stock(trenv, ticker, buy_ord_unpr, 10)  # 10주씩 매수

                    logger.info(buy_result)

                    if buy_result is not None:
                        # 주문번호(ODNO) 확인. 주문번호가 있으면 정상
                        if buy_result.iloc[0]['ODNO'] is not None:
                            buy_msg = f"{ticker}, 10주를 정상적으로 매수하였습니다. 주문번호: {buy_result.iloc[0]['ODNO']}"

                            logger.info(buy_msg)
                            send_email(f"{ticker} 시장가 매수", buy_msg)
                    else:
                        logger.error("매수 중 오류가 발생하였습니다.")
                        send_email(f"{ticker} 매수 중 오류", "매수 중 오류가 발생하였습니다.")
                else:
                    # 주문가능수량이 최소 10주 이상이 되어야 한다.
                    logger.info("매수가능금액이 부족합니다.")

            else:
                logger.info("매수가능금액 데이터가 없음. 매수 스킵!")

    elif value.lower() == 'sell':
        logger.info("++++++++++ sell ++++++++++")

        # 계좌정보 확인
        my_account_balance = get_account_balance(trenv)

        if isinstance(my_account_balance, tuple) and len(my_account_balance) == 2 and my_account_balance[0] is not None:
            output1_df = my_account_balance[0]

            if 'ovrs_pdno' in output1_df.columns:  # 열 존재 확인 (잔고에 아무 것도 없으면, 빈 값을 주기 때문에 체크)
                filtered_df = output1_df[output1_df['ovrs_pdno'] == ticker]  # ticker 정보 확인

                if not filtered_df.empty:
                    first_row = filtered_df.iloc[0]
                    psbl_qty = first_row['ord_psbl_qty']  # 주문가능수량 (매도 가능한 주문 수량)

                    logger.info(first_row)
                    logger.info(f"psbl_qty : {psbl_qty}")

                    # 매도할 수량이 있어야 진행
                    if psbl_qty is not None and int(psbl_qty) > 0 and float(ticker_last) > 0:
                        # 10주씩 매도. 단, 10주 미만인 경우 모두 매도한다.
                        psbl_qty = "10" if int(psbl_qty) >= 10 else psbl_qty
                        logger.info(f"psbl_qty2 : {psbl_qty}")

                        # 소수점 둘째 자리까지 floor 처리한 이후 .1을 제한 값으로 매도 지정가 설정
                        sell_ord_unpr = math.floor(float(ticker_last) * 100) / 100 - 0.1
                        logger.info(f"sell_ord_unpr : {sell_ord_unpr}")

                        sell_result = sell_overseas_stock(trenv, ticker, sell_ord_unpr, psbl_qty)

                        logger.info(sell_result)

                        if sell_result is not None:
                            # 주문번호(ODNO) 확인. 주문번호가 있으면 정상
                            if sell_result.iloc[0]['ODNO'] is not None:
                                sell_msg = f"{ticker}, {psbl_qty}주를 정상적으로 매도하였습니다. 주문번호: {sell_result.iloc[0]['ODNO']}"

                                logger.info(sell_msg)
                                send_email(f"{ticker} 시장가 매도", sell_msg)
                        else:
                            logger.error("매도 중 오류가 발생하였습니다.")
                            send_email(f"{ticker} 매도 중 오류", "매도 중 오류가 발생하였습니다.")

                else:
                    logger.info(f"{ticker} 매도할 수량이 없습니다.")

            else:
                logger.info("잔고가 비어 있습니다.")

    else:
        raise ValueError(f"Invalid value({value})")


if __name__ == '__main__':
    logger.info("TradeHook Web Server starts..")

    # ssl_context 부분은 인증서가 있는 경우에만 입력
    app.run(host='0.0.0.0', port=5556, debug=False, ssl_context=('crt.pem', 'key.pem'))
