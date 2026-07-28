# Governed Next Best Action for Healthcare Professional Engagement

**Executive brief — for review by Commercial Operations, Medical Affairs, Legal, Compliance, Privacy, and Patient Safety**

Status: proposal. Section 13 states precisely what is built today and what is still hypothesis.

---

## 1. The decision we are asking for

We are asking for approval to build a governed Next Best Action (NBA) capability for HCP engagement,
and for the named function owners in Section 9 to be assigned. We are **not** asking for approval to
automate promotional decisions, to let software direct Medical Affairs activity, or to place any
model between a safety communication and the healthcare professional who needs it.

Approval gates each phase. No phase proceeds without the prior phase's exit criteria being met and
signed off.

---

## 2. Executive summary

Reaching healthcare professionals well has become genuinely harder. A single HCP relationship now
spans field visits, approved email, portal content, congress activity, medical information requests,
and safety communications — and every one of those touches carries regulatory obligations that
differ by market, by channel, and by whether the interaction is promotional or scientific.

Most organizations orchestrate this with static rules and a periodic target list refresh. That
approach degrades in three predictable ways: content recommendations collapse onto a small set of
assets so HCPs see the same few messages repeatedly; sequencing rules keep pushing promotional
outreach after the HCP's needs have visibly changed; and field teams quietly stop using the
suggestions, which makes the whole investment invisible.

We propose a connected view of HCP engagement — a knowledge graph over HCPs, accounts, referral and
affiliation structures, approved content, claims, and indications — with a decision layer on top
that recommends what to say next, through which channel, and when. Specialised software agents
monitor quality, diagnose problems, and propose improvements as reviewable change requests.

Three design commitments make this appropriate for a regulated environment:

1. **Compliance is enforced outside the model.** Hard constraints — consent, label scope, MLR
   approval and expiry, licensure, market rules, frequency caps — live in a deterministic,
   version-controlled rule engine that the model cannot argue with, outperform, or bypass. Model
   confidence never overrides a control.
2. **Commercial and Medical are separate systems.** They do not share a model, a data plane, an
   owner, or a governance body. Commercial NBA never reads medical interaction content.
3. **Safety communication is not optimized.** It is executed as a mandatory push, outside the
   ranking system, exempt from frequency caps, and reported on for reach and timeliness.

No software agent writes to production. Agents propose; deterministic gates validate; accountable
humans approve; everything is versioned and reversible.

---

## 3. Scope and non-goals

### In scope

- Content recommendation for **promotional** HCP engagement, selecting only among currently approved
  assets.
- Channel and timing recommendations for rep-delivered and non-personal promotional engagement.
- Suggestions surfaced to field teams inside CRM, and triggers into approved marketing automation.
- Continuous monitoring of recommendation quality, content coverage, and HCP fatigue signals.
- A governed change process for improving the above.

### Explicitly out of scope — non-goals

- **Directing Medical Affairs.** The system does not task, schedule, prioritise, or recommend MSL
  activity. Medical engagement planning is owned by Medical Affairs on its own platform.
- **Using medical data for commercial targeting.** Medical information requests, MSL interaction
  content, and medical inquiry records are not inputs to commercial models. See Section 5.3.
- **Generating claims.** The system never writes, rephrases, summarises, or recombines promotional
  claims. It selects among approved assets, and at most assembles pre-cleared modular content under
  pre-approved assembly rules.
- **Ranking or delaying safety communication.** See Section 6.2.
- **Autonomous production changes.** No agent-initiated change reaches production without human
  approval at the tier defined in Section 8.
- **Patient-level decision-making.** No patient-identifiable data is used, and no output influences
  individual patient care.
- **Replacing field judgement.** Reps and managers can always override, and their reasons are
  captured as a first-class signal.

---

## 4. Where HCP engagement breaks down today

### 4.1 Content concentration

Recommendation systems trained on engagement reward whatever already gets clicked. Left unchecked,
the effect compounds: a handful of assets dominate, HCPs see the same messaging repeatedly,
scientific breadth narrows, newer evidence never gets exposure, and engagement decays — which the
model reads as disinterest rather than as the fatigue it caused.

