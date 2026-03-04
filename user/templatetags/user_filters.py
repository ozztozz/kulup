from django import template

register = template.Library()

@register.filter
def get_day_name(day_number):
    """Convert day number to Turkish day name"""
    days = {
        1: 'Pazartesi',
        2: 'Salı',
        3: 'Çarşamba',
        4: 'Perşembe',
        5: 'Cuma',
        6: 'Cumartesi',
        7: 'Pazar',
    }
    return days.get(day_number, '')
