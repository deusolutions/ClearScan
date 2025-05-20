import pytest
from src import comparator

def test_compare_scans():
    old = {('10.0.0.1', 22, 'open'), ('10.0.0.2', 80, 'open')}
    new = {('10.0.0.1', 22, 'open'), ('10.0.0.3', 443, 'open')}
    added, removed = comparator.compare_scans(old, new)
    assert ('10.0.0.3', 443, 'open') in added
    assert ('10.0.0.2', 80, 'open') in removed
    assert ('10.0.0.1', 22, 'open') not in added
    assert ('10.0.0.1', 22, 'open') not in removed
