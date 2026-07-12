import sys
import os

def test_import_core():
    import aim_cli
    assert aim_cli is not None, "Failed to import aim_cli"

def test_doctor_exists():
    # Assert that aim_doctor.py exists in the .aim_core directory
    core_dir = os.path.dirname(os.path.abspath(__import__('aim_cli').__file__))
    doctor_path = os.path.join(core_dir, 'aim_doctor.py')
    assert os.path.exists(doctor_path), f"aim_doctor.py missing at {doctor_path}"
