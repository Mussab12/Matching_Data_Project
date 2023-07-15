from django import template

register = template.Library()


@register.filter
def arrayIndex(sequence, position):
    """
        Filter for get element by index in array
            :param sequence: array
            :param position:  int
    """
    return sequence[position]


@register.filter
def get_item(dictionary, key):
    """
        Filter for get element by key in dict
            :param dictionary: dict
            :param key:  key
    """
    return dictionary.get(key)


@register.filter
def sum_of_dict(data):
    """
        Filter for calculate the sum of dict
            :param data: dict
    """
    new_data_list = [data[item] for item in data]
    return sum(new_data_list)


@register.filter
def count_of_validPattern(data):
    """
        Get the count of valid Pattern
            :param data: array
    """
    valid_patterns = sum([item > 0 for item in data])
    return valid_patterns
