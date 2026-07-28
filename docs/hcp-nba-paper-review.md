# Review: "Agentic Graph Engineering for Next Best Action in Healthcare Professional Engagement"

Reviewer perspective: pharmaceutical commercial/medical Next Best Action (NBA) and omnichannel
orchestration — the kind of program that ships inside Veeva/Salesforce CRM, gets reviewed by an
MLR committee, and has to survive an audit.

**Verdict:** the structure is sound and the governance instinct is right, but the paper is not yet
safe to circulate to a pharma executive audience. Three problems are disqualifying as written: it
merges commercial and medical engagement into one optimizer, it treats safety communication as a
ranking/diversity objective, and it presents an LLM "Verification Agent" as the compliance control.
There are also no pharmacovigilance obligations, no causal measurement design, and no acknowledgement
of the single most common cause of NBA failure in this industry — field force non-adoption.

The rewrite is at `docs/hcp-nba-executive-brief.md`.

---

## What the original gets right

- Governance-first framing, and the explicit statement that compliance cannot be overridden by
  model confidence. That is the correct posture and most vendor material does not say it.
- Separating detection, recommendation, verification, and approval into a lifecycle.
- Naming the two real failure modes of production NBA: content concentration (the model collapses
  onto a few assets) and static sequencing rules that do not notice the HCP's intent has changed.
- Declining to claim autonomy. "Assisted, governed optimization" is the honest and sellable framing.
- Business-readable tone with technical detail suppressed.

---

## Material issues

### 1. Commercial and medical engagement are merged. This is the most serious problem.

The paper puts "Medical Science Liaison interactions," "medical information requests," and
"medical inquiry records" into the same connected view and the same optimizer as promotional field
and email engagement, and it lists MSL transition as a next best action the engine should
recommend.

In pharma this is not a design preference, it is a firewall. Medical Affairs activity is
non-promotional scientific exchange; commercial functions may not direct MSL deployment, and
medical/MSL interaction data and unsolicited medical information requests may not be recycled into
promotional targeting. Companies operating under a Corporate Integrity Agreement have this written
into their obligations, and the PhRMA Code and FDA promotional rules point the same way. A
recommendation engine that reads MSL call notes to decide who the rep should email is exactly the
artifact an auditor or a monitor is looking for.

**Fix applied in the rewrite:** two decision planes with separate data, models, owners, and
governance. Commercial NBA never reads medical interaction content. The only permitted crossing is
a one-way, aggregated, non-content signal into medical (never the reverse), and an HCP-initiated
unsolicited request is routed to Medical Information as a compliance obligation, not consumed as a
commercial intent signal. "Refer to MSL" is removed as a commercial action and replaced with a
documented, non-directive triage path.

### 2. Safety communication is treated as a content-diversity problem.

The original lists "risk of underexposing important safety updates" as a symptom of poor content
coverage and asks the post-ranking agent to "ensure critical information is surfaced."

Safety communication — Dear Healthcare Professional letters, label changes, REMS materials, urgent
field safety notices — is a regulatory obligation with a completeness and timeliness requirement.
It must never be an item competing for slots in a ranked list, and it must never be
suppressed by a frequency cap, a fatigue rule, or a diversity objective.

**Fix applied:** safety communication is carved out of the optimizer entirely, executed as a
mandatory push with reach-and-timeliness reporting, and explicitly exempted from frequency capping
and ranking. The optimizer is not allowed to reorder it, delay it, or count it against contact
limits.

### 3. Pharmacovigilance is missing.

Any system ingesting rep call notes, emails, portal messages, or medical inquiries will encounter
adverse events and product complaints. There is a mandatory intake and onward-reporting duty with a
hard clock. The paper does not mention it once.

**Fix applied:** an explicit AE/product-complaint detection and routing obligation, with the
requirement that detection routes to the safety system and never gates on model confidence, plus
the constraint that AE presence is not a commercial targeting feature.

### 4. The "Verification Agent" is not an acceptable control.

An agent that evaluates the other agents' proposals cannot be the compliance gate. If it is an LLM,
it is non-deterministic, unauditable in the way a regulator expects, and it fails silently. An
agent checking agents is also a self-referential control — it shares the same failure modes and
the same bad inputs as the thing it is checking.