### 4.2 Static sequencing

Journey rules are written once and rarely revisited, so they miss changes in intent that are obvious
to a human. Promotional outreach continues when the HCP is clearly seeking scientific information.
Channels that are visibly generating fatigue keep getting used because the rule says so. Access
constraints — the no-see prescriber, the closed health system — are handled crudely or not at all.

### 4.3 Field non-adoption — the failure mode most programs ignore

The most common outcome for an NBA program in this industry is not a compliance incident. It is a
capability that reps stop opening. The causes are consistent and addressable: suggestion volume
exceeds what anyone can act on in a week; suggestions live outside the CRM workflow; there is no
reason code, so the rep cannot explain to the HCP why they are raising a topic; dismissals go into a
void; and most decisively, the suggestion conflicts with what incentive compensation pays the rep to
do. A suggestion that competes with an IC target loses every time. Section 9 treats this as a launch
prerequisite, not a change-management afterthought.

---

## 5. What we propose

### 5.1 A connected view of engagement

We bring together, into one governed knowledge graph:

- CRM interaction history and account structure
- Digital engagement — approved email, portal, congress, webinar
- The approved content library, with each asset's claims, indications, audience, market, and
  effective and expiry dates
- Referral, affiliation, co-prescribing, and publication relationships
- Practice, institution, IDN, and GPO hierarchies
- Payer and formulary access context at the appropriate level of aggregation
- Consent, channel preference, licensure, and eligibility state
- De-identified, aggregate patient-journey signals where permitted by market

### 5.2 Why a graph, and not just a feature table

This is a fair challenge and it has a specific answer. A conventional model works well for HCPs with
rich individual histories, and poorly for everyone else. A graph earns its place in three situations
that matter commercially:

- **Low-signal HCPs.** No-see and no-call prescribers, restricted-access accounts, newly licensed
  prescribers, and new-to-territory relationships have too little individual history to model
  directly. Network structure lets us reason about them from their context — the practice they sit
  in, the referral patterns around them, the institution's protocols.
- **Scientific coherence.** Content sits in a claim-and-indication structure. Enforcing that a
  recommendation is coherent with the indication and the label is far more reliable as a structural
  property of the graph than as a filter applied after ranking.
- **Account reality.** Decisions increasingly sit with institutions, not individuals. Hierarchy and
  affiliation are relationships, and relationships are what a graph represents natively.

### 5.3 Commercial and Medical separation — architectural, not procedural

This is a control, so it is built into the architecture rather than written into a policy document.

| | Commercial plane | Medical plane |
| --- | --- | --- |
| Purpose | Promotional engagement | Non-promotional scientific exchange |
| Owner | Commercial Operations | Medical Affairs |
| Data | CRM, digital promotional engagement, approved promotional assets | Medical inquiries, MSL interactions, medical content |
| Models | Separate | Separate |
| Governance | Promotional review committee | Medical governance |
| Access to the other plane's content | None | None |

Permitted crossings, and only these:

- **HCP-initiated unsolicited requests** are routed to Medical Information as a compliance
  obligation. The request content is not returned to the commercial plane and is not used as a
  commercial intent signal. Routing metadata is logged for audit.
- **Aggregated, non-content, delayed signal may flow to Medical**, never the reverse, and never at a
  granularity that reveals promotional intent or individual interaction content.
- **Safety and label changes** flow to both planes from the source of truth, unmodified.

"Recommend an MSL visit" is removed as a commercial action. Where an HCP's expressed need is
scientific, the commercial plane's only permitted output is to stop promotional outreach on that
topic and log the documented, non-directive triage path.

---

## 6. Non-negotiable controls

### 6.1 The compliance envelope

Every candidate recommendation passes a deterministic gate before it can be delivered. The gate is
version-controlled, unit-tested, and maintained outside the models. It fails closed: if a control
cannot be evaluated, the recommendation is suppressed.

