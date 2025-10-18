import requests
import logging

logger = logging.getLogger(__name__)

import src.utils.kis_auth as ka


def safe_api_call(func, *args, **kwargs):
    """토큰 만료 시 자동 갱신 후 재시도"""
    try:
        return func(*args, **kwargs)
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:  # 토큰 만료 에러
            logger.info("Token expired. Renewing...")
            ka.auth()
            return func(*args, **kwargs)  # 재시도
        else:
            raise e  # 다른 에러는 그대로 throw
