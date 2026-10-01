from apscheduler.schedulers.blocking import BlockingScheduler

from etl.pipeline import run_pipeline

scheduler = BlockingScheduler()

# scheduler.add_job(
#     run_pipeline,
#     trigger="cron",
#     hour=0,
#     minute=0
# )

scheduler.add_job(run_pipeline, trigger="interval", minutes=2)

print("Scheduler started...")

scheduler.start()
