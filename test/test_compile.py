

def test_compile():
    try:
        import tiddlywebplugins.tank
        assert True
    except ImportError as exc:
        assert False, exc
