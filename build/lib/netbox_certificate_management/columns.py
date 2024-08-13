import django_tables2 as tables
from django.utils.safestring import mark_safe

class ColorStatusColumn(tables.Column):
    """
    Display a value with dynamic background color based on its value.
    """
    def __init__(self, *args, **kwargs):
        self.thresholds = kwargs.pop('thresholds', {})
        super().__init__(*args, **kwargs)

    def render(self, value):
        color = self.get_color(value)
        if(color):
            return mark_safe(
                f'<span class="badge" style="background-color: {color}; color: white">{value}</span>'
            )
        else: return value

    def get_color(self, value):
        """
        Determine the color based on the value. Modify this method to fit your needs.
        """
        if value <= self.thresholds.get('critical', 26):
            return 'red'
        else:
            return None
