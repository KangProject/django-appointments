from django import template
from schedule.models import Calendar

register = template.Library()

class CalendarNode(template.Node):
    def __init__(self, content_object, distinction, context_var):
        self.content_object = template.Variable(content_object)
        self.distinction = distinction
        self.context_var = context_var
    
    def render(self, context):
        context[self.context_var] = Calendar.objects.get_calendar_for_object(self.content_object.resolve(context), self.distinction)
        return ''

def do_get_calendar_for_object(parser, token):
    if len(token.split_contents()) == 4:
        tag_name, content_object, _, context_var = token.split_contents()
        distinction = None
    elif len(token.split_contents()) == 5:
        tag_name, content_object, distinction, _, context_var = token.split_contents()
    else:
        raise template.TemplateSyntaxError, "%r tag follows form <tag_name> <content_object> as <context_var>" % token.contents.split()[0]
    return CalendarNode(content_object, distinction, context_var)
    
register.tag('get_calendar_for_object', do_get_calendar_for_object)