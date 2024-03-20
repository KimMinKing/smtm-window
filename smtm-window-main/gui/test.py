import requests
import pandas as pd
import time
from concurrent.futures import ThreadPoolExecutor

# URL = "https://api.upbit.com/v1/trades/ticks"
start = time.time()


def save_dataframes_to_csv(datas, file_path='output.csv'):
    # CSV 파일에 데이터 추가
    for i, data in enumerate(datas, start=1):
        # DataFrame으로 변환
        df = pd.DataFrame(data, index=range(len(data)))

        
        # CSV 파일에 DataFrame 추가
        if i == 1:
            # 첫 번째 DataFrame일 때 파일을 새로 생성
            df.to_csv(file_path, encoding='utf-8-sig', index=False)
        else:
            # 나머지 DataFrame일 때 파일을 추가 모드로 열어서 추가
            df.to_csv(file_path, mode='a', encoding='utf-8-sig', index=False, header=False)



def get_url(url):
    response=requests.get(url).json()
    
    restype=type(response)
    if restype==dict:
        print(response)
        return response
    df = pd.DataFrame(response)
    return df

list_of_urls = ["https://api.upbit.com/v1/trades/ticks?market=KRW-TT&count=500",
                "https://api.upbit.com/v1/trades/ticks?market=KRW-MASK&count=500",
                "https://api.upbit.com/v1/trades/ticks?market=KRW-APT&count=500",
                "https://api.upbit.com/v1/trades/ticks?market=KRW-AVAX&count=500",
                "https://api.upbit.com/v1/trades/ticks?market=KRW-KAVA&count=500",
                "https://api.upbit.com/v1/trades/ticks?market=KRW-LINK&count=500",
                "https://api.upbit.com/v1/trades/ticks?market=KRW-BTT&count=500",
                "https://api.upbit.com/v1/trades/ticks?market=KRW-JST&count=500",
                "https://api.upbit.com/v1/trades/ticks?market=KRW-TRX&count=500",
                "https://api.upbit.com/v1/trades/ticks?market=KRW-STX&count=500",
                "https://api.upbit.com/v1/trades/ticks?market=KRW-SUI&count=500",
                "https://api.upbit.com/v1/trades/ticks?market=KRW-ETH&count=500",
                "https://api.upbit.com/v1/trades/ticks?market=KRW-ARB&count=500",
                "https://api.upbit.com/v1/trades/ticks?market=KRW-GAS&count=500",
                "https://api.upbit.com/v1/trades/ticks?market=KRW-CRO&count=500",          
                "https://api.upbit.com/v1/trades/ticks?market=KRW-SUI&count=500",
                "https://api.upbit.com/v1/trades/ticks?market=KRW-ETH&count=500",
                "https://api.upbit.com/v1/trades/ticks?market=KRW-ARB&count=500",
                "https://api.upbit.com/v1/trades/ticks?market=KRW-GAS&count=500",
                "https://api.upbit.com/v1/trades/ticks?market=KRW-CRO&count=500",  
                "https://api.upbit.com/v1/trades/ticks?market=KRW-SUI&count=500",
                "https://api.upbit.com/v1/trades/ticks?market=KRW-ETH&count=500",
                "https://api.upbit.com/v1/trades/ticks?market=KRW-ARB&count=500",
                "https://api.upbit.com/v1/trades/ticks?market=KRW-GAS&count=500",
                "https://api.upbit.com/v1/trades/ticks?market=KRW-CRO&count=500",    
                "https://api.upbit.com/v1/trades/ticks?market=KRW-CRO&count=500",  
                "https://api.upbit.com/v1/trades/ticks?market=KRW-CRO&count=500",  
                "https://api.upbit.com/v1/trades/ticks?market=KRW-SUI&count=500",
                "https://api.upbit.com/v1/trades/ticks?market=KRW-ETH&count=500",
                "https://api.upbit.com/v1/trades/ticks?market=KRW-ARB&count=500",
                "https://api.upbit.com/v1/trades/ticks?market=KRW-GAS&count=500",
                "https://api.upbit.com/v1/trades/ticks?market=KRW-CRO&count=500",          
                "https://api.upbit.com/v1/trades/ticks?market=KRW-SUI&count=500",
                "https://api.upbit.com/v1/trades/ticks?market=KRW-ETH&count=500",
                "https://api.upbit.com/v1/trades/ticks?market=KRW-ARB&count=500",
                "https://api.upbit.com/v1/trades/ticks?market=KRW-GAS&count=500",
                "https://api.upbit.com/v1/trades/ticks?market=KRW-SUI&count=500",
                "https://api.upbit.com/v1/trades/ticks?market=KRW-ETH&count=500",
                "https://api.upbit.com/v1/trades/ticks?market=KRW-ARB&count=500",
                "https://api.upbit.com/v1/trades/ticks?market=KRW-GAS&count=500",
                "https://api.upbit.com/v1/trades/ticks?market=KRW-CRO&count=500",          
                "https://api.upbit.com/v1/trades/ticks?market=KRW-SUI&count=500",
                "https://api.upbit.com/v1/trades/ticks?market=KRW-ETH&count=500",
                "https://api.upbit.com/v1/trades/ticks?market=KRW-ARB&count=500",
                "https://api.upbit.com/v1/trades/ticks?market=KRW-GAS&count=500",
                "https://api.upbit.com/v1/trades/ticks?market=KRW-SUI&count=500",
                "https://api.upbit.com/v1/trades/ticks?market=KRW-ETH&count=500",
                "https://api.upbit.com/v1/trades/ticks?market=KRW-ARB&count=500",
                "https://api.upbit.com/v1/trades/ticks?market=KRW-GAS&count=500",
                "https://api.upbit.com/v1/trades/ticks?market=KRW-CRO&count=500",          
                "https://api.upbit.com/v1/trades/ticks?market=KRW-SUI&count=500",
                "https://api.upbit.com/v1/trades/ticks?market=KRW-ETH&count=500",
                "https://api.upbit.com/v1/trades/ticks?market=KRW-ARB&count=500",
                "https://api.upbit.com/v1/trades/ticks?market=KRW-GAS&count=500",   
]
print(len(list_of_urls))


# 그룹의 크기 결정
group_size = 10

# URL 리스트를 그룹의 크기에 맞게 나누기
url_chunks = [list_of_urls[i:i+group_size] for i in range(0, len(list_of_urls), group_size)]

# response_list 초기화
response_list=[]

# 나뉜 URL 리스트에 대해 반복하여 작업 수행
for chunk in url_chunks:
    print("Processing chunk of URLs:")
    
    with ThreadPoolExecutor(max_workers=10) as pool:
        response_list.extend(list(pool.map(get_url,chunk)))
    time.sleep(0.1)

print(len(response_list))

# 결과를 Excel 파일로 저장
save_dataframes_to_csv(response_list)

end = time.time()
print(f"---- 프로그램 실행 시간은 {round(end-start, 1)}초")