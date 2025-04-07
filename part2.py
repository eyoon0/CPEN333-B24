# Group #: B24
# Student names: Jesse Tam, Eric Yoon
 
import threading
import queue
import time, random

def consumerWorker(queue: queue.Queue) -> None:

    while True:
        item = queue.get() # Retrieving item from the buffer queue
        
        time.sleep(random.uniform(RANDOM_TIME_MIN, RANDOM_TIME_MAX)) # Randomized time taken to consume an item
        print(f"[{threading.current_thread().name}] Consumed: {item}")

        queue.task_done() # Signal that the work on the retrieved item is done

def producerWorker(queue: queue.Queue) -> None:

    for i in range(PRODUCER_ITEMS):
        time.sleep(random.uniform(RANDOM_TIME_MIN, RANDOM_TIME_MAX)) # Randomized time taken to produce an item
        item = random.randint(1, 100)  # Produce a random item

        queue.put(item) # Puts the random item into the buffer queue
        print(f"[{threading.current_thread().name}] Produced: {item}") # Signifies that the item has been produced

    print(f"[{threading.current_thread().name}] Finished producing.") # When producer x is finished producing 5 items, leaves the loop and states it is finished

if __name__ == "__main__":
    
    buffer = queue.Queue()

    PRODUCERS = 4
    CONSUMERS = 5
    PRODUCER_ITEMS = 5
    RANDOM_TIME_MIN = 1
    RANDOM_TIME_MAX = 5

    consumer_threads = []
    for i in range(CONSUMERS): # Create and start consumer threads
        t = threading.Thread(target=consumerWorker, args=(buffer,), daemon=True, name=f"Consumer-{i}")
        t.start()
        consumer_threads.append(t)

    producer_threads = []
    for i in range(PRODUCERS): # Create and start producer threads
        t = threading.Thread(target=producerWorker, args=(buffer,), name=f"Producer-{i}")
        t.start()
        producer_threads.append(t)

    for t in producer_threads: # Wait for all producer threads to finish
        t.join()

    buffer.join() # Block until all items in the queue have been processed

    print("All items have been produced and consumed.")