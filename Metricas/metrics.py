import time


class Metrics:

    def __init__(self):

        self.execution_time = 0
        self.states_explored = 0
        self.success_rate = 0

        self.start_time = None

    def start(self):
        self.start_time = time.time()

    def stop(self):
        self.execution_time = time.time() - self.start_time