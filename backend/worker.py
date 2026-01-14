from rq import Worker
from services.jobs import get_queue

if __name__ == "__main__":
    queue = get_queue()
    worker = Worker([queue])
    worker.work()
