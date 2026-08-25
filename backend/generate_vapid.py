#!/usr/bin/env python3
"""
Run once to generate VAPID keys for Web Push notifications.
Output goes into your .env file.

Usage:
    pip install pywebpush
    python generate_vapid.py
"""
from pywebpush import Vapid

v = Vapid()
v.generate_keys()

print("Add these to your .env file:\n")
print(f"VAPID_PRIVATE_KEY={v.private_key}")
print(f"VAPID_PUBLIC_KEY={v.public_key}")
print(f'VAPID_CLAIM_EMAIL=your@email.com')
