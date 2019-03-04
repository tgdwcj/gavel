import argparse
import grpc
import numpy as np
import time

import runtime.rpc.scheduler_client as scheduler_client
import scheduler

class TestPolicy:
    def get_allocation(self, throughputs):
        (m, n) = throughputs.shape
        return np.full((m, n), 1.0 / m)

def get_num_epochs_to_run(job_id, worker_type):
    return 1

def read_trace(trace_filename):
    commands_and_num_epochs = []
    with open(trace_filename, 'r') as f:
       for command_and_num_epochs in f.read().strip().split('\n'):
           [command, num_epochs] = command_and_num_epochs.split('\t')
           num_epochs = int(num_epochs)
           commands_and_num_epochs.append((command, num_epochs))
    return commands_and_num_epochs

def main(trace_filename, min_workers, sleep_seconds):
    num_epochs_left = {}
    s = scheduler.Scheduler(TestPolicy(), get_num_epochs_to_run,
                            min_workers=min_workers)
    start = time.time()
    for (command, num_epochs) in read_trace(trace_filename):
        job_id = s.add_job(command, num_epochs)

    while s.num_jobs() > 0:
        time.sleep(sleep_seconds)

    print("Total time taken: %.2f seconds" % (time.time() - start))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Execute a trace"
    )
    parser.add_argument('-t', "--trace_filename", type=str, required=True,
                        help="Trace filename")
    parser.add_argument('-m', "--min_workers", type=int, default=None,
                        help="Minimum number of workers to wait for before " \
                             "scheduling jobs")
    parser.add_argument('-s', "--sleep_seconds", type=int, default=10,
                        help="Number of seconds to sleep when waiting for all" \
                             "jobs to complete")
    args = parser.parse_args()

    main(args.trace_filename, args.min_workers, args.sleep_seconds)