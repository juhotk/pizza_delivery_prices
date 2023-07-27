import ctypes

from schedule import Scheduler, Job, CancelJob


class ExtendedScheduler(Scheduler):
    """ Modified version of the original scheduler that allows jobs to return values and supports exceptions. """

    def __init__(self, run_all_at_start=True, cancel_jobs_on_failure=True):
        """ Initializes the extended class and the parent
            :param run_all_at_start: if False the jobs will be run for the first time on the scheduled time instead of
                immediately and then according to the schedule
            :param cancel_jobs_on_failure: whether the jobs should be permanently canceled when a fail-state has
                been reached. Otherwise, they will be rescheduled. """
        super().__init__()
        self.cancel_jobs_on_failure = cancel_jobs_on_failure
        self.dll = ctypes.WinDLL("user32")

        if run_all_at_start is True:
            self.run_all()

    def run_pending(self) -> list[object]:
        """ Overrides the parent function so that it returns the outputs """
        runnable_jobs = (job for job in self.jobs if job.should_run)
        list_of_returns = []

        for job in sorted(runnable_jobs):
            list_of_returns.append(self._run_job(job))

        return list_of_returns

    def _run_job(self, job: Job) -> object:
        """ Overrides the parent function so that exceptions are accounted for and the user is informed
            about any jobs that have come to a halt.
            :param job: an instance of schedule.Job
        """
        try:
            res = job.run()
            if isinstance(res, CancelJob) or res is CancelJob or res is False:
                self.cancel_job(job)
                self.dll.MessageBoxW(0, "The scheduled job has stopped.", "Job stopped", 0x1000)

            return res
        except Exception:
            self.dll.MessageBoxW(
                0, "The scheduled job has stopped due to an exception.", "Job stopped", 0x00000010 | 0x1000)

            if self.cancel_jobs_on_failure is True:
                self.cancel_job(job)

            return None
