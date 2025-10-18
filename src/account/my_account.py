from typing import Tuple, Optional
import pandas as pd

from src.overseas_stock.overseas_stock_functions import inquire_balance, inquire_psamount
from src.utils.utils import safe_api_call


##############################################################################################
# [해외주식] 주문/계좌 > 해외주식 잔고 [v1_해외주식-006]
##############################################################################################

def get_account_balance(trenv: tuple) -> Tuple[pd.DataFrame, pd.DataFrame]:
    ib_params = {
        "cano": trenv.my_acct,
        "acnt_prdt_cd": trenv.my_prod,
        "ovrs_excg_cd": "NASD",
        "tr_crcy_cd": "USD"
    }
    inquire_balance_result = safe_api_call(inquire_balance, **ib_params)
    # print(inquire_balance_result)

    return inquire_balance_result


##############################################################################################
# [해외주식] 주문/계좌 > 해외주식 매수가능금액조회 [v1_해외주식-014]
##############################################################################################

def get_buy_amount(trenv: tuple, item_cd: str, ovrs_ord_unpr: str, ovrs_excg_cd="NASD") -> Optional[pd.DataFrame]:
    ip_params = {
        "cano": trenv.my_acct,
        "acnt_prdt_cd": trenv.my_prod,
        "ovrs_excg_cd": ovrs_excg_cd,
        "ovrs_ord_unpr": ovrs_ord_unpr,  # 해외주문단가
        "item_cd": item_cd  # 종목코드
    }
    inquire_psamount_result = safe_api_call(inquire_psamount, **ip_params)
    # print(inquire_psamount_result)

    return inquire_psamount_result
