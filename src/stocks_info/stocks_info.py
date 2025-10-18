from typing import Tuple, Optional
import pandas as pd

from src.overseas_stock.overseas_stock_functions import trade_vol, updown_rate, volume_power, volume_surge, news_title, \
    brknews_title, search_info
from src.utils.utils import safe_api_call


##############################################################################################
# [해외주식] 시세분석 > 해외주식 거래량순위[해외주식-043]
##############################################################################################

# nday - 0:당일, 1:2일전, 2:3일전, 3:5일전, 4:10일전, 5:20일전, 6:30일전, 7:60일전, 8:120일전, 9:1년전
# vol_rang - 0(전체), 1(1백주이상), 2(1천주이상), 3(1만주이상), 4(10만주이상), 5(100만주이상), 6(1000만주이상)
def get_trade_vol(excd: str, nday="0", vol_rang="6") -> Tuple[pd.DataFrame, pd.DataFrame]:
    trade_vol_result1, trade_vol_result2 = safe_api_call(trade_vol, excd=excd, nday=nday, vol_rang=vol_rang)
    return trade_vol_result1, trade_vol_result2


##############################################################################################
# [해외주식] 시세분석 > 해외주식 상승률/하락률[해외주식-041]
##############################################################################################

# gubn : 0(하락율), 1(상승율)
# vol_rang - 0(전체), 1(1백주이상), 2(1천주이상), 3(1만주이상), 4(10만주이상), 5(100만주이상), 6(1000만주이상)
def get_updown_rate(gubn: str, excd="NAS", nday="0", vol_rang="0") -> Tuple[pd.DataFrame, pd.DataFrame]:
    updown_rate_result1, updown_rate_result2 = safe_api_call(updown_rate, excd=excd, gubn=gubn, nday=nday,
                                                             vol_rang=vol_rang)
    return updown_rate_result1, updown_rate_result2


##############################################################################################
# [해외주식] 시세분석 > 해외주식 매수체결강도상위[해외주식-040]
##############################################################################################

# nday - 0:당일, 1:2일전, 2:3일전, 3:5일전, 4:10일전, 5:20일전, 6:30일전, 7:60일전, 8:120일전, 9:1년전
# vol_rang - 0(전체), 1(1백주이상), 2(1천주이상), 3(1만주이상), 4(10만주이상), 5(100만주이상), 6(1000만주이상)
def get_volume_power(excd="NAS", nday="0", vol_rang="0") -> Tuple[pd.DataFrame, pd.DataFrame]:
    volume_power_result1, volume_power_result2 = safe_api_call(volume_power, excd=excd, nday=nday, vol_rang=vol_rang)
    return volume_power_result1, volume_power_result2


##############################################################################################
# [해외주식] 시세분석 > 해외주식 거래량급증[해외주식-039]
##############################################################################################

# mixn - N분전 : 0(1분전), 1(2분전), 2(3분전), 3(5분전), 4(10분전), 5(15분전), 6(20분전), 7(30분전), 8(60분전), 9(120분전)
# vol_rang - 0(전체), 1(1백주이상), 2(1천주이상), 3(1만주이상), 4(10만주이상), 5(100만주이상), 6(1000만주이상)
def get_volume_surge(excd="NAS", mixn="4", vol_rang="0") -> Tuple[pd.DataFrame, pd.DataFrame]:
    volume_surge_result1, volume_surge_result2 = safe_api_call(volume_surge, excd=excd, mixn=mixn, vol_rang=vol_rang)
    return volume_surge_result1, volume_surge_result2


##############################################################################################
# [해외주식] 시세분석 > 해외뉴스종합(제목) [해외주식-053]
##############################################################################################

def get_overseas_news(nation_cd="US") -> pd.DataFrame:
    nt_params = {
        "info_gb": "",
        "class_cd": "",
        "nation_cd": nation_cd,
        "exchange_cd": "",
        "symb": "",
        "data_dt": "",
        "data_tm": "",
        "cts": ""
    }
    news_title_result = safe_api_call(news_title, **nt_params)
    return news_title_result


##############################################################################################
# [해외주식] 시세분석 > 해외속보(제목) [해외주식-055]
##############################################################################################

def get_overseas_brknews() -> pd.DataFrame:
    brknews_title_result = safe_api_call(brknews_title, fid_news_ofer_entp_code="0", fid_cond_scr_div_code="11801")
    return brknews_title_result


##############################################################################################
# [해외주식] 시세분석 > 해외주식 상품기본정보[v1_해외주식-034]
##############################################################################################

# prdt_type_cd (str): 512  미국 나스닥 / 513  미국 뉴욕 / 529  미국 아멕스  515  일본
# 501  홍콩 / 543  홍콩CNY / 558  홍콩USD 507  베트남 하노이 / 508  베트남 호치민 551  중국 상해A / 552  중국 심천A
def get_overseas_base_info(pdno: str, prdt_type_cd="512") -> Optional[pd.DataFrame]:
    search_info_result = safe_api_call(search_info, prdt_type_cd=prdt_type_cd, pdno=pdno)
    return search_info_result
