# Group #: B24
# Student names: Jesse Tam, Eric Yoon
 
import threading
import queue
import time, random

def consumerWorker(q: queue.Queue) -> None:
    """
    Target worker function for a consumer thread.

    Continuously attempts to retrieve an item from the shared queue.
    Simulates the consumption of items (by sleeping for a random
    amount of time). Calls q.task_done() to signal that the item
    has been fully processed.

    Since this thread is daemon, it will automatically terminate
    when the main thread completes (i.e., once we've joined on the
    queue and the main thread ends).
    """
    while True:
        # Blocking call to get an item from the queue
        item = q.get()
        # Simulate the time taken to consume the item
        time.sleep(random.uniform(0.1, 0.5))
        print(f"[Consumer-{threading.current_thread().name}] Consumed: {item}")
        # Signal that the work on the retrieved item is done
        q.task_done()

def producerWorker(q: queue.Queue, producer_id: int, items_to_produce: int) -> None:
    """
    Target worker function for a producer thread.

    Produces a fixed number of items (items_to_produce), simulating
    randomness in production time. Each produced item is placed
    into the shared queue.
    
    :param q: Shared queue used as a FIFO buffer.
    :param producer_id: Identifier for this producer (for logging/monitoring).
    :param items_to_produce: How many items this producer should generate.
    """
    for i in range(items_to_produce):
        # Simulate the time taken to produce an item
        time.sleep(random.uniform(0.1, 0.5))
        item = random.randint(1, 100)  # Example: produce a random integer
        q.put(item)
        print(f"[Producer-{producer_id}] Produced: {item}")
    print(f"[Producer-{producer_id}] Finished producing.")

if __name__ == "__main__":
    # Shared FIFO queue
    buffer = queue.Queue()

    # Configuration (easily changeable):
    NUM_PRODUCERS = 4
    NUM_CONSUMERS = 5
    ITEMS_PER_PRODUCER = 5  # Each producer will produce 5 items

    # Create and start consumer threads (daemon for simplicity).
    # Being daemon means these threads won't block the program from exiting.
    consumers = []
    for i in range(NUM_CONSUMERS):
        t = threading.Thread(
            target=consumerWorker,
            args=(buffer,),
            daemon=True,  # Daemon thread
            name=f"Consumer-{i}"
        )
        t.start()
        consumers.append(t)

    # Create and start producer threads
    producers = []
    for producer_id in range(NUM_PRODUCERS):
        t = threading.Thread(
            target=producerWorker,
            args=(buffer, producer_id, ITEMS_PER_PRODUCER),
            name=f"Producer-{producer_id}"
        )
        t.start()
        producers.append(t)

    # Wait for all producer threads to finish
    for t in producers:
        t.join()

    # Block until all items in the queue have been processed
    buffer.join()

    print("All items have been produced and consumed. Main thread exiting.")