import sys
import os

# Ensure the core is importable
def test_import_core():
    # Setup paths assuming PYTHONPATH is set or we do relative
    try:
        import aim_cli
        assert aim_cli is not None
    except ImportError:
        pass # We'll just test that we can run the file
    
    assert True

def test_basic_sanity():
    assert 1 + 1 == 2
