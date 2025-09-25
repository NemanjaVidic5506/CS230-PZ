import os
from celery import Celery, current_task
from model import train_regression_synthetic, train_openml_dataset

BROKER = os.getenv("CELERY_BROKER_URL", "redis://redis:6379/0")
BACKEND = os.getenv("CELERY_RESULT_BACKEND", BROKER)

celery = Celery("tasks", broker=BROKER, backend=BACKEND)

@celery.task(name="tasks.train_synthetic")
def train_synthetic(n_samples=1000, n_features=20, noise=0.1, random_state=42):
  task_id = current_task.request.id
  return train_regression_synthetic(task_id, n_samples, n_features, noise, random_state)

@celery.task(name="tasks.train_openml")
def train_openml(dataset="diabetes", target=None):
  task_id = current_task.request.id
  return train_openml_dataset(task_id, dataset, target)
