from decimal import Decimal
from django import template

register = template.Library()


@register.filter(name='indian_currency')
def indian_currency(value):
    """
    Formats a number or Decimal in Indian numbering style with ₹ symbol.
    Example: 125000 -> ₹1,25,000.00
    """
    if value is None or value == '':
        return '₹0.00'

    try:
        d_val = Decimal(str(value))
    except Exception:
        return f'₹{value}'

    is_negative = d_val < 0
    d_val = abs(d_val)

    # Format to 2 decimal places
    s = f"{d_val:.2f}"
    parts = s.split('.')
    int_part = parts[0]
    dec_part = parts[1]

    if len(int_part) <= 3:
        formatted_int = int_part
    else:
        last3 = int_part[-3:]
        rest = int_part[:-3]
        # Group rest by 2s from right
        groups = []
        while len(rest) > 2:
            groups.insert(0, rest[-2:])
            rest = rest[:-2]
        if rest:
            groups.insert(0, rest)
        formatted_int = ','.join(groups) + ',' + last3

    prefix = '-₹' if is_negative else '₹'
    return f"{prefix}{formatted_int}.{dec_part}"