| Control | Blocks | Enforced at |
| --- | --- | --- |
| Label scope per market | Any asset outside the approved indication for that market; any inferred or generated claim | Content gate |
| MLR approval and expiry | Unapproved, withdrawn, or expired assets; assets outside their approved audience | Approved-asset registry, read-only |
| Fair balance | Assets whose required safety pairing is not intact | Content gate, structural |
| Consent and legal basis | Any channel without valid, market-appropriate basis, including opt-in where required | Consent hub |
| Channel preference and opt-out | Any channel the HCP has declined | Consent hub |
| Licensure, specialty, eligibility | Assets not permitted for that professional category or credential | Eligibility gate |
| Prescriber data restrictions | Use of restricted prescriber-identifiable data, including registered opt-outs | Data layer |
| Market and jurisdiction rules | Anything not permitted in that market, including data localisation constraints | Market rule set |
| Transfer-of-value and spend rules | Actions creating undisclosed or non-compliant transfers of value | Interaction gate |
| Frequency and contact strategy | Contact exceeding the approved cadence for that segment and channel | Orchestration gate |
| Pre-approval and pre-launch | Any product-specific promotion before approval | Content gate |

Two properties of this table matter more than its contents. First, no entry can be satisfied by a
model output — each is a lookup against a system of record. Second, no entry can be traded off
against expected performance. There is no confidence threshold at which a control relaxes.

### 6.2 Safety communication is outside the optimizer

Dear Healthcare Professional letters, label changes, urgent field safety notices, and risk-management
materials are regulatory obligations, not content candidates.

- They are **never ranked** and never compete for a slot.
- They are **exempt from frequency caps**, fatigue rules, and diversity objectives.
- They are **executed as a mandatory push** on the schedule set by the accountable safety function.
- They are **reported on for reach and timeliness**, not for engagement.
- The optimizer **cannot reorder, delay, suppress, or substitute** them, and cannot count them
  against a contact budget.

### 6.3 Adverse event and product complaint obligations

Any system reading call notes, emails, portal messages, or inquiries will encounter adverse events
and product complaints, and the reporting clock is not negotiable.

- Suspected adverse events and product complaints are detected and routed to the safety system
  within the mandated window.
- Routing **never gates on model confidence**. Anything suspected is forwarded; the safety function
  adjudicates, not the model.
- Adverse event presence is **never a commercial targeting feature**.
- Detection performance is monitored with recall prioritised over precision, and the safety function
  owns the thresholds.

---

## 7. What the agents do — and what they may not do

Each agent performs one narrow function, proposes rather than acts, and is bounded by an explicit
prohibition.

| Agent | Contribution | May not |
| --- | --- | --- |
| **Knowledge maintenance** | Flags stale or inconsistent relationships; proposes graph updates as reviewable diffs | Write to the production graph; create or alter claim, label, or content mappings, which are owned by the approved-asset registry |
| **Model quality** | Monitors stability, drift, and ranking quality; triggers revalidation when thresholds are crossed | Promote a model; widen its own thresholds |
| **Performance monitoring** | Tracks coverage, diversity, fatigue, opt-out, and adoption; produces a structured diagnosis when a metric leaves its expected range | Change targets; act on its own diagnosis |
| **Post-ranking adjustment** | Reduces redundancy and holds content diversity inside its approved floor and ceiling | Introduce any asset that did not pass the compliance gate; alter safety communications |
| **Journey orchestration** | Proposes next content, channel, and timing within eligibility and cadence rules | Exceed contact strategy; recommend medical or MSL activity; act without gate clearance |
| **Diagnostic assistance** | Summarises evidence for reviewers, drafts change rationale, triages alerts | Approve anything, or serve as a compliance control |

### 7.1 Why there is no "verification agent"

An earlier version of this design had an agent that checked the other agents. We removed it. An
agent evaluating agents shares their inputs, their blind spots, and their non-determinism, and it
fails silently — which is the one property a control must never have.

