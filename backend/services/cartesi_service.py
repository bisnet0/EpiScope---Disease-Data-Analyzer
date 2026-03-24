import requests
import json

CARTESI_INSPECT_URL = "http://localhost:8080/inspect"


def verify_ledger_on_chain(payload):
    payload_hex = "0x" + json.dumps(payload).encode("utf-8").hex()
    return payload_hex
