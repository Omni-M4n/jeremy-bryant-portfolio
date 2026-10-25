"""Read a tiny synthetic packet extract; never capture traffic or infer loss counts."""
from pathlib import Path
import re
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from foundation_runtime import main, require

LAB_ID = "network-loss-diagnosis"
ROOT = Path(__file__).resolve().parent


def fields(value, names):
    require(isinstance(value, dict) and set(value) == set(names.split()), "unexpected fields")


def whole(value, maximum=10000000):
    require(type(value) is int and 0 <= value <= maximum, "invalid nonnegative whole number")


def analyse(case):
    require(case.get("artifacts") == {}, "Use data.packets as the only packet evidence; artifacts must be empty. Prepare a fresh case and preserve the older attempt.")
    data = case["data"]
    fields(data, "client_start server_start request_bytes capture_drops packets")
    for key in ("client_start", "server_start", "request_bytes"):
        whole(data[key])
    require(data["request_bytes"] > 0 and data["client_start"] + data["request_bytes"] <= 10000000, "invalid request boundary")
    require(data["capture_drops"] is None or type(data["capture_drops"]) is int, "drop count must be integer or null")
    if data["capture_drops"] is not None:
        whole(data["capture_drops"])
    require(isinstance(data["packets"], list) and 1 <= len(data["packets"]) <= 60, "one to sixty packet rows required")
    starts = {"client": data["client_start"], "server": data["server_start"]}
    ranges = {"client": [], "server": []}
    repeats, unseen, reset, seen = [], [], False, set()
    previous, acknowledged, response = -1, None, None
    for row in data["packets"]:
        fields(row, "id at_ms side kind seq length ack")
        require(isinstance(row["id"], str) and re.fullmatch(r"f[0-9]{2}", row["id"]) and row["id"] not in seen, "unique neutral frame ID required")
        seen.add(row["id"])
        whole(row["at_ms"])
        require(row["at_ms"] >= previous and not reset, "out-of-order time or packets after reset outside this model")
        previous = row["at_ms"]
        require(row["side"] in starts and row["kind"] in {"data", "ack", "reset"}, "unsupported side or packet kind")
        whole(row["length"], 65535)
        if row["kind"] == "data":
            whole(row["seq"])
            require(row["ack"] is None and row["length"] > 0 and row["seq"] >= starts[row["side"]] and row["seq"] + row["length"] <= 10000000, "invalid data range")
            interval = (row["seq"], row["seq"] + row["length"])
            require(row["side"] != "client" or interval[1] <= starts["client"] + data["request_bytes"], "client data exceeds the one-request boundary")
            known = ranges[row["side"]]
            require(all(interval == old or interval[1] <= old[0] or interval[0] >= old[1] for old in known), "partial overlap is outside this extract model")
            if interval in known:
                repeats.append(row["id"])
            else:
                known.append(interval)
            if row["side"] == "server" and response is None:
                response = row["at_ms"]
        elif row["kind"] == "ack":
            whole(row["ack"])
            require(row["seq"] is None and row["length"] == 0, "invalid acknowledgement row")
            other = "server" if row["side"] == "client" else "client"
            require(row["ack"] >= starts[other], "acknowledgement predates supplied stream anchor")
            require(other != "client" or row["ack"] <= starts["client"] + data["request_bytes"], "acknowledgement exceeds the one-request boundary")
            contiguous = starts[other]
            for start, end in sorted(ranges[other]):
                if start > contiguous:
                    break
                contiguous = max(contiguous, end)
            if row["ack"] > contiguous:
                unseen.append(row["id"])
            if row["side"] == "server" and row["ack"] >= starts["client"] + data["request_bytes"] and acknowledged is None:
                acknowledged = row["at_ms"]
        else:
            require(row["seq"] is None and row["ack"] is None and row["length"] == 0, "invalid reset row")
            reset = True
    timing_known = acknowledged is not None and response is not None and response >= acknowledged
    timing = f"request-ack-to-response:{response - acknowledged}ms" if timing_known else "insufficient-timing-evidence"
    drops = data["capture_drops"]
    capture = "drop-count-unavailable" if drops is None else (f"capture-drops-reported:{drops}" if drops else "no-local-drops-reported")
    observations = ["Repeated exact ranges at: " + (", ".join(repeats) or "none") + ".", "Acknowledgements beyond contiguous captured bytes at: " + (", ".join(unseen) or "none") + "."]
    observations.append(f"Timing: request-ack={acknowledged}ms; first-response={response}ms; wait={response - acknowledged}ms." if timing_known else "Timing: complete request acknowledgement or following response absent.")
    return {"decisions": {"repetition": "repeated-range-observed" if repeats else "no-repeat-in-extract", "acknowledgement": "unseen-bytes-acknowledged" if unseen else "no-unseen-ack-in-extract", "termination": "reset-observed" if reset else "no-reset-in-extract", "timing": timing, "capture": capture}, "observations": observations, "limitations": ["Repeated bytes can reflect retransmission or duplicate capture; they do not prove packet loss or locate its cause. Acknowledged unseen bytes show incomplete observation, not that those bytes were lost in transit.", "The acknowledgement-to-response interval includes endpoint work and transport effects; it is not a pure application-delay or round-trip-time measurement. Reset origin and capture completeness need separate evidence."]}


if __name__ == "__main__":
    raise SystemExit(main(ROOT, LAB_ID, analyse))
