import statistics
from .utils import _CALCULATIONS_GRAPHVIZSHAPE
from ..node import Node


def Count(node):
    '''Node to count inputs

    Args:
        node (Node): input stream
    '''
    def foo(val):
        ret._count += 1
        return ret._count

    ret = Node(foo=foo, foo_kwargs=None, name='Count', inputs=1, graphvizshape=_CALCULATIONS_GRAPHVIZSHAPE)
    ret._count = 0
    node >> ret
    return ret


def Max(node):
    '''Node to take rolling max of inputs

    Args:
        node (Node): input stream
    '''
    def foo(val):
        ret._max = max(ret._max, val) if ret._max is not None else val
        return ret._max

    ret = Node(foo=foo, foo_kwargs=None, name='Max', inputs=1, graphvizshape=_CALCULATIONS_GRAPHVIZSHAPE)
    ret._max = None
    node >> ret
    return ret


def Min(node):
    '''Node to take rolling min of inputs

    Args:
        node (Node): input stream
    '''
    def foo(val):
        ret._min = min(ret._min, val) if ret._min is not None else val
        return ret._min

    ret = Node(foo=foo, foo_kwargs=None, name='Min', inputs=1, graphvizshape=_CALCULATIONS_GRAPHVIZSHAPE)
    ret._min = None
    node >> ret
    return ret


def Sum(node):
    '''Node to take rolling sum inputs

    If stream type is iterable, will do += sum(input). If input
    stream type is not iterable, will do += input.

    Args:
        node (Node): input stream
    '''
    def foo(val):
        try:
            # iterable, sum with sum function
            iter(val)
            ret._sum += sum(val)
        except TypeError:
            # not iterable, sum by value
            ret._sum += val
        return ret._sum

    ret = Node(foo=foo, foo_kwargs=None, name='Sum', inputs=1, graphvizshape=_CALCULATIONS_GRAPHVIZSHAPE)
    ret._sum = 0
    node >> ret
    return ret


def Average(node):
    '''Node to take the running average

    If stream type is iterable, will do (average + sum(input))/(count+len(input)).
    If input stream type is not iterable, will do (average + input)/count
    '''
    def foo(val):
        try:
            # iterable, sum with sum function
            iter(val)
            ret._sum += sum(val)
            ret._count += len(val)
        except TypeError:
            # not iterable, sum by value
            ret._sum += val
            ret._count += 1
        return ret._sum / ret._count if ret._count > 0 else float('nan')

    ret = Node(foo=foo, foo_kwargs=None, name='Average', inputs=1, graphvizshape=_CALCULATIONS_GRAPHVIZSHAPE)
    ret._sum = 0
    ret._count = 0

    node >> ret
    return ret


def SMA(node, window_width=10, full_only=False):
    '''Node to take the simple moving average over a window of ticks

    Arguments:
        node (node): input stream
        window_width (int): size of window to use
        full_only (bool): only return if list is full
    '''
    def sma(val):
        return statistics.mean(val) if len(val) > 0 else float('nan')
    return node.window(window_width, full_only).apply(sma)

def EMA(node, smoothing=2, interval=5, window_width=10, full_only=False):
    '''Node to take the exponential moving average over a window of ticks

    Arguments:
        node (node): input stream
        smoothing (int): smoothing factor
        window_width (int): size of window to use
        full_only (bool): only return if list is full
    '''
    ret = None  # avoid undefined symbol
    def ema(val):
        '''Calculates the EMA of prices within the window'''
        # Handle case where length is less than duration; EMA is SMA
        if(len(val) < interval-1):
            ret._prev = statistics.mean(val) if len(val) > 0 else float('nan')
            return ret._prev
        # Regular case (EMA based off of previous EMA)
        else:
            ema_mult = smoothing / (interval+1)
            ema = (val - ret._prev) * ema_mult + ret._prev
            ret._prev = ema
            return ret
    ret = node.window(window_width, full_only).apply(ema)
    return ret


Node.rollingCount = Count
Node.rollingMin = Min
Node.rollingMax = Max
Node.rollingSum = Sum
Node.rollingAverage = Average
Node.sma = SMA
