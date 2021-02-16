

def usd(number, decimal_places=2):
    """Return a properly formatted USD currency figure.

    """
    if number >= 0:
        return f'${number:.{decimal_places}f}'
    else:
        return f'-${abs(number):.{decimal_places}f}'