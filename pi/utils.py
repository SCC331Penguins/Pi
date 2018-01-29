def typeCheck(var, reqType):
    if(not isinstance(var, reqType)):
        raise TypeError('Invalid Type')
    return True
