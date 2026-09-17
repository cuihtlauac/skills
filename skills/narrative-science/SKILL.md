---
name: narrative-science
description: >-
  Write human-facing technical prose in a narrative science-journalism style
  (think Wired, Quanta, The Atlantic) instead of the default textbook tone. Use
  ONLY when producing a standalone piece a person will read for its own sake — an
  article, blog post, explainer, essay, newsletter, magazine-style piece, or a
  write-up/report meant for an audience — or when the user says "make this
  readable", "write it up for readers", "narrative style", or invokes /narrative.
  Do NOT use for machine-facing or utilitarian text: code, comments, commit
  messages, backlog/changelog entries, structured data, API/reference docs,
  READMEs-as-spec, or ordinary chat answers and quick explanations. When unsure
  whether the reader wants prose or facts, default to plain and skip this skill.
---

# Narrative science style

A style discipline for one specific situation: the user is sharing technical
information **with a human being who will read it as prose** — an article, a blog
post, an explainer, an essay, a write-up for colleagues or the public. Most
generated text is not this. Code, commit messages, backlog and changelog lines,
structured data, reference docs, and quick chat answers are all machine-facing or
utilitarian, and this skill must stay out of them. The goal here is to bridge the
gap between a dry technical report and high-quality science journalism.

## When this applies (and when it does not)

Apply it when the artifact is prose meant to be *read*:

- "Write a blog post / article / explainer about X"
- "Draft something for our users / readers / newsletter explaining Y"
- "Turn this report (or these results) into something a person can read"
- The user asks for "narrative", "readable", "magazine-style", or types `/narrative`

Stay out when the text is utilitarian, even if the subject is technical:

- Code, inline comments, docstrings, commit messages, PR descriptions
- Backlog / changelog entries, structured data, config, logs
- API references, spec-style READMEs, tables meant for lookup
- Ordinary conversational answers and short explanations in chat

When it is genuinely ambiguous whether the user wants crafted prose or just the
facts, **default to plain and do not invoke this skill.** Better to under-fire and
let the user ask for it by name than to dress up an answer they wanted terse.

## The style

**Role.** Write as a top-tier science journalist and narrative non-fiction
writer. Translate technical material into engaging, accessible, intellectually
respectful prose for an educated but non-expert audience. Respect the reader's
intelligence; do not assume they share your vocabulary.

### 0. Truth is paramount (this rule overrides every style rule below)

The style exists to make true things vivid — never to make vivid things pass as
true. When a stylistic rule and a fact collide, the fact wins, every time.

- **No invented specifics.** Do not manufacture numbers, dates, names, quotes,
  benchmarks, or mechanisms to make a sentence land harder. "Concrete over
  abstract" (§2) means *translate* real quantities into visceral terms, not
  *conjure* quantities that were never in the source. If you don't have the
  figure, write around it.
- **Vividness must not distort.** A punchy verb or a clean framing that subtly
  overstates what the science actually shows is a bug, not a flourish. Precision
  beats drama when they conflict.
- **Flag uncertainty, don't launder it.** If something is contested, approximate,
  or your own inference, say so plainly. Do not let confident prose imply
  certainty the evidence doesn't support.
- **When unsure, degrade to plain.** Better a flat, accurate sentence than a
  beautiful, wrong one. If you cannot make it both true and vivid, keep it true.

### 0.5 Fidelity and economy (the translation contract)

When the task is to *translate a specific source* — a man page, a report, a
result, a spec — the narrative **replaces** the source; it does not supplement it.
The reader should finish it having learned everything the source conveys, and
should never need to open the original. That contract cuts two ways, and violating
it in either direction is the same failure:

- **Carry all the load-bearing information.** Every option, default, caveat, or
  fact in the source that changes what a reader would *do* must survive the
  translation. Readability is not a licence to drop content. If the source
  documents three flags and a default value, the reader must come away knowing
  they exist.
- **Translate, don't expand.** Do not import outside facts, history, benchmarks,
  or trivia that aren't in the source just to build a better narrative arc. Added
  information turns a translation into an essay — a *different task*. If you're
  itching to add a fascinating tangent, that's a signal you've left the
  translation brief; either drop it, or tell the user it's an addition.
- **Stay economical.** A faithful translation of dense reference material lands
  near the source's own information density — expect a **small** multiple of its
  length, not several times it. A draft running 3–5× the source is almost
  certainly padded with imported material or restated filler; cut back to what the
  source actually says. Terse input, terse output.
- **When the source is genuinely thin, say so — don't inflate.** If a man page
  documents almost nothing, the honest narrative is short and admits the tool is
  simple. Manufacturing depth the source doesn't have violates both this rule and
  §0.

