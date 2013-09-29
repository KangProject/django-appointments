from django.db.models.signals import pre_save

from models import Event, Calendar


def optional_calendar(sender, **kwargs):
    event = kwargs.pop('instance')

    if isinstance(event, Event):
        try:
            calendar = Calendar._default_manager.get(name='default')
        except Calendar.DoesNotExist:
            calendar = Calendar(name='default', slug='default')
            calendar.save()

        event.calendar = calendar

    return True

pre_save.connect(optional_calendar)
