from modelfit.worker.celery_app import celery_app


def main() -> None:
    celery_app.worker_main(["worker", "--loglevel=INFO"])
