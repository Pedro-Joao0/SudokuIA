import time


class Metrics:

    def __init__(self):

        self.execution_time  = 0
        self.states_explored = 0
        self.success_rate    = 0
        self.score_history   = []

        self.start_time = None

    def start(self):
        self.start_time = time.time()

    def stop(self):
        self.execution_time = time.time() - self.start_time

    def increment_states(self):
        self.states_explored += 1

    def mark_success(self):
        self.success_rate = 1.0

    def mark_fail(self):
        self.success_rate = 0.0

    def reset(self):
        self.execution_time  = 0
        self.states_explored = 0
        self.success_rate    = 0
        self.score_history   = []
        self.start_time      = None

    def to_dict(self):
        return {
            "time":    self.execution_time,
            "states":  self.states_explored,
            "success": self.success_rate,
        }

    @staticmethod
    def show_chart(results: dict):
        import matplotlib.pyplot as plt
        algos  = list(results.keys())
        times  = [results[a]["time"]   for a in algos]
        states = [results[a]["states"] for a in algos]
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9, 4))
        fig.suptitle("Algorithm Performance Comparison")
        b1 = ax1.bar(algos, times,  color="black")
        ax1.set_title("Execution Time (s)")
        ax1.bar_label(b1, fmt="%.4f", padding=3)
        b2 = ax2.bar(algos, states, color="black")
        ax2.set_title("States Explored")
        ax2.bar_label(b2, padding=3)
        plt.tight_layout()
        plt.show()