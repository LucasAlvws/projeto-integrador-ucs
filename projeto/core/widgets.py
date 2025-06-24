from django import forms
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

class PeriodicityWidget(forms.MultiWidget):
    def __init__(self, attrs=None):
        widgets = [
            forms.NumberInput(attrs={'placeholder': _('Years'), 'min': '0', 'style': 'width: 80px;'}),
            forms.NumberInput(attrs={'placeholder': _('Months'), 'min': '0', 'style': 'width: 80px;'}),
            forms.NumberInput(attrs={'placeholder': _('Weeks'), 'min': '0', 'style': 'width: 80px;'}),
            forms.NumberInput(attrs={'placeholder': _('Days'), 'min': '0', 'style': 'width: 80px;'}),
        ]
        super().__init__(widgets, attrs)

    def decompress(self, value):
        if value:
            # Convert days back to years, months, weeks, days
            days = int(value)
            years = days // 365
            remaining_days = days % 365
            months = remaining_days // 30
            remaining_days = remaining_days % 30
            weeks = remaining_days // 7
            final_days = remaining_days % 7
            return [years, months, weeks, final_days]
        return [0, 0, 0, 0]

    def value_from_datadict(self, data, files, name):
        values = super().value_from_datadict(data, files, name)
        if values:
            years, months, weeks, days = [int(v) if v else 0 for v in values]
            total_days = years * 365 + months * 30 + weeks * 7 + days
            return total_days
        return 0

    def render(self, name, value, attrs=None, renderer=None):
        if self.is_localized:
            for widget in self.widgets:
                widget.is_localized = self.is_localized
        
        # value is a list of values, each corresponding to a widget
        # in self.widgets.
        if not isinstance(value, list):
            value = self.decompress(value)
        
        output = []
        final_attrs = self.build_attrs(attrs)
        id_ = final_attrs.get('id')
        
        for i, widget in enumerate(self.widgets):
            try:
                widget_value = value[i]
            except IndexError:
                widget_value = None
            
            if id_:
                final_attrs = dict(final_attrs, id='%s_%s' % (id_, i))
            
            widget_name = '%s_%s' % (name, i)
            rendered = widget.render(widget_name, widget_value, final_attrs, renderer)
            
            # Add labels for each field
            labels = [_('Years'), _('Months'), _('Weeks'), _('Days')]
            label_html = f'<label style="display: block; margin-bottom: 5px; font-weight: bold;">{labels[i]}:</label>'
            
            output.append(f'<div style="display: flex; flex-direction: column; margin-right: 15px;">{label_html}{rendered}</div>')
        
        return mark_safe('<div style="display: flex; align-items: flex-start;">' + ''.join(output) + '</div>')
