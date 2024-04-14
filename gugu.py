startnum=2      #시작 단
endnum=9        #끝 단


# 각 열의 개수 입력 받기
num_cols = int(input("몇 열로 출력할까요? "))

#몫
mok = 8//num_cols

#나머지
na = 8%num_cols
if na != 0:     #나머지가 있으면 한번 더 반복하게
    mok=mok+1


#몫 만큼 반복
for c in range(1, mok + 1):

    
    #끝 단을 2+ 보여질 열 값 + 몫 반복 숫자 예) 2 + (3(열)*1) = 5
    #5까지 그러니 2,3,4단 까지만 나오게 하는거임
    #다음은 2 + (3(열)*2) = 8 | 5,6,7 까지
    endnum=2+(num_cols*c)
    if endnum > 9:      #9단이 넘어가면 9단까지만 나오게
        endnum=10

    for i in range(1, 10):  # 1부터 9까지의 숫자에 대해 반복

        for j in range(startnum, endnum):  # 해당 열의 범위 내에서 반복

            print(j, "x", i, "=", i * j, end="\t")  # 구구단의 결과 출력

        print()  # 각 구구단 사이에 한 줄 띄기
        
    startnum=endnum #2,3,4 단이 반복되었으면 다음에는 5단부터 반복이니까 시작값을 5단으로 해놓는거임.

    print()