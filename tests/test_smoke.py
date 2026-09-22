def test_basilisk_imports():
    from Basilisk.simulation import spacecraft
    assert spacecraft.Spacecraft() is not None
