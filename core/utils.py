from decimal import Decimal, getcontext

# Set decimal precision globally
getcontext().prec = 8

def round_decimal(value, decimals=4):
    return Decimal(value).quantize(Decimal(10) ** -decimals)