**Fix applied:** hard compliance gates are a deterministic, version-controlled, unit-tested rule
engine that sits outside the models and cannot be bypassed. Any LLM-based checking is demoted to
triage, explanation, and drafting the reviewer's summary — helpful, but never the gate. The gate's
own test suite becomes a controlled artifact.

### 5. The "Knowledge Management Agent" quietly performs regulated work.

"Incorporating newly approved scientific evidence" and "maintaining content accuracy" means changing
which claims attach to which product, indication, and audience. That is MLR territory. An agent
writing that to a production graph is an uncontrolled change to promotional content logic.

**Fix applied:** no agent writes to production. Agents emit versioned, diffable proposals. Content,
claim, and label mappings are owned by the approved-asset registry (PromoMats/Vault-equivalent),
consumed read-only, with effective and expiry dates enforced. Explicit prohibition on generative
composition of claims — the system selects among approved assets and, at most, assembles
pre-cleared modular content under pre-approved assembly rules.

### 6. The compliance list is generic where pharma is specific.

"Geographic regulations," "consent management," and "MLR approvals" are placeholders. A pharma
reviewer will want to see the actual constraint surface: legal basis and opt-in by market
(GDPR/ePrivacy for EU email, CAN-SPAM/CASL, Japan and China regimes including PIPL localization),
transfer-of-value capture and Open Payments/EFPIA disclosure, aggregate spend and gift restrictions
that vary by US state, licensure and specialty eligibility, AMA Prescriber Data Restriction Program
opt-outs, restrictions on prescriber-identifiable Rx data use, de-identification standards for
patient-level data, sample and speaker-program rules, and pre-approval/pre-launch limits to
disease awareness only.

**Fix applied:** a concrete control table naming the constraint, where it is enforced, and what it
blocks.

### 7. Off-label promotion and label scope are never mentioned.

The hardest prohibition in pharma promotion is absent. Fair balance is mentioned once in passing.

**Fix applied:** label-scope enforcement per market as a hard gate, fair-balance pairing as a
structural property of the asset rather than an optimization objective, and a stated prohibition on
the system inferring or generating any claim outside the approved label.

### 8. There is no explanation of why a graph is the right substrate.

The graph is asserted, not justified, which invites the reasonable objection that a feature store
and a gradient-boosted model would do. The defensible answer exists and should be stated: HCPs sit
in referral, co-prescribing, affiliation, and co-authorship structures; accounts roll up into
practices, IDNs, and GPOs; content sits in a claim/indication/evidence ontology. The graph earns
its place by propagating signal to low-signal HCPs — no-see and no-call prescribers, restricted
access accounts, new-to-territory, pre-launch markets — and by enforcing claim-to-indication
coherence structurally rather than by post-hoc filtering.

**Fix applied:** an explicit "why a graph" subsection tied to cold-start and access-restricted
coverage, which is a business problem executives recognize.

### 9. Outcomes are asserted without a measurement design, and some are unfalsifiable.

"Reduce compliance risk," "improve engagement effectiveness," "accelerate optimization cycles from
weeks to days" — no baselines, no comparison, no attribution method. In a category where every
vendor claims Rx lift, unsubstantiated numbers destroy credibility fastest. Rx-lift attribution is
also genuinely confounded by formulary and access changes, sales-force sizing, and seasonality.

**Fix applied:** a measurement section built on randomized HCP-level and geography-level holdouts,
pre-registered primary and guardrail metrics, separation of engagement proxies from business
outcomes, explicit statement of what the program will not claim, and a KPI table where every target
is set only after a measured baseline.

### 10. Field force adoption is not addressed at all.

This is the number one reason pharma NBA programs fail. Reps ignore suggestions. Contributing
causes are well known: suggestion volume exceeds what a rep can act on, suggestions arrive outside
the CRM workflow, there is no reason code so the rep cannot defend the action to the HCP, dismissal
feedback goes nowhere, and — decisively — the suggestion conflicts with what incentive compensation
pays the rep to do. If IC rewards reach and frequency on a target list, an NBA suggestion that
moves effort elsewhere loses every single time.

**Fix applied:** a dedicated adoption section covering suggestion throttling, in-CRM delivery,
mandatory reason codes, structured dismissal reasons feeding the models, and explicit alignment
with incentive compensation and target-list governance as a launch prerequisite rather than a
later concern.

### 11. There is no operating model, no ownership, and no rollback.