Hard compliance validation is therefore a deterministic rule engine: explicit, versioned,
unit-tested, and independently auditable, with its own test suite treated as a controlled artifact.
Language models remain useful for triage, explanation, and preparing the reviewer's packet. They are
never the gate.

---

## 8. Change control

### 8.1 Lifecycle

**Detect** — monitoring identifies a degradation or an opportunity.
**Diagnose** — a structured statement of the problem, affected population, and evidence.
**Propose** — an agent generates a versioned, diffable change request with expected impact and
rollback plan.
**Validate** — deterministic gates plus offline evaluation against the approved test suite.
**Approve** — the accountable owner for that change tier signs off.
**Deploy and observe** — released with a holdout where feasible, monitored against pre-declared
guardrails.

### 8.2 Approval tiers

| Tier | Change type | Approver |
| --- | --- | --- |
| 0 | Operational configuration inside an already-approved envelope | Commercial Operations owner |
| 1 | Model retraining or reweighting inside the validated envelope | Analytics owner, with model-quality sign-off |
| 2 | New or altered content, claim, indication, or audience mapping | Promotional review committee |
| 3 | New channel, new market, new data source, or change of legal basis | Legal, Privacy, and Compliance |
| 4 | Anything touching safety communication or adverse event handling | Patient Safety, as owner |

### 8.3 Reversibility

- Every artifact — graph version, model version, rule set, content mapping — is versioned and
  attributable.
- One-command rollback to the last approved version.
- A **kill switch** that halts all automated recommendation delivery without disrupting safety
  communication.
- A **degraded mode** that falls back to approved static rules, so a failure never leaves field
  teams without guidance.
- Full audit trail: what was recommended, to whom, on what basis, under which versions, approved by
  whom.

### 8.4 Making oversight real

Documented human review that always approves is not a control. We therefore monitor approval and
override rates, time spent in review, and post-deployment reversals, and we report them to the
governing body. A reviewer with no information, no time, or no authority to decline is a finding, not
a process.

### 8.5 Validation and model risk

- GxP relevance determination completed per workflow, with validated-system treatment where
  applicable.
- Data integrity expectations applied to inputs feeding regulated decisions.
- A documented model card per production model: purpose, data, limitations, evaluation, owner.
- Champion/challenger with promotion criteria declared before the comparison runs.
- Drift triggers explicitly tied to label changes, new indications, and market rule changes — not
  only to statistical drift.
- A documented position on automated processing and profiling of professionals under applicable
  privacy law, and on AI-regulation classification and transparency obligations per market.

---

## 9. Field adoption and the operating model

### 9.1 Adoption is engineered, not communicated

- **Throttle volume.** A rep can genuinely act on a small number of suggestions per week. The system
  targets that number rather than maximising suggestion count.
- **Deliver in the workflow.** Suggestions appear in CRM where the rep already works. No separate
  tool.
- **Always give a reason code.** Every suggestion carries a plain-language rationale the rep can use
  in conversation, and can defend.
- **Make dismissal valuable.** Structured dismissal reasons are captured and feed the models and the
  monitoring agent. A dismissal is information, not friction.
- **Align incentive compensation first.** Target-list governance and IC design must be consistent
  with what the system recommends. This is a prerequisite for launch in any market, not a later
  optimisation. Where they conflict, IC wins in practice, and the program fails quietly.
- **Give managers visibility.** Coaching views showing suggestion quality and outcomes, not
  compliance-style adoption scorecards.

### 9.2 Accountability

| Function | Accountable for |
| --- | --- |
| Commercial Operations / Omnichannel | Overall capability, adoption, Tier 0 changes |
| Analytics / Data Science | Models, evaluation, Tier 1 changes, model cards |
| Promotional review (MLR) | Content, claim, indication, audience mappings; Tier 2 |
| Legal and Compliance | Rule set correctness, Tier 3, audit readiness |
| Privacy | Legal basis, consent architecture, cross-border and localisation |
| Patient Safety | Safety communication execution, adverse event routing, Tier 4 |
| Medical Affairs | The medical plane, and confirming separation holds |
| IT and Security | Platform, access control, retention, resilience |

