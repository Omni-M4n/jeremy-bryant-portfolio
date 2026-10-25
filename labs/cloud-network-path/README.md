# Can traffic follow this cloud path?

A door can be unlocked while the road to it is closed. A private room can also be reached through a public reception desk. You will draw both the route and the rule checks for fictional network connections.

This extends [firewall-review](../firewall-review/README.md). The earlier lab checks rules that filter traffic. Here, you also check public addresses and routes for replies. You use a listed service that passes traffic onward. This is an extension to the earlier lab.

**Before you start:** firewall-review and network-address-path. Allow 30-40 minutes.

## Words used here

A **subnet** is a group of network addresses. A **route** says where traffic
goes next. **CIDR** is a way to write an address range. For example,
10.44.1.0/24 names a range, while /32 names one address. A **port** names
an entry point for a service. A **security group** is a set of rules that
allow traffic. An **internet gateway** links a cloud network to the internet.
A **relay** accepts one connection and makes a second connection onward.

## Set up a first attempt

Use Python 3.10 or newer, already on your computer. It works on Windows,
macOS or Linux. You need no extra packages, cloud account or network link.
A terminal is where you type commands. From the project folder, open one in
`labs/cloud-network-path`. The commands use `python`. If your Python 3
command has a different name, use that name.

```text
python --version
python lab.py cases
python lab.py prepare --scenario guided --out run/attempt-01
python lab.py show --case run/attempt-01/case.json
```

Read the small JSON file. JSON stores values with names. Here, `true` means
yes, `false` means no, and `null` means no value was given. Predict each
result first. Save it in `run/attempt-01/answers.json`. Fill in each decision
and explain why. List the record IDs in `evidence`. An ID is a record's name.
Keep this first attempt.

Run these commands only after you save your prediction.

```text
python lab.py analyse --case run/attempt-01/case.json
python lab.py check --case run/attempt-01/case.json --answers run/attempt-01/answers.json
python test_lab.py
python lab.py verify
```

The check looks at your answer words and checks that written fields are
filled in. A person must still review your reasons. Exit codes show how a
command ended. Code 0 means success. Code 1 means a mismatch or an unfinished
worksheet. Code 2 means the input is not valid. The `verify` command checks
the supplied cases. It does not score your work. These commands stay on your
computer and do not contact a cloud service.

Prepare `changed` in `run/attempt-02`. Prepare `challenge` in
`run/attempt-03`. Edit only these copies. Use a new output folder each time
so you keep each earlier attempt. To undo an edit, prepare a fresh copy.
Keep your evidence until someone reviews it. Later, remove only the named
practice folder you made. Never put personal records in it.


## Exact model

The input lists `endpoints`, `relays` and `requests`. An endpoint is one end
of a connection. It has private/public addresses, its subnet, return `routes`
and `inbound` rules. Inbound means traffic coming in. Each route has a `cidr`
and `target`. The target is local, igw (internet gateway) or blackhole (unusable).
Each inbound rule has a source `cidr` and TCP `port`. TCP is the network
protocol used here. A relay names `via`, `listen`, `target` and onward `port`.
A request gives `source`, `target`, `port` and, if needed, `via`.

Private addresses must be in 10.44.0.0/16. Public addresses must be ones set
aside for examples. For a direct request from outside, the target needs a
public address. Next, choose the most specific return route to the source.
This is the matching route with the narrowest address range. It must be igw
for an external source, or local for an internal source. Last, an inbound
allow rule must match both source and port.

The helper reports the first failed check. The answer is `no-public-address`,
`return-route-missing`, or `inbound-not-allowed`. If all three pass, use
`reachable-in-model`.

A relay request needs both parts of its path to pass. Each part is called
a leg. The second leg's source is the relay's private address. Success gives
`reachable-via-relay`. A failure starts with `relay-leg-1:` or `relay-leg-2:`,
then names the failed check.

Use only relay mappings listed in the input. A mapping says where to send
traffic. Each relay listener can have just one mapping. Each combination of
`via`, `target` and onward `port` must also have just one mapping. This stops
a request from matching two different listeners.

Assume an external source can reach the gateway. Assume internal routes
and outbound rules allow each connection. Also assume replies to established
connections are allowed. The model checks the return route at the target.
It does not work out routes at the source.

The helper rejects repeated route destinations, even if written in different
ways, such as /0 and /0.0.0.0. It rejects other unsupported inputs too.
A more specific blackhole route can take priority over a broader usable route.

## Small operation

Make a new guided copy. Remove only e1's default igw route. Predict the new
path table. Draw the route that is now missing. To restore the original,
prepare a fresh copy. This changes no host firewall or network setting.

## Evidence and handover

Save a diagram of the whole path. Label its addresses and ports.
Keep a table of paths that pass or fail, and the route chosen for each request.
Save your edits to copied rules. In your handover, list assumptions you have
not tested. State what you would need to observe in a real network before
you could say a connection works.

Label the stage of your work. Was it a first attempt, done with prompts,
checked on your own, or recalled later? A matching answer alone does not
show that you have learnt the skill or used a real cloud tool.

## Limits and sources

This model leaves out IPv6, another form of IP address. It leaves out NAT
gateways, which change addresses, and DNS, which looks up names. It does not
check network ACLs (access rules), host firewalls or an app's sign-in checks.
It does not send real packets. A reachable result depends on the assumptions
above. A private address alone does not settle every possible path.

The authors opened these source documents when they prepared this lab.
The helper uses the rules above. The sources explain how real services work.

- [AWS internet gateway](https://docs.aws.amazon.com/vpc/latest/userguide/VPC_Internet_Gateway.html) - direct IPv4 internet access uses public addressing and gateway routing.
- [AWS subnet route tables](https://docs.aws.amazon.com/vpc/latest/userguide/subnet-route-tables.html) - the most specific matching route is selected.
- [AWS security groups](https://docs.aws.amazon.com/vpc/latest/userguide/vpc-security-groups.html) - source, protocol and port rules control permitted traffic.
