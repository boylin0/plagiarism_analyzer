from app import app
from worker import WorkerPool
from time import sleep

#workerPool = WorkerPool('D:\\Users\\boylin0\\Documents\\Work\\plagiarism_analyzer\\data\\c.1B.hw4')
#
#workerPool.StartWorker()
#
#try:
#    while True:
#        sleep(1)
#        print(workerPool.getProgress())
#        print(workerPool.getResult())
#except KeyboardInterrupt:
#    workerPool.StopWorker()
#    print('exit')

if __name__ == '__main__':
    app.run(host='localhost', port=3001, debug=True)
