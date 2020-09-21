def equal(a, b):
    try:
        assert a == b
        print(a == b, 'T')
    except:
        print(a, '==', b, 'F')