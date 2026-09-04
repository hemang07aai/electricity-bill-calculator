# backend.py
# Hashing, bill calculation, helpers

import hashlib
import random
import datetime
from typing import Tuple

def hash_password(password: str) -> str:
    """Return SHA-256 hex digest for password (simple, no extra packages)."""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

def verify_password(password: str, password_hash: str) -> bool:
    return hash_password(password) == password_hash

def calculate_bill(units: float, customer_type: str) -> Tuple[float,float,float,float]:
    """
    Slab rates example; returns (energy_charge, fixed_charge, gst, total)
    """
    units = float(units) if units else 0.0
    if customer_type.lower() == "domestic":
        if units <= 100:
            energy = float(units) * 1.5
        elif units <= 200:
            energy = 100 * 1.5 + (float(units) - 100) * 2.5
        elif units <= 500:
            energy = 100 * 1.5 + 100 * 2.5 + (float(units) - 200) * 4.0
        else:
            energy = 100 * 1.5 + 100 * 2.5 + 300 * 4.0 + (float(units) - 500) * 6.0
        fixed = 50.0
    else:
        # commercial
        if units <= 100:
            energy = float(units) * 3.5
        elif units <= 200:
            energy = 100 * 3.5 + (float(units) - 100) * 5.0
        elif units <= 500:
            energy = 100 * 3.5 + 100 * 5.0 + (float(units) - 200) * 6.5
        else:
            energy = 100 * 3.5 + 100 * 5.0 + 300 * 6.5 + (float(units) - 500) * 7.5
        fixed = 100.0

    gst = energy * 0.18
    total = energy + fixed + gst
    # Round
    return round(energy,2), round(fixed,2), round(gst,2), round(total,2)

def new_bill_number() -> str:
    return f"BILL{random.randint(10000, 99999)}"

def make_bill(customer_name: str, customer_type: str, units: float, status: str = "Unpaid") -> dict:
    energy, fixed, gst, total = calculate_bill(units, customer_type)
    bill_no = new_bill_number()
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return {
        "bill_no": bill_no,
        "customer_name": customer_name,
        "customer_type": customer_type,
        "units": units,
        "energy_charge": energy,
        "fixed_charge": fixed,
        "gst": gst,
        "total": total,
        "status": status,
        "created_at": now
    }
