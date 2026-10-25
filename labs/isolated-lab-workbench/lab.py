"""Review supplied workbench evidence. Never inspect or change a real VM."""
from pathlib import Path
import re
import sys
from ipaddress import ip_address, ip_network

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from foundation_runtime import main, require, validate_case

ROOT = Path(__file__).resolve().parent
LAB_ID = "isolated-lab-workbench"
MODES = {"disabled", "not-attached", "nat", "nat-network", "bridged", "host-only", "internal"}
LIMITATIONS = [
    "This reviews fictional supplied records only; it does not inspect a hypervisor, verify real isolation or restore a VM.",
    "The boundary is one disconnected VM with a loopback-only service. Host-only and internal networks require a different authorised design; NAT can permit outbound access.",
    "Eight adapter records, guest addresses/routes and listed transfer settings support only the stated observation time. Missing devices, host routing, passthrough and later changes require manual review.",
    "A matching dummy-file hash demonstrates that file's supplied rollback evidence, not a full-system restore, backup quality or protection against malicious software."
]


def exact(value, fields, label):
    require(isinstance(value, dict) and set(value) == set(fields), label + ": missing or unsupported fields")


def text(value, label):
    require(isinstance(value, str) and 0 < len(value) <= 100 and value.strip() == value, label + ": bounded text required")


def boolean(value, label):
    require(type(value) is bool, label + ": boolean required")


def digest(value):
    require(value is None or isinstance(value, str) and re.fullmatch(r"[0-9a-f]{64}", value), "hash must be lowercase SHA-256 or null")


