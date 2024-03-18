import requests
import pandas as pd
import time
from concurrent.futures import ThreadPoolExecutor

# URL = "https://api.upbit.com/v1/trades/ticks"
start = time.time()

def get_url(url):
    response=requests.get(url).json()
    df = pd.DataFrame(response)
    return df

list_of_urls = ["https://api.upbit.com/v1/trades/ticks?market=KRW-TT&count=500",
                "https://api.upbit.com/v1/trades/ticks?market=KRW-MASK&count=500",
                "https://api.upbit.com/v1/trades/ticks?market=KRW-APT&count=500",
                "https://api.upbit.com/v1/trades/ticks?market=KRW-AVAX&count=500",
                "https://api.upbit.com/v1/trades/ticks?market=KRW-KAVA&count=500",
                "https://api.upbit.com/v1/trades/ticks?market=KRW-LINK&count=500",
                "https://api.upbit.com/v1/trades/ticks?market=KRW-SOL&count=500",
                "https://api.upbit.com/v1/trades/ticks?market=KRW-SOL&count=500",
                "https://api.upbit.com/v1/trades/ticks?market=KRW-SOL&count=500",
                "https://api.upbit.com/v1/trades/ticks?market=KRW-SOL&count=500",
                "https://api.upbit.com/v1/trades/ticks?market=KRW-LINK&count=500",
                "https://api.upbit.com/v1/trades/ticks?market=KRW-SOL&count=500",
                "https://api.upbit.com/v1/trades/ticks?market=KRW-SOL&count=500",
                "https://api.upbit.com/v1/trades/ticks?market=KRW-SOL&count=500",
                "https://api.upbit.com/v1/trades/ticks?market=KRW-SOL&count=500",
                "https://api.upbit.com/v1/trades/ticks?market=KRW-LINK&count=500",
                "https://api.upbit.com/v1/trades/ticks?market=KRW-SOL&count=500",
                "https://api.upbit.com/v1/trades/ticks?market=KRW-SOL&count=500",
]

with ThreadPoolExecutor(max_workers=10) as pool:
    futures = []
    for url in list_of_urls:
        futures.append(pool.submit(get_url, url))

    # 각 작업이 완료될 때까지 기다리고, 작업이 완료된 후 일정 시간 동안 쉬기
    for future in futures:
        result = future.result()  # 작업이 완료될 때까지 기다림
        print(result)  # 결과 출력
        time.sleep(0.1)  # 일정 시간 동안 쉬기

# for response in response_list:
#     print(response)

print(len(list_of_urls))

end = time.time()
print(f"---- 프로그램 실행 시간은 {round(end-start, 1)}초")
