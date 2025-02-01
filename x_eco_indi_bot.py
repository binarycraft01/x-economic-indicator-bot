import os
import tweepy
import schedule
import requests
import time
import json
import logging
from dotenv import load_dotenv
from datetime import datetime

##### 로깅 설정: 로그 레벨을 INFO로 설정하고, 시간, 로그 레벨, 메시지를 포함하도록 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

##### .env 파일에서 환경 변수 로드
load_dotenv()  

##### X(트위터) API KEY 및 한국은행 ECOS API KEY 설정
consumer_key = os.getenv("CONSUMER_KEY")
consumer_secret = os.getenv("CONSUMER_SECRET")
access_token = os.getenv("ACCESS_TOKEN")
access_token_secret = os.getenv("ACCESS_TOKEN_SECRET")
bok_api_key = os.getenv("BOK_ECOS_API_KEY")

###### 필요한 모든 환경 변수 및 API KEY가 잘 설정되어 있는지 확인
required_env_vars = ["CONSUMER_KEY", "CONSUMER_SECRET", "ACCESS_TOKEN", "ACCESS_TOKEN_SECRET", "BOK_ECOS_API_KEY"]
for var in required_env_vars:
    if not os.getenv(var):
        raise ValueError(f"환경 변수 {var}가 설정되지 않았습니다.")


###### Tweepy Client 객체 생성 (Twitter API v2 사용)
client = tweepy.Client(
    consumer_key=consumer_key, 
    consumer_secret=consumer_secret,
    access_token=access_token, 
    access_token_secret=access_token_secret
)

###### 한국은행 ECOS API URL 설정
API_URL = f"https://ecos.bok.or.kr/api/KeyStatisticList/{bok_api_key}/json/kr/1/101"

###### 받아온 핵심지표 정보 날짜 데이터 가공
def format_date(date_str):
    if len(date_str) == 8:  # YYYYMMDD 형식
        return datetime.strptime(date_str, '%Y%m%d').strftime('%Y년%m월%d일')
    elif len(date_str) == 6:  # YYYYMM 형식
        return datetime.strptime(date_str, '%Y%m').strftime('%Y년%m월')
    elif len(date_str) == 4:  # YYYY 형식
        return f"{date_str}년"
    else:
        return date_str  # 다른 형식은 그대로 반환

###### 한국은행 ECOS API에서 데이터를 가져오는 함수
def get_api_data():
    try:
        response = requests.get(API_URL)
        response.raise_for_status()  # HTTP 오류 발생 시 예외 발생
        return response.json()
    except requests.RequestException as e:
        logging.error(f"API 요청 중 오류 발생: {e}")
        return None

###### 응답받은 API에서 중요한 경제 지표를 추출하는 함수
def extract_key_info(data):
    if not data or 'KeyStatisticList' not in data or 'row' not in data['KeyStatisticList']:
        logging.error("API 응답 데이터 형식이 올바르지 않습니다.")
        return None

    key_stats = data['KeyStatisticList']['row']
    important_stats = [
        '한국은행 기준금리',
        '콜금리(익일물)',
        '원/달러 환율(종가)',
        '코스피지수',
        '코스닥지수'
    ]
    
    result = []
    for stat in key_stats:
        if stat['KEYSTAT_NAME'] in important_stats:
            value = stat['DATA_VALUE']
            unit = stat['UNIT_NAME'].strip() if stat['UNIT_NAME'] else ''
            date = format_date(stat['CYCLE'])
            result.append(f"{stat['KEYSTAT_NAME']}: {value} {unit} ({date})")
    
    return '\n'.join(result)


##### 작성한 X(Twitter) 트윗 내용을 생성하는 함수
def create_tweet_content(key_info):
    post_time = datetime.now()
    return f"{key_info}"

###### 트윗을 작성하고 게시하는 함수
def post_tweet():
    data = get_api_data()
    if not data:
        logging.error("API 데이터를 가져오는데 실패했습니다.")
        return

    key_info = extract_key_info(data)
    if not key_info:
        logging.error("핵심 정보 추출에 실패했습니다.")
        return

    tweet_text = create_tweet_content(key_info)
    
    try:
        response = client.create_tweet(text=tweet_text)
        logging.info(f"트윗이 성공적으로 게시되었습니다. Tweet ID: {response.data['id']}")
        logging.info(f"게시된 트윗 내용:\n{tweet_text}")
    except tweepy.TweepyException as e:
        logging.error(f"트윗 게시 중 에러 발생: {e}")


# # 한국 시간에 맞춘 UTC 시간으로 설정
# schedule.every().day.at("00:00").do(post_tweet)  # 오전 9시 (한국 시간)
# schedule.every().day.at("06:00").do(post_tweet)  # 오후 3시 (한국 시간)
# schedule.every().day.at("12:00").do(post_tweet)  # 오후 9시 (한국 시간)
# schedule.every().day.at("18:00").do(post_tweet)  # 오전 3시 (한국 시간)

# # 메인 실행 부분
# if __name__ == "__main__":
#     logging.info("프로그램 시작")
#     while True:
#         try:
#             schedule.run_pending()
#             time.sleep(60)  # 1분마다 스케줄 확인
#         except Exception as e:
#             logging.error(f"예상치 못한 오류 발생: {e}")
#             time.sleep(300)  # 5분 대기 후 재시도


### 개발 테스트용 ###
# 평소에는 주석 처리
# 스케줄 없이 즉시 실행하려면 메인 실행 부분 주석 처리
# 이후 해당 부분 주석 해제하고 실행

if __name__ == "__main__":
    logging.info("프로그램 시작")
    post_tweet()  # 즉시 트윗 게시