import tweepy
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()  # .env 파일 로드

consumer_key = os.getenv("CONSUMER_KEY")
consumer_secret = os.getenv("CONSUMER_SECRET")
access_token = os.getenv("ACCESS_TOKEN")
access_token_secret = os.getenv("ACCESS_TOKEN_SECRET")

# 환경 변수 확인
if not all([consumer_key, consumer_secret, access_token, access_token_secret]):
    raise ValueError("환경 변수가 올바르게 설정되지 않았습니다.")


# Client 객체 생성 (API v2 사용)
client = tweepy.Client(
    consumer_key=consumer_key, 
    consumer_secret=consumer_secret,
    access_token=access_token, 
    access_token_secret=access_token_secret
)

# 트윗을 게시하는 현재 시간
post_time = datetime.now()

# 테스트 트윗 게시
try:
    tweet_text = f"Python을 이용한 자동 글 작성 테스트 / 글 작성 시간 : {post_time.strftime('%Y년 %m월 %d일 %H시 %M분')}"
    response = client.create_tweet(text=tweet_text)
    print(f"트윗이 성공적으로 게시되었습니다. Tweet ID: {response.data['id']}")
    print(tweet_text)
    
except tweepy.TweepyException as e:
    print(f"트윗 게시 중 에러 발생: {e}")
    print(f"에러 코드: {e.api_code}")
    print(f"에러 메시지: {e.api_messages}")

# 여기에 추가 기능 구현 (예: 실시간 데이터 수집, 주기적 트윗 게시 등)
