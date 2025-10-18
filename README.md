# KIS Auto Trading with TradingView's Webhook

한국투자증권(KIS) Open API를 활용한 해외주식 거래 및 정보 조회 코드입니다.  
이 프로젝트는 TradingView의 Webhook을 통해 매수/매도 신호를 받아 자동으로 해외주식 주문을 처리하며, 계좌 잔고 조회, 시세 분석, 이메일 알림 등의 기능을 포함합니다. **모의투자 환경에서 테스트
후 실전 적용을 권장합니다.**

⚠️ **주의**: 이 코드는 교육 및 테스트 목적으로만 사용하세요. <u>실제 투자 시 발생하는 손실에 대한 책임은 사용자에게 있으며, API 키와 계좌 정보는 보안에 유의하세요.</u>

🎰️ **인증서가 없는 경우**: 인증서 없이도 구성할 수 있습니다. [설정 > 인증서가 없는 경우](#인증서가-없는-경우) 로 이동하여 적용 방법을 확인하면 됩니다.

---

## 프로젝트 구조

```shell
.
├── .env                   # email 전송 설정 파일
├── .gitignore             # gitignore
├── README.md              # 이 문서
├── pyproject.toml         # 프로젝트 설정 및 의존성 정의
├── logs                   # 로그 파일 저장 디렉토리
│   └── app.log            # 웹서버 로그 파일 (자동 생성)
├── src                    # 소스 코드 디렉토리
│   ├── account            # 계좌 관련 모듈
│   │   └── my_account.py  # 계좌 잔고 및 매수가능금액 조회
│   ├── order              # 주문 관련 모듈
│   │   └── order.py       # 해외주식 매수/매도 함수
│   ├── overseas_stock     # 해외주식 API 함수
│   │   └── overseas_stock_functions.py  # 시세 조회, 주문 등의 API 호출 함수
│   ├── stocks_info        # 주식 정보 조회 모듈
│   │   └── stocks_info.py # 거래량 순위, 상승/하락률 등 조회 함수
│   └── utils              # 유틸리티 모듈
│       ├── email_utils.py # 이메일 전송 (Gmail 사용)
│       ├── kis_auth.py    # KIS API 인증 및 토큰 관리
│       └── utils.py       # API 호출 헬퍼 (safe_api_call 등)
├── uv.lock                # uv 패키지 매니저 락 파일 (의존성 고정)
└── webserver.py           # Flask 웹서버 (TradingView webhook 수신)
```

---

## 요구사항

- Python 3.13 이상
- KIS Open API 앱키/앱시크릿 (한국투자증권 개발자 센터에서 발급: https://apiportal.koreainvestment.com/)
- TradingView 계정 (webhook 신호 전송용)
- Gmail 계정 (이메일 알림용, 앱 비밀번호 필요) - 필수 아님

---

## 설치

이 프로젝트는 `uv` 패키지 매니저를 사용합니다. (uv가 없으면 설치 가이드 참조)

- 리포지토리 클론

```shell
git clone https://github.com/your-repo/kis-github.git
cd kis-github
```

- 의존성 설치 (pyproject.toml 기반)

```shell
uv sync
```

🛠️ 주요 의존성: pandas, pycryptodome, pyqt6, pyside6, pyyaml, requests, websockets, Flask, python-dotenv

---

## 설정

### **환경 변수 설정 (.env 파일 생성. 필수 X)**

- 프로젝트 루트에 `.env` 파일을 생성하고 아래 내용을 입력하세요.
- 이메일을 보내는 경우에만 해당 정보를 입력하면 되며, 이메일을 보내지 않으려면 [webserver.py](webserver.py) 에서 `send_email` 부분을 주석처리 및 삭제하여 구동하세요.

```text
SENDER_EMAIL=your_gmail@gmail.com          # Gmail 발신자 이메일
SENDER_PASSWORD=your_app_password          # Gmail 앱 비밀번호 (2단계 인증 활성화 후 생성)
RECEIVER_EMAIL=receiver_email@example.com  # 수신자 이메일
```

### **KIS API 설정 (YAML 파일)**

- `~/KIS/config/kis_devlp.yaml` 파일을 생성하고 아래 내용을 입력하세요. (kis_auth.py 참조)

```text
# 홈페이지에서 API서비스 신청시 받은 Appkey, Appsecret 값 설정
# 실전투자
my_app: 'YOUR_APP_KEY'
my_sec: 'YOUR_APP_SECRET'

# HTS ID
my_htsid: 'YOUR_HTS_ID'

# 계좌번호 앞 8자리
my_acct_stock: "종합계좌번호 8자리"
#my_acct_future: "선물옵션계좌 8자리"
#my_paper_stock: "모의투자 증권계좌 8자리"
#my_paper_future: "모의투자 선물옵션계좌 8자리"

# 계좌번호 뒤 2자리
my_prod: "01" # 종합계좌
# my_prod: "03" # 국내선물옵션계좌
# my_prod: "08" # 해외선물옵션 계좌
# my_prod: "22" # 개인연금
# my_prod: "29" # 퇴직연금

# domain infos
prod: "https://openapi.koreainvestment.com:9443" # 서비스
ops: "ws://ops.koreainvestment.com:21000" # 웹소켓
vps: "https://openapivts.koreainvestment.com:29443" # 모의투자 서비스
vops: "ws://ops.koreainvestment.com:31000" # 모의투자 웹소켓

my_token: "" # 토큰 (자동생성)

# User-Agent; Chrome > F12 개발자 모드 > Console > navigator.userAgent > 자신의 userAgent 확인가능
my_agent: "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
```

- 토큰은 `kis_auth.py`에서 자동 관리되며, `~/KIS/config/KISYYYYMMDD` 파일에 저장됩니다.

### **SSL 인증서 (webserver.py)**

- HTTPS를 위해 `crt.pem` (인증서)와 `key.pem` (개인 키)를 프로젝트 루트에 배치 (자체 서명 또는 Let's Encrypt 사용)
- 인증서 없이 HTTP으로도 설정 가능

### **TradingView webhook 설정**

- TradingView 알림(Alert)에서 webhook URL을 `https://your-domain/webhook` 으로 설정하며, 별도로 포트 설정은 불가능. 즉, 80(HTTP), 443(HTTPS)만
  가능.
- 페이로드 예시:

```json
{
  "ticker": "TSLA",
  "value": "buy"
}
```

🔫 **value** 는 <u>*buy* 혹은 *sell*</u>

- 시크릿 키는 별도로 설정하면 좋겠지만, TradingView의 Webhook에서 지원하지 않음

### **인증서가 없는 경우**

- TradingView의 Webhook은 <u>http 혹은 https</u> 로만 통신이 가능하며, 80과 443을 제외한 포트로는 전송 불가능  
  (인증서가 없으면 http(80 port)만 사용 가능)
- [webserver.py](webserver.py) 에서 인증서 관련 내용(`ssl_context`)을 삭제 처리 후 진행

---

## 사용법

### 인증 및 환경 로드

```python
import src.utils.kis_auth as ka

ka.auth()  # 토큰 발급/갱신
trenv = ka.getTREnv()  # 환경 변수 로드 (계좌번호 등)
```

### 주요 기능 및 예시

- 계좌 잔고 조회 (my_account.py)

```python
from src.account.my_account import get_account_balance

balance = get_account_balance(trenv)
print(balance[0])  # 잔고 DataFrame
```

- 매수/매도 (order.py)

```python
from src.order.order import buy_overseas_stock, sell_overseas_stock

buy_result = buy_overseas_stock(trenv, "TSLA", 10)  # TSLA 10주 매수
sell_result = sell_overseas_stock(trenv, "TSLA", 5)  # TSLA 5주 매도
```

- 시세 정보 조회 (stocks_info.py)

```python
from src.stocks_info.stocks_info import get_trade_vol, get_updown_rate

trade_vol_df1, trade_vol_df2 = get_trade_vol("NAS")  # 거래량 순위
updown_df1, updown_df2 = get_updown_rate("1", "NAS")  # 상승률
```

- 이메일 전송 (email_utils.py)

```python
from src.utils.email_utils import send_email

send_email("테스트 제목", "테스트 메시지")
```

- 웹 서버 실행 (webserver.py)

    - 포트 5556에서 HTTPS 서버 실행
    - TradingView webhook 수신 시 자동 매매 처리 (buy/sell)
    - 중복 신호 방지: 30초 내 동일 신호 무시
    - 성공/실패 시 이메일 알림 전송

```shell
uv run. / webserver.py
```

### 로그 확인

- `logs/app.log.YYYY-MM-DD` 파일에서 일자별 로그 확인 (자동 로테이션).

---

## 주요 파일 설명

- **kis_auth.py**: API 인증, 토큰 관리, 웹소켓 연결. AES 암호화 및 YAML 설정 로드.
- **overseas_stock_functions.py**: KIS API 호출 헬퍼 (주문, 시세 조회, 뉴스 등). 안전한 API 호출(safe_api_call) 포함.
- **my_account.py**: 계좌 잔고(inquire_balance) 및 매수가능금액(inquire_psamount) 조회.
- **order.py**: 시장가 매수/매도 함수.
- **stocks_info.py**: 거래량 순위, 상승/하락률, 거래량 급증, 뉴스 조회 등.
- **email_utils.py**: Gmail SMTP를 사용한 이메일 전송.
- **utils.py**: API 에러 핸들링(safe_api_call) 및 헬퍼 함수.
- **webserver.py**: Flask 웹서버. TradingView webhook 수신 → 매매 처리 → 이메일 알림.

---

## 주의사항

- **API 제한**: KIS API는 호출 횟수 제한이 있음. `smart_sleep()`으로 지연 처리.
- **모의투자**: 실전 도메인 대신 모의 도메인 사용 시 `kis_devlp.yaml`의 `my_url` 변경.
- **보안**: API 키, 비밀번호를 Git에 커밋하지 마세요. `.gitignore`에 `.env`와 YAML 추가.
- **에러 핸들링**: 토큰 만료 시 자동 재인증 (utils.py).
- **테스트**: 실제 매매 전에 모의 환경에서 테스트하세요.

---

## License

MIT License

---

## 참조

- [KIS Open Trading API](https://github.com/koreainvestment/open-trading-api)
- [TradeHook](https://github.com/haguri-peng/TradeHook)