A single governing body reviews performance, change requests above Tier 1, override rates, and the
risk register on a standing cadence.

---

## 10. How we will measure this

### 10.1 Design

- **Randomised holdouts** at HCP level where feasible and geography level where not, so that lift is
  measured against a comparable control rather than against last quarter.
- **Pre-registered metrics.** Primary and guardrail metrics, with thresholds, declared before
  release. Guardrail breach triggers automatic rollback consideration.
- **Engagement proxies and business outcomes reported separately.** Clicks are not prescriptions.
- **Stated confounders.** Formulary and access changes, sales-force sizing, competitor events, and
  seasonality all move prescribing independently. Where they cannot be controlled, we say so rather
  than attributing the movement to this program.

### 10.2 KPI frame

Every target is set after a measured baseline. We are deliberately not publishing target numbers in
advance of baselines.

| Dimension | Metric | Type |
| --- | --- | --- |
| Relevance | Suggestion acceptance and completion rate | Primary |
| Business outcome | Incremental prescribing versus holdout, defined attribution window | Primary |
| Coverage | Share of target HCPs reached with a compliant, relevant interaction | Primary |
| Content health | Distribution across approved assets, held between a floor and a ceiling | Guardrail |
| Fatigue | Opt-out and unsubscribe rate, email engagement decay, no-see conversion, rep-logged HCP complaints | Guardrail |
| Compliance | Gate rejection rate, control failures, audit findings | Guardrail |
| Safety | Reach and timeliness of mandatory communications; adverse event routing latency | Absolute obligation |
| Equity of access | Coverage variance across HCP volume deciles and geographies | Guardrail |
| Agility | Cycle time from detection to approved deployed change | Operational |
| Oversight quality | Reviewer override rate, post-deployment reversal rate | Operational |

Note that content diversity is a **guardrail with a floor and a ceiling**, not a goal. Maximising
diversity degrades relevance. The floor prevents collapse onto a few assets; the ceiling prevents
incoherent scattering.

### 10.3 What we will not claim

- We will not claim reduced compliance risk without an audit or monitoring finding to evidence it.
- We will not attribute prescribing changes to this program without a holdout.
- We will not report cycle-time improvement without a measured baseline of the current process.
- We will not present offline evaluation results as market performance.

---

## 11. Dependencies and prerequisites

These determine feasibility, and the first is the usual reason programs stall.

1. **Content metadata quality.** Every approved asset must be tagged to claim, indication, audience,
   market, channel, and expiry. Without this, nothing downstream works. This is typically the
   largest unglamorous workstream and it must be resourced explicitly.
2. **HCP identity and account mastering.** Reliable resolution of individuals to accounts,
   affiliations, and hierarchies.
3. **A consent and preference system of record**, per market, with legal basis captured.
4. **CRM and marketing automation integration**, including a supported path for delivering
   suggestions into the rep's workflow and triggering approved non-personal channels.
5. **Approved-asset registry integration**, read-only, with effective and expiry dates honoured.
6. **Safety system integration** for mandatory communication and adverse event routing.
7. **Data-use clearances** per market, including localisation and cross-border constraints.
8. **Incentive compensation and target-list alignment** in each market before launch there.

---

## 12. Risk register