def analyse(case):
    validate_case(case, LAB_ID)
    data = case["data"]
    exact(data, ["boundary", "vm_id", "disposable", "adapters", "channels", "guest", "loopback", "restore"], "data")
    require(data["boundary"] == "disconnected-loopback", "unsupported boundary")
    text(data["vm_id"], "VM ID")
    boolean(data["disposable"], "disposable")
    adapters = data["adapters"]
    require(isinstance(adapters, list) and 0 <= len(adapters) <= 8, "provide at most eight adapter records")
    slots, connected = set(), []
    for adapter in adapters:
        exact(adapter, ["slot", "mode"], "adapter")
        slot = adapter["slot"]
        require(type(slot) is int and 1 <= slot <= 8 and slot not in slots, "invalid or duplicate adapter slot")
        require(isinstance(adapter["mode"], str) and adapter["mode"] in MODES, "unsupported adapter mode")
        slots.add(slot)
        if adapter["mode"] not in {"disabled", "not-attached"}:
            connected.append(slot)
    channels = data["channels"]
    exact(channels, ["shared_folders", "clipboard", "drag_drop", "passthrough"], "channels")
    require(type(channels["shared_folders"]) is int and 0 <= channels["shared_folders"] <= 20, "invalid shared folder count")
    for key in ("clipboard", "drag_drop", "passthrough"):
        boolean(channels[key], key)
    guest = data["guest"]
    exact(guest, ["default_routes", "non_loopback_addresses"], "guest")
    require(type(guest["default_routes"]) is int and 0 <= guest["default_routes"] <= 20, "invalid default route count")
    require(isinstance(guest["non_loopback_addresses"], list) and len(guest["non_loopback_addresses"]) <= 20, "invalid address inventory")
    for value in guest["non_loopback_addresses"]:
        require(isinstance(value, str), "address must be text")
        address = ip_address(value)
        require(not address.is_loopback, "non-loopback inventory contains a loopback address")
        require(address in ip_network("192.0.2.0/24") or address in ip_network("2001:db8::/32"), "use documentation addresses only")
    require(len(set(guest["non_loopback_addresses"])) == len(guest["non_loopback_addresses"]), "duplicate guest address")
    loop = data["loopback"]
    exact(loop, ["bind_address", "http_status", "body", "refused_after_stop"], "loopback")
    require(loop["bind_address"] is None or isinstance(loop["bind_address"], str) and loop["bind_address"] in {"127.0.0.1", "0.0.0.0"}, "unsupported listener address")
    require(loop["http_status"] is None or type(loop["http_status"]) is int and 100 <= loop["http_status"] <= 599, "invalid HTTP status")
    require(loop["body"] is None or isinstance(loop["body"], str) and len(loop["body"]) <= 100, "invalid response body")
    require(loop["refused_after_stop"] is None or type(loop["refused_after_stop"]) is bool, "invalid stopped-listener result")
    restore = data["restore"]
    exact(restore, ["snapshot_id", "snapshot_vm", "restored_id", "disk_mode", "baseline_sha256", "changed_sha256", "restored_sha256"], "restore")
    for key in ("snapshot_id", "snapshot_vm", "restored_id"):
        if restore[key] is not None:
            text(restore[key], key)
    require(isinstance(restore["disk_mode"], str) and restore["disk_mode"] in {"normal", "write-through"}, "unsupported disk mode")
    for key in ("baseline_sha256", "changed_sha256", "restored_sha256"):
        digest(restore[key])

    decisions = {"scope": "disposable-vm-recorded" if data["disposable"] else "stop-non-disposable"}
    missing = sorted(set(range(1, 9)) - slots)
    decisions["network"] = (
        "network-boundary-violated" if connected else
        "adapter-inventory-incomplete" if missing else
        "guest-evidence-conflicts" if guest["default_routes"] or guest["non_loopback_addresses"] else
        "disconnected-boundary-supported")
    active_channels = [key for key, value in channels.items() if value]
    decisions["host-paths"] = "host-transfer-path-present" if active_channels else "no-listed-host-transfer-path"
    decisions["connectivity"] = (
        "listener-binding-out-of-scope" if loop["bind_address"] == "0.0.0.0" else
        "loopback-evidence-incomplete" if any(value is None for value in loop.values()) else
        "loopback-positive-failed" if loop["http_status"] != 200 or loop["body"] != "BASELINE\n" else
        "loopback-stop-check-failed" if not loop["refused_after_stop"] else
        "loopback-pair-demonstrated")
    decisions["rollback"] = (
        "disk-outside-snapshot-model" if restore["disk_mode"] != "normal" else
        "restore-evidence-incomplete" if any(restore[key] is None for key in restore) else
        "snapshot-identity-mismatch" if restore["snapshot_vm"] != data["vm_id"] or restore["snapshot_id"] != restore["restored_id"] else
        "change-not-demonstrated" if restore["changed_sha256"] == restore["baseline_sha256"] else
        "restored-bytes-mismatch" if restore["restored_sha256"] != restore["baseline_sha256"] else
        "dummy-file-rollback-demonstrated")
    accepted = {"disposable-vm-recorded", "disconnected-boundary-supported", "no-listed-host-transfer-path", "loopback-pair-demonstrated", "dummy-file-rollback-demonstrated"}
    decisions["review"] = "supplied-evidence-complete" if all(value in accepted for value in decisions.values()) else "resolve-evidence-gaps"
    observations = [
        f'VM={data["vm_id"]}; recorded disposable={str(data["disposable"]).lower()}; boundary={data["boundary"]}.',
        f'Adapter slots missing={missing}; connected-mode slots={connected}; default routes={guest["default_routes"]}; non-loopback addresses={guest["non_loopback_addresses"]}.',
        f'Enabled listed host transfer paths={active_channels}.',
        f'Loopback bind={loop["bind_address"]}; HTTP={loop["http_status"]}; body={loop["body"]!r}; refused after stop={loop["refused_after_stop"]}.',
        f'Snapshot={restore["snapshot_id"]}; snapshot VM={restore["snapshot_vm"]}; restored snapshot={restore["restored_id"]}; disk mode={restore["disk_mode"]}.',
        f'Baseline SHA-256={restore["baseline_sha256"]}; changed={restore["changed_sha256"]}; restored={restore["restored_sha256"]}.'
    ]
    return {"decisions": decisions, "observations": observations, "limitations": list(LIMITATIONS)}


if __name__ == "__main__":
    raise SystemExit(main(ROOT, LAB_ID, analyse))
