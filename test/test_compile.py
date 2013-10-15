

def test_compile():
    try:
        import tiddlywebplugins.tank
        assert True
    except ImportError, exc:
        assert False, exc
