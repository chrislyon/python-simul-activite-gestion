import sys
import time
import random
import signal
import multiprocessing

processes = []

def launch_process(number, kill_queue, child_connection):

    kill_flag = False

    while not kill_flag:
        while child_connection.poll():
            print 'Process %s received message: %s' % (number, child_connection.recv())
        child_connection.send('Process %s sending message to parent' % number)
        sleep_time = random.choice(range(5))
        print 'Thread %s, checking in... sleep: %s' % (number, sleep_time)
        time.sleep(sleep_time)
        if not kill_queue.empty():
            kill_flag = kill_queue.get()
            print 'Got %s from the queue.' % kill_flag
    return

def signal_handler(signal, frame):

    print '\nCaught interrupt, cleaning up...'
    for process in processes:
        print process.terminate()

    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

if __name__ == '__main__':

    parent_connections = []
    kill_queue = multiprocessing.Queue()

    for number in range(5):
        parent_connection, child_connection = multiprocessing.Pipe()
        parent_connections.append(parent_connection)
        process = multiprocessing.Process(target=launch_process, args=(number,kill_queue,child_connection,))
        process.start()
        processes.append(process)

    for number in range(10):
        print 'Main process sleeping: %s...' % number
        time.sleep(1)

    for number, parent_connection in enumerate(parent_connections):
        parent_connection.send('Parent sending message to child %s' % number)

    print 'Done with incremental messages.'
    for number in range(10):
        print 'Main process sleeping: %s...' %number
        time.sleep(1)

    for number in range(10):
        child = random.choice(range(len(parent_connections)))
        parent_connections[child].send('Parent sending message to child %s' % child)

    for number in range(10):
        for parent_connection in parent_connections:
            while parent_connection.poll():
                print 'Parent thread received message: %s' % parent_connection.recv()
        print 'All messages processed, sleeping for 1 second before polling again.'
        time.sleep(1)

    for process in processes:
        kill_queue.put(True)
    
    for process in processes:
        process.join()

    print 'Main thread done.'

