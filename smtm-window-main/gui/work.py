import queue
import threading

class Worker:

    def __init__(self, name) :
        self.task_queue=queue.Queue()
        self.thread=None
        self.name=name
        self.on_terminated = None
        self.stop_flag = False

    #종료 콜백 함수를 등록하는 메서드.
    def register_on_terminated(self,callback):
        self.on_terminated=callback



    def post_task(self, task):
        """task를 추가한다

        task: dictionary이며 runnable에는 실행 가능한 객체를 담고 있어야 하며, runnable의 인자로 task를 넘겨준다.
        """
        self.task_queue.put(task)

    #작업을 수행할 쓰레드를 만들고 시작한다, 이미 작업이 진행되고 있는 경우 아무런 일도 일어나지 않는다.
    def start(self):
        if self.thread is not None:
            print("쓰레드가 None이 아닙니다.")
            return
        

        def looper():
            while True:
                # task에 값이 있으면 꺼내오고 없으면 계속 기다린다.
                task = self.task_queue.get()
                
                if task is None:
                    print(f"종료..task가 없어.. 워커 이름은 :{self.name}, 쓰레드 get ident 는 {threading.get_ident()}")

                    # 콜백 함수가 있다면
                    if self.on_terminated is not None:
                        self.on_terminated()    # 콜백해주고
                    self.task_queue.task_done()   # 테스크 끝내고
                    break   # 나가


                #print(f"가즈아.. 워커 이름은 :{self.name}, 쓰레드 get ident 는 {threading.get_ident()}")
                runnable = task["runnable"]
                runnable(task)
                self.task_queue.task_done()


        self.thread = threading.Thread(target=looper, name=self.name, daemon=True)
        self.thread.start()

    def stop(self):
        """현재 진행 중인 작업을 끝으로 스레드를 종료하도록 한다."""
        if self.thread is None:
            return

        self.task_queue.put(None)
        self.thread = None
        self.task_queue.join()

