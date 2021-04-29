import typing
import hashlib
from threading import Thread
from multiprocessing import Process, Queue, Value
from plutus import (
    passphrase_to_address,
    passphrase_to_private_key,
    load_database,
    passphrase_to_public_key,
    process,
    private_key_to_public_key,
    public_key_to_address,
)
from config import DATABASE

class Counter(object):
    def __init__(self):
        self.val = Value('i', 0)

    def increment(self, n=1):
        with self.val.get_lock():
            self.val.value += n

    @property
    def value(self):
        return self.val.value

counter = Counter()

def generate(queue: Queue, database: typing.List):
    print("generating...")
    i = 0
    for db in database:
        for public_key in db:
            # i+=1
            # if i % 1000 == 0:
            #     print(i)
            queue.put(public_key)


def check(name: str, queue: Queue, database: typing.List):
    print(f"Worker {name} start to work...")
    global counter
    while True:
        if not queue.empty():
            passphrase = queue.get()
            counter.increment(1)
            if counter.value % 1000 == 0:
                print(counter.value)
            pri = passphrase_to_private_key(passphrase)
            pub = private_key_to_public_key(pri)
            addr = public_key_to_address(pub)
            
            # (pri, pub, addr) = queue.get()
            process(pri, pub, addr, database)


def main():
    q = Queue()

    database = load_database(DATABASE)
    
    producer = Thread(target=generate, args=(q, database))
    producer.start()

    consumers = []
    for i in range(4):
        name = 'Consumer-{}'.format(i)
        consumer = Process(target=check, args=(name, q, database))
        consumer.start()
        consumers.append(consumer)

    producer.join()

    for consumer in consumers:
        consumer.join()
    
    q.join()

if __name__ == '__main__':
    main()
