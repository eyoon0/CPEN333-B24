# Group #: B24
# Student names: Jesse Tam, Eric Yoon
 
import threading
import queue
import time, random

RANDOM_TIME = (1,5)

def consumerWorker (queue):
    """target worker for a consumer thread"""
    while True:

        item = queue.get()
        if item is None:
            break

        print(f"Consumer {threading.current_thread().name} consumed {item}.")
        time.sleep(random.randint(RANDOM_TIME))
        queue.task_done()
  
def producerWorker(queue):
    """target worker for a producer thread"""
    
    for i in range(ITEMS // PRODUCER_THREADS):
        item = random.randint(1,100)
        print(f"Producer {threading.current_thread().name} produced {item}.")
        queue.put(item)
        time.sleep(random.randint(RANDOM_TIME))

    queue.put(None)

if __name__ == "__main__":
    buffer = queue.Queue()
    
    PRODUCER_THREADS = 4
    CONSUMER_THREADS = 5
    ITEMS = 20

    producers = []
    consumers = []

    for i in range(PRODUCER_THREADS):
        t = threading.Thread(target=producerWorker, args=(buffer,))
        producers.append(t)
        t.start()

    for i in range(CONSUMER_THREADS):
        t = threading.Thread(target=consumerWorker, args=(buffer,))
        t.start()

    for t in producers:
        t.join()
    
    buffer.join()

    print("All items have been produced and consumed.")