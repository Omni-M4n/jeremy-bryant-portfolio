# Security labs: a guide to the library

<!-- LAB_COUNTS_START -->
This release has **61 core labs** and **25 extensions**.
<!-- LAB_COUNTS_END -->

These guided exercises were prepared for Jeremy Bryant's learning portfolio.
The original set had 26 offline foundation labs and four hands-on tool labs.
The library has since grown. The data and stories are fictional: they were made
for practice. They are not university submissions or records of a real incident.

Start with the [practice guide](PRACTICE-GUIDE.md). It explains key words, short
sessions and what to save. The [full summer study plan](SUMMER-STUDY-PLAN.md)
covers all 86 packages in a checked order. It gives two flexible starting routes.
Its [JSON companion](SUMMER-STUDY-PLAN.json) lists the exact skills needed first
and session codes. You can also use the
[website study plan](https://jeremy-bryant.pages.dev/security-labs/study-plan/).
The plan records no completed learner attempts.

## The first six

| Lab | Question | Skill |
| --- | --- | --- |
| [DNS triage](dns-triage/README.md) | What happened to each name lookup? | Packet evidence and careful network diagnosis |
| [Login triage](login-triage/README.md) | Which events deserve further investigation? | Timelines, thresholds, context and escalation |
| [Access review](access-review/README.md) | Who needs which actions on which resources? | Least privilege and preserving necessary access |
| [HTTP log triage](http-triage/README.md) | What do web requests and responses actually show? | Web-log evidence, context and cautious escalation |
| [File integrity](file-integrity/README.md) | What changed, and was the change expected? | Hashes, baselines and change review |
| [Firewall review](firewall-review/README.md) | Which rule decides this packet? | Rule order, network boundaries and necessary traffic |

These were the first six labs in the library. They are useful topic guides.
For a starting route, use the study plan above. Start with one small task.
You do not need to finish a whole topic group in one sitting.

## The original twenty additional foundation labs

These twenty labs came after the first six. Each has guided, changed and
challenge cases. A case is one set of facts to work through. Start with its
README. This list shows what you can practise. It does not record work experience.

### Network investigation and testing

| Lab | Purpose |
| --- | --- |
| [Asset discovery and inventory](asset-discovery/README.md) | Compare a saved scan with the authorised asset inventory. |
| [TCP handshake investigation](tcp-handshake/README.md) | Distinguish a completed handshake, a reset and incomplete evidence. |
| [TLS certificate review](tls-review/README.md) | Check certificate evidence against the intended hostname and observation time. |
| [HTTP headers and cookies](http-header-review/README.md) | Review web response settings against the needs of a fictional application. |
| [Vulnerability prioritisation](vulnerability-prioritisation/README.md) | Explain which fictional findings need attention first using an explicit local rubric. |
| [Remediation and retesting](vulnerability-retest/README.md) | Decide whether a claimed fix is demonstrated, incomplete or cannot yet be tested. |
| [Email identity and message triage](email-triage/README.md) | Compare message identities and destinations with trusted receiving evidence. |

### Defensive operations and recovery

| Lab | Purpose |
| --- | --- |
| [Endpoint process investigation](endpoint-triage/README.md) | Use process relationships and approved activity to decide what deserves review. |
| [Scheduled task review](scheduled-task-review/README.md) | Compare recurring task settings and changes with authorised maintenance. |
| [Evidence timeline reconstruction](timeline-analysis/README.md) | Normalise event times and show where clock uncertainty limits ordering. |
| [Alert correlation and duplicate handling](alert-correlation/README.md) | Group related records without confusing duplicate alerts with separate incidents. |
| [Backup and recovery verification](backup-verification/README.md) | Check backup scope, freshness and restore evidence against stated recovery needs. |
| [Linux file permission review](linux-permissions/README.md) | Work out access from owner, group and other permission bits. |
| [SSH configuration review](ssh-config-review/README.md) | Evaluate a small supported configuration against stated administration requirements. |

### Cloud, identity and configuration

| Lab | Purpose |
| --- | --- |
| [Cloud storage exposure review](cloud-storage-review/README.md) | Reason about public exposure in a deliberately small fictional storage model. |
| [Joiner, mover and leaver access](identity-lifecycle/README.md) | Update access decisions when a person starts, changes duties or leaves. |
| [MFA and account recovery review](mfa-review/README.md) | Check enrolment and recovery evidence against explicit account requirements. |
| [Cloud audit-event investigation](cloud-audit-triage/README.md) | Reconstruct identity and configuration activity from saved audit events. |
| [Secret handling and exposure review](secret-handling/README.md) | Find fictional sensitive values in the wrong places and plan an appropriate response. |
| [Dependency inventory and advisory review](dependency-review/README.md) | Match a small inventory to fictional version-range advisories without assuming exploitability. |

## The original four hands-on tool labs

| Lab | Practical question | Separate tool |
| --- | --- | --- |
| [Traffic capture](traffic-capture/README.md) | Can I collect and explain the traffic from my own controlled requests? | Wireshark |
| [Web access control](burp-access-control/README.md) | Does the server check who may read each fictional record, before and after a fix? | Burp Suite Community |
| [Offline detection rule](snort-rule-testing/README.md) | Does one simple rule detect the chosen marker and reject near-misses? | Snort 3 |
| [Windows event investigation](windows-event-investigation/README.md) | Can I trace a harmless process chain from collected events without confusing reused process IDs? | Sysmon in a disposable Windows VM |

These four have their own commands, listed in each README. They include software
checks and fictional inputs. Full tool practice means using the named tool.
A supplied PCAP packet file or XML event file does not show a personal capture.
A test of the web app does not show that a learner used Burp by hand.

Read each README before setup. A website build does not install tools or monitor
the host computer. These materials do not record a reviewed solo tool attempt.
Later packages also include tool tasks. Check their setup and scope before use.

## Further core labs and extensions

The list below contains the checked additions in this release. An extension
adds practice to a named core lab. Use each README to check the setup and skills
it needs. The study plan places these packages in the full learning route.

<!-- ADDITIONS_START -->
### Network and DNS

| Kind | Package | Practice goal |
| --- | --- | --- |
| Core | [Map addresses, subnets and a packet's route](network-address-path/README.md) | Distinguish local-subnet delivery, gateway routing and name resolution; predict the next hop. |
| Core | [Read ARP and DHCP exchanges](arp-dhcp-evidence/README.md) | Explain address resolution and lease negotiation, and separate normal renewal from a missing step. |
| Extension | [Investigate DNS records and caching](dns-cache-records/README.md) | Explain alias chains, record purpose and cached/stale answers; this extends transaction matching into cache behaviour. |
| Extension | [Run a scoped Nmap service inventory](controlled-nmap/README.md) | Collect the scan personally, compare observed services with known listeners and state uncertainty in service labels. |
| Extension | [Test real firewall enforcement and rollback](firewall-enforcement/README.md) | Move from the packet simulator to actual connection outcomes, rule logging and safe rollback. |
| Core | [Check IPv4 and IPv6 exposure parity](ipv6-parity/README.md) | Recognise when an IPv4 restriction leaves a separate IPv6 path and verify both paths. |
| Extension | [Diagnose latency, loss and failed connections](network-loss-diagnosis/README.md) | Distinguish retransmission evidence, application delay and capture loss without assuming one root cause. |
| Core | [Review VPN routes and DNS scope](vpn-routing-review/README.md) | Explain full versus split routing and identify traffic or name queries outside the intended tunnel. |

### Windows, Linux and endpoint

| Kind | Package | Practice goal |
| --- | --- | --- |
| Core | [Build and verify a disposable lab workbench](isolated-lab-workbench/README.md) | Explain host/guest boundaries and prove that a harmless change can be rolled back. |
| Core | [Use shell commands for read-only troubleshooting](shell-troubleshooting/README.md) | Choose a relevant command, interpret its fields and explain why its output cannot establish malicious intent. |
| Extension | [Measure effective Windows file permissions](windows-acl/README.md) | Test inheritance and effective access with actual accounts; this adds Windows ACL behaviour beyond a small policy model. |
| Extension | [Trace Linux service identities and sudo scope](linux-service-identity/README.md) | Explain service accounts, privilege boundaries and when an administration command requires elevation. |
| Extension | [Apply and verify a lab patch with rollback](patch-rollback/README.md) | Confirm the actual installed version, service health and rollback path rather than relying on a success message. |
| Extension | [Inventory startup mechanisms beyond scheduled tasks](startup-surface/README.md) | Recognise several startup mechanisms and distinguish unexplained changes from authorised configuration. |
| Extension | [Configure and verify SSH key access in the lab](ssh-key-practice/README.md) | Move from configuration review to actual authentication evidence, permissions and recovery. |
| Core | [Create and verify a small endpoint baseline](endpoint-baseline/README.md) | Translate requirements into observable controls and document justified exceptions without assuming every restriction is beneficial. |

### Identity and cloud

| Kind | Package | Practice goal |
| --- | --- | --- |
| Core | [Map cloud shared responsibility and controls](shared-responsibility/README.md) | Allocate security and recovery tasks to the customer/provider and name what the service description does not settle. |
| Core | [Compare encryption, encoding, hashing and key recovery](encryption-key-recovery/README.md) | Choose the appropriate concept for integrity or confidentiality and demonstrate why missing a required key changes recoverability. |
| Extension | [Evaluate provider-style IAM policy precedence](iam-explicit-deny/README.md) | Reason about allow/deny precedence and resource scope in a richer policy model. |
| Core | [Trace temporary role credentials and expiry](temporary-credentials/README.md) | Distinguish a human identity from an assumed role, and explain expiry, delegation and session attribution. |
| Core | [Review resource ownership, cost controls and teardown](cloud-resource-lifecycle/README.md) | Identify unowned resources, missing expiry/ownership tags and incomplete teardown; distinguish a budget alert from an enforced spending cap. |
| Core | [Practise password-vault and recovery hygiene](password-vault-recovery/README.md) | Demonstrate unique generated credentials, recovery planning and safe handling of exported or backup data. |
| Extension | [Trace cloud network reachability](cloud-network-path/README.md) | Show how routing and filtering combine, including a private service reached through an unintended path. |
| Extension | [Enrol and recover a local training MFA account](mfa-hands-on/README.md) | Perform enrolment, successful/failed challenges and approved recovery; this adds observed lifecycle behaviour to review of enrolment flags. |

### Web and API

| Kind | Package | Practice goal |
| --- | --- | --- |
| Core | [Test session expiry and logout](session-lifecycle/README.md) | Determine whether logout and expiry invalidate a session at the server and whether legitimate login still works. |
| Extension | [Construct and trace an HTTP request](http-request-construction/README.md) | Relate URL components, method, headers, body and encoding to the server's recorded request; this adds request construction. |
| Core | [Explain and retest a simple SQL injection](local-sql-injection/README.md) | Explain the difference between data and query instructions, then demonstrate the provided parameterised fix. |
| Core | [Compare reflected text and safe output encoding](local-output-encoding/README.md) | Explain why an untrusted value rendered as markup/script differs from escaped text, and verify the supplied fix. |
| Core | [Test a state-changing request's CSRF protection](csrf-local/README.md) | Explain ambient session use, anti-CSRF validation and why the intended request must remain usable. |
| Core | [Validate API input and error handling](api-schema-validation/README.md) | Separate validation failures from server errors and check that error responses avoid exposing internals. |
| Core | [Test a small request limit without load testing](rate-limit-lab/README.md) | Measure threshold/reset behaviour and legitimate recovery while recognising that a local demonstration does not establish production capacity. |
| Core | [Review upload validation and path containment](file-upload-path/README.md) | Check filename, file-type and storage-path handling, then verify that the supplied fix preserves allowed uploads. |

### Logs, SOC and incident response

| Kind | Package | Practice goal |
| --- | --- | --- |
| Core | [Import and normalise logs into a small local workspace](log-ingestion/README.md) | Map timestamps and fields, identify malformed rows and verify record counts before investigating. |
| Extension | [Build a small SOC query workbook](soc-query-workbook/README.md) | Write filters, counts and joins that answer explicit investigation questions without double-counting alerts. |
| Core | [Write a small auditable Python log helper](python-log-helper/README.md) | Validate inputs, handle a malformed record and compute a reproducible count or timeline rather than copying opaque code. |
| Extension | [Evaluate a detection against a labelled benign corpus](detection-corpus/README.md) | Move beyond one marker exercise to measure false positives/misses and justify a threshold change without fitting only the example. |
| Core | [Investigate missing or delayed telemetry](logging-health/README.md) | Distinguish an apparently quiet system from a collection gap and decide whether a query can support a conclusion. |
| Extension | [Work an end-to-end benign incident case](incident-case/README.md) | Combine separate lab skills into a defensible hypothesis, evidence requests and a final scoped conclusion. |
| Core | [Assess indicator quality and expiry](indicator-quality/README.md) | Explain confidence, source reliability, scope and expiry instead of treating every listed indicator as malicious. |
| Core | [Choose proportionate containment in a tabletop](containment-tabletop/README.md) | Balance evidence preservation, business impact, authority and reversibility when selecting the next action. |

### Forensics and recovery

| Kind | Package | Practice goal |
| --- | --- | --- |
| Extension | [Acquire and register a small evidence set](evidence-custody/README.md) | Add source, time, handling and integrity records to simple hashing, and explain what chain of custody does not prove. |
| Core | [Identify file types beyond the extension](file-type-triage/README.md) | Distinguish a filename label from file-format evidence and avoid concluding malware from a mismatch. |
| Extension | [Interpret filesystem timestamps and copies](file-time-analysis/README.md) | Explain that creation/modification/access values reflect filesystem operations and do not directly prove a person's actions. |
| Core | [Recover a deleted dummy file from a disposable image](deleted-file-recovery/README.md) | Practise read-only image handling, recovery to a separate folder and checking whether a recovered file is complete. |
| Core | [Reconstruct a benign browsing session from a lab profile](browser-artifacts/README.md) | Correlate history/download/cache clues while distinguishing stored records from proof of who used the browser. |
| Extension | [Perform and measure a real dummy-data restore](restore-drill/README.md) | Move from reviewing supplied restore evidence to verifying file contents, completeness and elapsed recovery time personally. |
| Extension | [Recover a benign object from your own capture](pcap-object-reconstruction/README.md) | Relate stream completeness to recovered content and explain why encrypted or missing traffic changes what can be recovered. |
| Extension | [Resolve a disagreement between two evidence sources](cross-source-corroboration/README.md) | Distinguish a supported cross-source link from coincidental matching and preserve alternative explanations. |

### Governance and reporting

| Kind | Package | Practice goal |
| --- | --- | --- |
| Core | [Classify a fictional team's data and handling needs](data-classification/README.md) | Link sensitivity and business purpose to access, retention, storage and sharing requirements. |
| Core | [Threat-model a small application or home-lab service](small-threat-model/README.md) | Identify assets, entry points, plausible failures and proportionate controls before adding tools. |
| Extension | [Prepare a public-safe evidence excerpt](evidence-redaction/README.md) | Remove unnecessary identifiers/secrets while keeping claims verifiable and preserving private originals. |
| Core | [Write scope and rules of engagement for a lab](rules-of-engagement/README.md) | Turn a vague testing idea into a bounded, reviewable activity. |
| Extension | [Create a small risk register with treatment choices](risk-register/README.md) | Extend technical finding priority into ownership, treatment, residual risk and review dates. |
| Core | [Prepare an incident brief and update for different audiences](incident-communications/README.md) | Separate confirmed facts, working hypotheses, action ownership and the next update need in technical and nontechnical wording. |
| Extension | [Write a reproducible finding and retest report](finding-report/README.md) | Explain scope, observation, impact, reproduction, correction and retest so another person can verify the claim. |
| Extension | [Complete an unfamiliar case and explain it to a reviewer](portfolio-mastery-capstone/README.md) | Demonstrate transfer, accurate limitations, useful next action and recall beyond following a guide. |
<!-- ADDITIONS_END -->

## Status and contribution

These are guided learning materials. Their reference checks test the supplied
data and helper tools. Jeremy's solo work and explanations of unseen cases
have not yet been assessed. The materials do not claim professional security
experience or that Jeremy wrote every helper tool. A personal work record should
state what the learner did, what was reviewed and what help was used.

## Start with one lab

Each folder has its own README and a single `lab.py` entry point. An entry point
is the file used to start the lab. Read the README, run `python lab.py --help`,
and work inside that lab's folder. The helper tools need Python 3.10+ and use
only its standard library, the tools that come with Python. The DNS packet file
can also be opened in Wireshark.

The offline exercises can run on Windows or in an existing Linux VM. A VM is a
practice computer that runs inside another computer. Offline tasks do not need
a cloud account, live target or public service. Tool tasks have separate needs.
They use owned local apps, saved packets or a disposable lab VM. Read each lab's
scope and setup rules. Loopback means traffic kept on the same computer.

The original twenty additional labs share `cases`, `prepare`, `show`, `analyse`,
`check` and `verify` commands. See the [maintained contract](FOUNDATION-CONTRACT.md)
and each README. That contract covers those twenty labs. The first six keep
their own commands. Use the README for every other package too.

Keep each practice run apart from reference fixtures. Fixtures are supplied
example files. Use the documented seed option where the lab has one. A seed
controls how example data is made. A new seed may change only names or labels;
that alone does not make the reasoning new. Check whether a command needs an
empty output folder before running it again. Keep notes from earlier attempts.

## Learning sequence

1. **Guided:** work through an example and explain each step in your own words.
2. **Solo:** on another day, keep the answer closed. Save your first answer.
3. **Unseen:** on another day, try fresh facts that need different reasoning.
4. **Reviewed:** explain the evidence to a reviewer. Save their check and any fixes.
5. **Recall:** try different facts about 7 and 28 days after the unseen attempt.

A solo attempt is not yet a reviewed result. Record a prompted attempt if you
need a hint about the answer. Use command help and your own notes when useful.
Log that help. If no fresh case or reviewer is ready, record "awaiting review".
Running a script cannot award mastery. Keep actual tool work separate from
reading supplied evidence. The goal is to understand each result, not to rush.

## Originality and evidence

- The scenarios, fixtures and tools were made as standalone exercises in October
  2026. They contain no assessment questions, answer sheets, course recordings or
  student identifiers.
- Each lab records how its fictional data was made and the hashes of reference
  files. A hash is a fingerprint of file bytes. It helps check that a file is the
  same and that a result can be repeated. It cannot prove skill or global novelty.
- Common security ideas and public protocol guides are shared knowledge. A
  protocol is a set of rules for sending data. These exercises use new questions,
  data, code and analyses. They do not just rename coursework.
- The access model is smaller than real cloud IAM, which manages identity and
  access. The login detector uses a simple teaching rule. Packet fixtures show
  made-up events. They are not captures from a real network.
- Web logs do not prove what happened inside an app. File hashes show changed
  bytes, not why they changed. The firewall model uses rules in order. It is not
  a set of settings to apply to a real host or cloud platform.

Read each lab's limits before using its output. Publish only new, checked
practice evidence. State who did the work and what they did.
