import typing
import hashlib
from queue import Queue
from threading import Thread
from plutus import passphrase_to_address, passphrase_to_private_key, load_database, passphrase_to_public_key, process
from config import DATABASE


def generate(queue: Queue, database: typing.List):
    for db in database:
        for public_key in db:
            queue.put((
                passphrase_to_private_key(public_key),
                passphrase_to_public_key(public_key),
                passphrase_to_address(public_key)
            ))


def check(queue: Queue, database: typing.List):
    while not queue.empty():
        (pri, pub, addr) = queue.get_nowait()
        process(pri, pub, addr, database)


def main():
    q = Queue(10)
    database = load_database(DATABASE)
    
    producer = Thread(target=generate, args=(q, database))
    producer.start()

    consumers = []
    for i in range(3):
        name = 'Consumer-{}'.format(i)
        consumer = Thread(target=consume, args=(q, database))
        consumer.start()
        consumers.append(consumer)

    producer.join()

    for consumer in consumers:
        consumer.join()

if __name__ == '__main__':
    main()