"Human reviewers evaluate proposed changes" does not say which humans, for which changes, with what
authority. Reversibility is claimed but no kill switch, rollback path, or degraded mode is defined.

**Fix applied:** a change tiering scheme from configuration through model updates inside a
validated envelope, new content/claim mappings requiring MLR, and new channel or market requiring
privacy and legal sign-off — each with a named accountable owner. Plus a defined kill switch,
rollback to last-approved version, and a safe degraded mode that falls back to approved static
rules. Override and approval rates are monitored so that human oversight can be shown to be real
rather than a rubber stamp.

### 12. Model risk management and validation are absent.

No mention of validation, computer-system-validation relevance determination, data integrity,
records and e-signature requirements where applicable, drift monitoring beyond a vague "model
stability," or EU AI Act posture and GDPR constraints on automated profiling of professionals.

**Fix applied:** a validation and model-risk subsection covering GxP relevance determination,
data-integrity expectations, documented model cards, champion/challenger with pre-declared
promotion criteria, drift triggers tied to label and indication changes, and a stated AI Act and
automated-decision position.

### 13. Maturity is ambiguous, which reads as overclaiming.

The paper says "we have developed" and then describes outcomes "expected" from an evaluation
framework that is never described. An executive cannot tell whether this is running in a market or
is a design document, and that ambiguity is itself a risk if any of the language leaks toward
promotional use.

**Fix applied:** an explicit maturity statement separating what is built, what is offline-evaluated
only, and what remains hypothesis, plus a clear decision request.

### 14. Missing risk register.

No candid discussion of hallucination, self-reinforcing feedback loops where the model's own
targeting becomes its training signal, popularity bias entrenching high-decile prescribers,
proxy-metric gaming, drift after a label change, "compliance theater" where controls are documented
but unenforced, or the equity problem where rural and lower-volume prescribers are systematically
deprioritized — which has reputational, patient-access, and arguably ethical dimensions.

**Fix applied:** a risk register with owner and mitigation for each.

---

## Smaller corrections

- **Drop the "Agentic Graph Engineering (AGE)" branding.** Inventing a framework acronym signals
  vendor material and costs credibility with this audience. Describe what it does.
- **Distinguish rep-facing suggestions from automated non-personal promotion.** These have different
  latency, approval, consent, and audit characteristics and cannot share one description.
- **"Next best action" needs defining on first use** as the specific artifact delivered — a CRM
  suggestion to a rep, or a trigger into marketing automation — because in this industry the term
  is used for both and the governance differs.
- **Diversity is an instrument, not a goal.** The original says this in the conclusion but the
  Performance Monitoring and Post-Ranking sections treat content diversity as a first-class KPI.
  Made consistent: diversity is a guardrail with a floor and a ceiling, tied to scientific coverage
  and fatigue, not maximized.
- **"Engagement fatigue" needs an operational definition** — otherwise it cannot be a KPI. Defined
  via opt-out and unsubscribe rate, email engagement decay, no-see conversion, and rep-logged HCP
  complaints.
- **Add the data-foundation prerequisite honestly.** Content metadata quality is the number one
  blocker. Without approved assets tagged to claim, indication, audience, market, and expiry, no
  NBA program works. This belongs up front as a dependency, not buried.
- **Add an explicit non-goals section.** Absent from the original, and its absence is why the
  medical/commercial merge slipped in unchallenged.

---

## Summary of structural changes in the rewrite

| Original | Rewrite |
| --- | --- |
| Executive Summary | Executive summary plus explicit decision requested |
| — | Scope and non-goals |
| Business Challenge | Where HCP engagement breaks down today, with field adoption added as a third failure mode |
| Proposed Solution | Proposal, with "why a graph" and a commercial/medical separation architecture |
| Governance-First Design | Non-negotiable controls, as a table naming enforcement point; safety and PV carved out |
| How the Intelligent Agents Contribute | What each agent may and may not do, with deterministic gates outside the agents |
| Controlled Change Management | Change control with tiered approval, kill switch, rollback, degraded mode |
| Business Value | Business value, tightened and de-duplicated |
| Expected Business Outcomes | Measurement design with holdouts, guardrails, and what we will not claim |
| — | Field adoption and operating model |
| — | Dependencies and prerequisites |
| — | Risk register |
| — | Current maturity |
| Conclusion | Conclusion |
