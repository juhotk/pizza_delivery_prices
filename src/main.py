import time

import pizza_job
from extended_scheduler import ExtendedScheduler


def main() -> None:
    scheduler = ExtendedScheduler()
    scheduler.every(10).minutes.do(pizza_job.run)

    while len(scheduler.get_jobs()) > 0:
        scheduler.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    main()
