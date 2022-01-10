from inspect import signature


def assert_param_counts(callback, count: int):
    # inspect callback object to ensure it takes specified number of parameters
    sig = signature(callback)
    assert len(sig.parameters) == count, "Callback signature must handle {} arguments".format(count)