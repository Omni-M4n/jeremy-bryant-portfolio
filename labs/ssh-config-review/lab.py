"""Original fictional evidence analysis; no host inspection or network activity."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from foundation_runtime import main, require, validate_case

ROOT = Path(__file__).resolve().parent
LAB_ID = "ssh-config-review"

def exact(value, fields, label):
    require(isinstance(value, dict) and set(value) == set(fields), label + ": unsupported or missing fields")

def text(value, label):
    require(isinstance(value, str) and 0 < len(value) <= 300 and value.strip() == value, label + ": bounded nonempty text required")


SUPPORTED = {
    "permitrootlogin": {"yes", "no", "prohibit-password", "forced-commands-only"},
    "passwordauthentication": {"yes", "no"},
    "kbdinteractiveauthentication": {"yes", "no"},
    "pubkeyauthentication": {"yes", "no"},
    "permitemptypasswords": {"yes", "no"},
    "maxauthtries": None,
}
BASELINE = {"permitrootlogin": "no", "passwordauthentication": "no", "kbdinteractiveauthentication": "no", "pubkeyauthentication": "yes", "permitemptypasswords": "no"}

def analyse(case):
    validate_case(case, LAB_ID)
    exact(case["data"], ["config"], "data")
    config = case["data"]["config"]
    require(isinstance(config, str) and 0 < len(config) <= 12000, "provide bounded config text")
    values, observations = {}, []
    for number, line in enumerate(config.splitlines(), 1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        parts = stripped.split()
        require(len(parts) == 2, f"line {number}: only plain keyword/value pairs are supported")
        key, value = parts[0].lower(), parts[1]
        require(key in SUPPORTED, f"line {number}: unsupported directive (including Match/Include)")
        if key == "maxauthtries":
            require(value.isascii() and value.isdigit() and 1 <= int(value) <= 100, "MaxAuthTries must be 1-100 in this model")
            value = str(int(value))
        else:
            require(value in SUPPORTED[key], f"line {number}: unsupported value")
        if key in values:
            observations.append(f'Line {number}: {key}={value} ignored by first-value rule; effective={values[key]}.')
        else:
            values[key] = value
            observations.append(f'Line {number}: {key}={value} is the first value.')
    require(bool(values), "at least one supported directive required")
    decisions = {}
    for key in SUPPORTED:
        if key not in values:
            result = "missing-explicit-setting"
        elif key == "maxauthtries":
            result = "matches-lab-baseline" if int(values[key]) <= 4 else "differs-from-lab-baseline"
        else:
            result = "matches-lab-baseline" if values[key] == BASELINE[key] else "differs-from-lab-baseline"
        decisions[key] = result
    methods = ("passwordauthentication", "kbdinteractiveauthentication", "pubkeyauthentication")
    if not all(key in values for key in methods):
        route = "insufficient-explicit-method-settings"
    elif values["pubkeyauthentication"] == "yes":
        route = "public-key-method-enabled"
    elif any(values[key] == "yes" for key in methods):
        route = "alternative-method-enabled"
    else:
        route = "no-supported-method-enabled"
    decisions["access-route"] = route
    observations.append(f'Supported authentication route={route}; enabling a method does not establish usable credentials or successful login.')
    return {"decisions": decisions, "observations": observations, "limitations": [
        "Only six explicit directives are modelled. Missing settings are unknown here; no version-specific defaults are assumed. Match, Include, unknown directives and complex syntax are rejected.",
        "The fictional baseline is PermitRootLogin no, PasswordAuthentication no, KbdInteractiveAuthentication no, PubkeyAuthentication yes, PermitEmptyPasswords no and MaxAuthTries 1-4. It is not a universal deployment recommendation.",
        "First occurrence wins for these supported directives. This text review is not sshd validation and cannot establish keys, PAM behaviour, network exposure or a working recovery login. No host configuration was read or changed."]}

if __name__ == "__main__":
    raise SystemExit(main(ROOT, LAB_ID, analyse))
