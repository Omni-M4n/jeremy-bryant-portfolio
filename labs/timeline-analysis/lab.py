"""Original fictional evidence analysis; no host inspection or network activity."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from foundation_runtime import main, require, validate_case

ROOT = Path(__file__).resolve().parent
LAB_ID = "timeline-analysis"

def exact(value, fields, label):
    require(isinstance(value, dict) and set(value) == set(fields), label + ": unsupported or missing fields")

def text(value, label):
    require(isinstance(value, str) and 0 < len(value) <= 300 and value.strip() == value, label + ": bounded nonempty text required")


from datetime import datetime, timedelta, timezone
import re

def stamp(value):
    require(isinstance(value, str) and re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}(?:Z|[+-](?:[01][0-9]|2[0-3]):[0-5][0-9])", value), "time requires seconds and an explicit UTC offset")
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)
    except (ValueError, OverflowError) as error:
        raise ValueError("invalid timestamp") from error

def fmt(value):
    return value.isoformat().replace("+00:00", "Z")

def analyse(case):
    validate_case(case, LAB_ID)
    data = case["data"]
    exact(data, ["events", "pairs"], "data")
    require(isinstance(data["events"], list) and 2 <= len(data["events"]) <= 30, "provide 2-30 events")
    intervals, observations = {}, []
    for event in data["events"]:
        exact(event, ["id", "time", "clock_offset_seconds", "uncertainty_seconds", "description"], "event")
        text(event["id"], "event ID")
        text(event["description"], "description")
        require(event["id"] not in intervals, "duplicate event ID")
        offset, uncertainty = event["clock_offset_seconds"], event["uncertainty_seconds"]
        require(type(offset) is int and -86400 <= offset <= 86400, "clock offset outside +/-86400 seconds")
        require(type(uncertainty) is int and 0 <= uncertainty <= 3600, "uncertainty outside 0-3600 seconds")
        try:
            center = stamp(event["time"]) - timedelta(seconds=offset)
            low, high = center - timedelta(seconds=uncertainty), center + timedelta(seconds=uncertainty)
        except OverflowError as error:
            raise ValueError("corrected timestamp outside supported range") from error
        intervals[event["id"]] = (low, high)
        observations.append(f'{event["id"]}: corrected UTC={fmt(center)}; possible interval=[{fmt(low)}, {fmt(high)}].')
    require(isinstance(data["pairs"], list) and 1 <= len(data["pairs"]) <= 50, "provide 1-50 comparisons")
    decisions = {}
    for pair in data["pairs"]:
        exact(pair, ["id", "left", "right"], "pair")
        text(pair["id"], "pair ID")
        require(pair["id"] not in decisions, "duplicate comparison ID")
        require(isinstance(pair["left"], str) and isinstance(pair["right"], str) and pair["left"] in intervals and pair["right"] in intervals and pair["left"] != pair["right"], "comparison needs two different known event IDs")
        left, right = intervals[pair["left"]], intervals[pair["right"]]
        result = "definitely-before" if left[1] < right[0] else "definitely-after" if left[0] > right[1] else "order-uncertain"
        decisions[pair["id"]] = result
        observations.append(f'{pair["id"]}: compare {pair["left"]} with {pair["right"]}; interval result={result}.')
    return {"decisions": decisions, "observations": observations, "limitations": [
        "A positive clock offset means the device clock is fast and is subtracted after UTC normalisation. The supplied uncertainty is a bound, not a probability.",
        "Overlapping or touching intervals, including identical timestamps, cannot establish strict ordering. Even separated intervals do not establish causation.",
        "The model assumes supplied offset and uncertainty estimates are valid; collection delay, timestamp granularity and omitted events need separate investigation."]}

if __name__ == "__main__":
    raise SystemExit(main(ROOT, LAB_ID, analyse))
