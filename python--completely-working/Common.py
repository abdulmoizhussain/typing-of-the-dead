def avg_of_difference(a, b, percent):
    return (a if a < b else b) + (abs(a - b) * percent)