This rule applies to *translation*. Open-ended composition ("write a blog post
about X") has no fixed source and no ratio to honour — there, length serves the
piece.

### 1. Narrative structure (the journalism triangle)

- **The hook (lead).** Never open with "This report discusses…". Start with a
  scene, a surprising number, a paradox, or a concrete real-world problem.
  Ground the abstract in the physical world immediately.
- **The nut graf.** By roughly the third paragraph, include one clear paragraph
  that zooms out and tells the reader exactly what the core discovery is and why
  it matters.
- **The journey, not just the destination.** Papers report results; narrative
  reports process. Show the friction, the failed attempts, the scale of the
  machinery, the difficulty — before revealing the solution.

### 2. Stylistic non-negotiables

- **The 80/20 analogy rule.** For each highly complex mechanism, give one
  grounded everyday analogy. Deliver it, let it illuminate, and move back to the
  science. Do not over-explain the analogy. Use analogies **sparingly** — roughly
  one per major concept, not one per paragraph; a piece wall-to-wall with "it's
  like…" reads as evasion, not clarity.
- **Every analogy leaks — show where.** No analogy maps perfectly onto the
  science, and an unqualified one becomes a false claim in the reader's head. When
  the gap matters, name it in a clause: "…like a seating chart — except the guests
  can also veto each other's *seats*, not just their neighbours." Mark the limit,
  then move on. If an analogy can't be bounded honestly in a line, it's the wrong
  analogy — cut it.
- **Concrete over abstract.** Replace abstract measurements with visceral
  comparisons. Not "a 10,000 kg force" but "the weight of two elephants"; not
  "sub-zero temperatures" but "colder than the dark side of the moon".
- **Verbs do the work.** Kill nominalizations. "The implementation of the system
  caused a reduction in latency" becomes "the new system slashed latency". Use
  active, vivid verbs.
- **The one-jargon budget.** You may introduce a technical term, but define it in
  plain English within the same sentence. After that you may use it. Discard
  tangential jargon entirely.

### 3. Anti-patterns (banned)

- **No academic transitions.** Never "Furthermore", "Moreover", "In conclusion",
  "Thus", "As previously stated".
- **No meta-commentary.** Never "Let's dive into…" or "In this article, we will
  explore…". Just start.
- **No fluff endings.** No "only time will tell", no "the future is bright". End
  on a sharp forward-looking detail, a lingering question, or a strong quote.
- **No passive hiding.** Not "Tests were conducted" — attribute the action. The
  team tested. The algorithm sorted. The laser ignited.

### 4. Tone and pacing

- **Curious and grounded.** Keep a tone of fascinated curiosity without talking
  down to the reader.
- **Vary sentence length aggressively.** Follow a dense multi-clause explanation
  with a punchy three-word sentence. Let the text breathe.

### 5. Link liberally (the third way on sourcing)

Journalism stays light on references and asks for trust; academic writing buries
its sources in a dry bibliography nobody reads. Inline hyperlinks are the way out:
sourcing that costs the reader nothing until they want it. Links are cheap — use
them generously.

- **Link the load-bearing nouns.** The first time a real project, tool, paper,
  standard, person, dataset, or concept appears, link it to its canonical home
  (official site, repo, spec, the original paper, a solid reference page). Don't
  wait for a "References" section — there isn't one.
- **Link every checkable claim to where it can be checked.** A benchmark, a
  historical fact, a "researchers found…" — hang it on the source. This is §0 made
  operational: a linked claim is a verifiable claim.
- **Weave, don't interrupt.** Anchor the link on the natural noun phrase in the
  sentence ("the [Mancoosi](url) project"), never on "click here" or a bare URL
  dumped mid-paragraph. The prose must read cleanly with every link stripped out.
- **Only real destinations — a fabricated URL is worse than none.** This is a
  hard §0 rule: never invent a link or guess a URL to look authoritative. If you
  don't know the exact address, name the source in plain text so the reader can
  find it, or leave a `[TODO: link to …]` marker for a human to fill. A dead or
  wrong link erodes exactly the trust the link was meant to build.
- **Density, not spam.** Rich means most substantive claims are anchored — not
  that every third word is blue. Link the noun that carries weight; skip the
  filler. If two adjacent links point to the same place, keep one.

## Why these constraints

They exist to counteract known LLM defaults. Banning meta-language stops the
model announcing what it is about to write. "Verbs do the work" and "no passive
hiding" pull it off the dry phrasing it mirrors from source material. Fixing the
ending style prevents the reflexive "In summary…" wrap-up. A worked
self-application demo lives in `example.md`.
