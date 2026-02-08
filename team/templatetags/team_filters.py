from django import template

register = template.Library()

# Team color mapping based on team name - uses vibrant palette
TEAM_COLORS = {
    # Light blue, Dark blue, Red/Coral, Orange/Peach palette
    'kirmizi': {
        'bg': 'bg-gradient-to-r from-red-200 via-red-50 to-slate-50',
        'banner': 'bg-gradient-to-r from-red-200  to-red-300',
        'border': 'border-red-400',
        'text': 'text-red-900',
        'badge': 'bg-red-500',
        'light': 'bg-red-100',
    },
    'mavi': {
        'bg': 'from-sky-200 to-sky-300 bg-gradient-to-r',
        'border': 'border-sky-400',
        'text': 'text-sky-900',
        'badge': 'bg-sky-500',
        'light': 'bg-sky-100',
    },
    'sarı': {
        'bg': 'from-orange-200 to-orange-300 bg-gradient-to-r',
        'border': 'border-orange-400',
        'text': 'text-orange-900',
        'badge': 'bg-orange-400',
        'light': 'bg-orange-100',
    },
    'yeşil': {
        'bg': 'from-green-200 to-green-300 bg-gradient-to-r',
        'border': 'border-slate-600',
        'text': 'text-slate-900',
        'badge': 'bg-slate-600',
        'light': 'bg-slate-100',
    },
    'siyah': {
        'bg': 'bg-[#1A1A1A]',
        'border': 'border-slate-600',
        'text': 'text-slate-900',
        'badge': 'bg-slate-700',
        'light': 'bg-slate-100',
    },
    'beyaz': {
        'bg': 'bg-white',
        'banner': 'bg-gradient-to-r from-white to-slate-100',
        'border': 'border-slate-300',
        'text': 'text-slate-900',
        'badge': 'bg-slate-600',
        'light': 'bg-slate-50',
    },
    'turuncu': {
        'bg': 'bg-gradient-to-r from-orange-200 via-orange-50 to-slate-50',
        'banner': 'bg-gradient-to-r from-orange-200 to-orange-300',
        'border': 'border-orange-400',
        'text': 'text-orange-900',
        'badge': 'bg-orange-400',
        'light': 'bg-orange-100',
    },
    'mor': {
        'bg': 'bg-[#E0BBE4]',
        'border': 'border-red-400',
        'text': 'text-orange-900',
        'badge': 'bg-red-500',
        'light': 'bg-red-100',
    },
    'pembe': {
        'bg': 'bg-red-50',
        'border': 'border-red-400',
        'text': 'text-red-900',
        'badge': 'bg-red-500',
        'light': 'bg-red-100',
    },
}


@register.filter
def team_color_class(team_name, color_type='bg'):
    """
    Get team color class based on team name.
    
    Usage: {{ training.team.name|team_color_class }} or {{ training.team.name|team_color_class:'badge' }}
    """
    if not team_name:
        return 'bg-gray-50'
    
    team_key = team_name.lower().strip()
    colors = TEAM_COLORS.get(team_key, {'bg': 'bg-gray-50', 'border': 'border-gray-200', 'text': 'text-gray-800', 'badge': 'bg-gray-500', 'light': 'bg-gray-100'})
    
    return colors.get(color_type, colors['bg'])


@register.filter
def team_color_dict(team_name):
    """
    Get all color classes for a team as a dictionary.
    
    Usage: {% with colors=training.team.name|team_color_dict %}
    """
    if not team_name:
        return TEAM_COLORS.get('default', {'bg': 'bg-gray-50', 'border': 'border-gray-200', 'text': 'text-gray-800', 'badge': 'bg-gray-500', 'light': 'bg-gray-100'})
    
    team_key = team_name.lower().strip()
    return TEAM_COLORS.get(team_key, {'bg': 'bg-gray-50', 'border': 'border-gray-200', 'text': 'text-gray-800', 'badge': 'bg-gray-500', 'light': 'bg-gray-100'})


@register.filter
def get_item(value, key):
    if isinstance(value, dict):
        return value.get(key)
    return None