| Risk | Consequence | Mitigation | Owner |
| --- | --- | --- | --- |
| Commercial/medical boundary erosion | Regulatory exposure, potential monitoring finding | Architectural separation, no shared data plane, periodic separation audit | Compliance and Medical Affairs |
| Language model error in a diagnostic or drafting step | Wrong diagnosis reaching a reviewer | Models never gate; deterministic controls; human approval; provenance shown to reviewer | Analytics |
| Self-reinforcing feedback loop | Model trains on its own targeting and narrows | Randomised holdouts, exploration budget, coverage guardrails | Analytics |
| Popularity bias | High-decile prescribers over-served, others neglected | Equity-of-access guardrail, coverage floors by segment | Commercial Operations |
| Proxy-metric gaming | Engagement rises, business outcome does not | Separate proxy from outcome reporting, holdout-based primary metric | Analytics |
| Drift after label or indication change | Non-compliant recommendations | Label change as an explicit revalidation trigger; expiry enforcement; fail-closed gate | MLR and Analytics |
| Field non-adoption | Investment produces no measurable value | Throttling, in-CRM delivery, reason codes, IC alignment as prerequisite | Commercial Operations |
| Compliance theater | Controls documented but not enforced | Gates as tested code, override-rate monitoring, independent audit | Compliance |
| Safety communication interference | Patient harm and regulatory exposure | Full carve-out from optimizer; cap exemption; reach reporting | Patient Safety |
| Vendor or platform lock-in | Rules and logic become unauditable | Rule set and content mappings held as our own version-controlled artifacts | IT |

---

## 13. Current maturity — stated plainly

| Component | Status |
| --- | --- |
| Knowledge graph design and schema | Designed |
| Graph construction on historical data | Prototype, single therapeutic area, offline |
| Recommendation and ranking approach | Offline evaluation only; no market deployment |
| Deterministic compliance gate | Design complete; not implemented |
| Commercial/medical separation architecture | Designed; requires Medical Affairs concurrence |
| Agent framework | Prototype; proposal generation only, no production write path |
| Safety and adverse event integration | Not started; requires Patient Safety engagement |
| Field adoption design | Designed; not tested with reps |
| Causal measurement design | Designed; no baselines measured |

No performance claim in this document is based on market deployment. All quantitative expectations
require baselines that have not yet been collected.

---

## 14. Conclusion

The goal is not more automation, more diversity, or more model sophistication. It is to deliver the
right information, through the right channel, at the right time — with scientific integrity,
regulatory compliance, and a clear line of accountability for every decision the system influences.

The design achieves that by being deliberately unambitious about autonomy and deliberately rigorous
about control. Software proposes; deterministic rules validate; named humans approve; everything is
versioned and reversible. Commercial and Medical stay separate because the architecture keeps them
separate. Safety communication reaches HCPs because no optimizer stands between them.

That combination is what makes the capability defensible in an audit, and defensibility is what
makes it deployable at all.

---

## Appendix A — Glossary

| Term | Meaning |
| --- | --- |
| **Next Best Action (NBA)** | A recommended next interaction. In this document it means either a suggestion surfaced to a field representative in CRM, or a trigger into approved automated non-personal promotion. The two have different approval, consent, and audit characteristics and are governed separately. |
| **HCP** | Healthcare professional. |
| **MLR / promotional review** | The medical, legal, and regulatory review that approves promotional content, its claims, its audience, and its expiry. |
| **MSL** | Medical Science Liaison. A Medical Affairs role conducting non-promotional scientific exchange. |
| **Fair balance** | The requirement that promotional material present risk information with appropriate prominence relative to benefit claims. |
| **Non-personal promotion (NPP)** | Promotional engagement not delivered by a person, such as approved email or digital channels. |
| **Approved-asset registry** | The system of record for approved content and its metadata, including effective and expiry dates. |
| **Guardrail metric** | A metric monitored to detect harm rather than to be maximised; breaching it triggers review or rollback. |
| **Fail closed** | If a control cannot be evaluated, the action is suppressed rather than permitted. |

## Appendix B — Market variation

The control envelope is market-specific and this is a build consideration, not a footnote. Consent
and legal basis for email differ materially between markets, with opt-in mandatory in several.
Transfer-of-value capture and disclosure regimes differ in scope and threshold. Some markets impose
data localisation requirements that constrain where the graph and models may run. Restrictions on
prescriber-identifiable prescribing data, and on professional-directed promotion generally, vary by
market and by state or province. Pre-approval activity is limited to disease awareness everywhere.

The implication is that the rule set is versioned per market, and no market goes live until its rule
set is signed off by local Legal, Compliance, and Privacy.
