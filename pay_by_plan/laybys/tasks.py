from django.contrib.auth import get_user_model
from huey import crontab
from huey.contrib.djhuey import periodic_task
from huey.contrib.djhuey import task

from .services import LaybyService

User = get_user_model()


@periodic_task(crontab(hour="0", minute="0"))
def send_daily_layby_summary():
    users = User.objects.all()
    for user in users:
        laybys = LaybyService.get_user_laybys(user)
        if laybys.exists():
            LaybyService.notify_layby_summary(user, laybys)


@task()
def notify_layby_completion(layby_id):
    layby = LaybyService.get_layby(layby_id)
    if layby and layby.is_complete:
        LaybyService.notify_layby_completion(layby.user, layby)
