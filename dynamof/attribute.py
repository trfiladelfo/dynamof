
from dynamof.core.utils import merge, find
from dynamof.core.model import Attr, Condition, Function


# condition and
def cand(*conditions):
    def build(attrs):
        return ' AND '.join([f'({cond.expression(attrs)})' for cond in conditions])
    attributes = merge([cond.attributes for cond in conditions])
    return Condition(build, attributes)

# condition or
def cor(*conditions):
    def build(attrs):
        return ' OR '.join([f'({cond.expression(attrs)})' for cond in conditions])
    attributes = merge([cond.attributes for cond in conditions])
    return Condition(build, attributes)


class AttrFunc:

    def __init__(self):
        pass

    def __call__(self, name):

        def find_attr(attrs, original_name=name):
            return find(attrs, lambda a: a.get('original') == original_name)

        def equals(value):
            def build(attrs):
                a = find_attr(attrs)
                return f'{a.alias} = {a.key}'
            return Condition(build, { name: value })

        def greater_than(value):
            def build(attrs):
                a = find_attr(attrs)
                return f'{a.alias} > {a.key}'
            return Condition(build, { name: value })

        def less_than(value):
            def build(attrs):
                a = find_attr(attrs)
                return f'{a.alias} < {a.key}'
            return Condition(build, { name: value })

        def less_than_or_equal(value):
            def build(attrs):
                a = find_attr(attrs)
                return f'{a.alias} <= {a.key}'
            return Condition(build, { name: value })

        def greater_than_or_equal(value):
            def build(attrs):
                a = find_attr(attrs)
                return f'{a.alias} >= {a.key}'
            return Condition(build, { name: value })

        def between(value_a, value_b):
            value_a_key = f'{name}_a'
            value_b_key = f'{name}_b'
            def build(attrs):
                a = find_attr(attrs)
                value_a_attr = find_attr(attrs, original_name=value_a_key)
                value_b_attr = find_attr(attrs, original_name=value_b_key)
                return f'{a.alias} BETWEEN {value_a_attr.key} AND {value_b_attr.key}'
            return Condition(build, {
                value_a_key: value_a,
                value_b_key: value_b
            })

        return Attr(equals, greater_than, less_than, less_than_or_equal, greater_than_or_equal, between)

    @classmethod
    def append(cls, *values):
        """Generates a function that will tell the builder the correct format
        for list appending for a specific item. The full update expression would
        look like...
            UpdateExpression="SET some_attr = list_append(some_attr, :i)"
        """
        def expression(a_attr):
            return f'{a_attr.alias} = list_append({a_attr.alias}, {a_attr.key})'

        def value():
            return list(values)

        return Function(expression, value)

    @classmethod
    def prepend(cls, *values):
        """Same as append - in reverse"""
        def expression(a_attr):
            return f'{a_attr.alias} = list_append({a_attr.key}, {a_attr.alias})'

        def value():
            return list(values)

        return Function(expression, value)


# NOTE: Magic here!!!
# Because Attr implments __call__
# this makes it a special object data type that
# can both have properties and be called:
#
#   roles: attr.append('admin')
#
# and
#
#   condition: attr('sunshie').equals('sunshie')
#

attr = AttrFunc()
