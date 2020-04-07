from django.forms import MultiValueField, IntegerField
from django.forms.widgets import MultiWidget, NumberInput

# CLASSES
class HourMinute:
    KEY_HOUR: str = "hour"
    KEY_MINUTE: str = "minute"
    DEFAULT_HOUR : int = 12
    DEFAULT_MINUTE : int = 0

    def __init__(self, hour=DEFAULT_HOUR, minute=DEFAULT_MINUTE):
        self.hour = hour
        self.minute = minute

    def to_json(self) -> dict:
        return { HourMinute.KEY_HOUR: self.hour, HourMinute.KEY_MINUTE: self.minute }


# WIDGETS
class InputHourMinuteWidget(MultiWidget):
    """This widget allows the user to fill in a hour and a minute.
    """

    def __init__(self, attrs=None):
        # Here we will use two `Select` widgets, one for hour and one for minutes
        widgets = [
            NumberInput(attrs=attrs),
            NumberInput(attrs=attrs)
        ]
        super(InputHourMinuteWidget, self).__init__(widgets, attrs)

    def decompress(self, value):
        """ Split the widget value into subwidgets values.
        """
        if value:
            return [int(value[HourMinute.KEY_HOUR]), int(value[HourMinute.KEY_MINUTE])]
        else:
            return [HourMinute.DEFAULT_HOUR, HourMinute.DEFAULT_MINUTE]



# FIELDS
class HourMinuteField(MultiValueField):
    widget = InputHourMinuteWidget()

    def __init__(self, **kwargs):
        # Define one message for all fields.
        error_messages = {
            'incomplete': 'Enter the hour and the minute.',
        }
        # Or define a different message for each field.
        fields = (
            IntegerField(
                error_messages={'incomplete': 'Enter hour.'},
                min_value=0,
                max_value=23,
                initial=HourMinute.DEFAULT_HOUR
            ),
            IntegerField(
                error_messages={'incomplete': 'Enter minute.'},
                min_value=0,
                max_value=59,
                initial=HourMinute.DEFAULT_MINUTE
            )
        )

        super().__init__(error_messages=error_messages, fields=fields,require_all_fields=True, **kwargs)


    def compress(self, data_list):
        return HourMinute(data_list[0], data_list[1])
        # return {"hour": data_list[0], "minute": data_list[1]}

