from typing import Optional
import pandas as pd

from src.overseas_stock.overseas_stock_functions import order
from src.utils.utils import safe_api_call


def buy_overseas_stock(trenv: tuple, pdno: str, ord_qty: int, ovrs_excg_cd="NASD") -> Optional[pd.DataFrame]:
    """
    시장가 매수
    해외거래소 기본 값은 NASDAQ(NASD)
    """
    if not trenv:
        raise ValueError("No trenv data.")

    if not pdno:
        raise ValueError("No pdno(Ticker).")

    if not ord_qty:
        raise ValueError("No ord_qty(Quantity).")

    bo_params = {
        "cano": trenv.my_acct,
        "acnt_prdt_cd": trenv.my_prod,
        "ovrs_excg_cd": ovrs_excg_cd,  # 해외거래소코드
        "pdno": pdno,  # 종목코드
        "ord_qty": ord_qty,
        "ovrs_ord_unpr": "0",  # 1주당 가격 (* 시장가의 경우 1주당 가격을 공란으로 비우지 않음 "0"으로 입력)
        "ord_dv": "buy",
        "ctac_tlno": "",
        "mgco_aptm_odno": "",
        "ord_svr_dvsn_cd": "0",
        "ord_dvsn": "01",  # 00:지정가, 01:시장가
        "env_dv": "real"
    }
    buy_order_result = safe_api_call(order, **bo_params)
    # print(buy_order_result)

    return buy_order_result


def sell_overseas_stock(trenv: tuple, pdno: str, ord_qty: int, ovrs_excg_cd="NASD") -> Optional[pd.DataFrame]:
    """
    시장가 매도
    해외거래소 기본 값은 NASDAQ(NASD)
    """
    if not trenv:
        raise ValueError("No trenv data.")

    if not pdno:
        raise ValueError("No pdno(Ticker).")

    if not ord_qty:
        raise ValueError("No ord_qty(Quantity).")

    bo_params = {
        "cano": trenv.my_acct,
        "acnt_prdt_cd": trenv.my_prod,
        "ovrs_excg_cd": ovrs_excg_cd,  # 해외거래소코드
        "pdno": pdno,  # 종목코드
        "ord_qty": ord_qty,
        "ovrs_ord_unpr": "0",  # 1주당 가격 (* 시장가의 경우 1주당 가격을 공란으로 비우지 않음 "0"으로 입력)
        "ord_dv": "sell",
        "ctac_tlno": "",
        "mgco_aptm_odno": "",
        "ord_svr_dvsn_cd": "0",
        "ord_dvsn": "01",  # 00:지정가, 01:시장가
        "env_dv": "real"
    }
    sell_order_result = safe_api_call(order, **bo_params)
    # print(sell_order_result)

    return sell_order_result
