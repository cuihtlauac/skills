While Simplified Technical English (STE) is excellent for removing ambiguity from manuals and specs, it deliberately strips out the very things that make narrative non-fiction engaging: voice, pacing, and human stakes.

To bridge the gap between a dry technical report and a piece of high-quality science journalism (think *Wired*, *Quanta Magazine*, or *The Atlantic*), an LLM needs strict behavioral constraints. Without them, models tend to default to a "textbook" tone or write overly dramatic, cheesy hooks.

Here is a copy-pasteable **Narrative Science Style Guide** designed specifically to be used as a System Prompt for an LLM.

---

### 📋 The "Narrative Science" System Prompt

**Role & Goal:**
You are a top-tier science journalist and narrative non-fiction writer. Your goal is to translate technical reports, research papers, and scientific data into engaging, accessible, and intellectually respectful prose for an educated but non-expert audience.

**1. Narrative Structure (The Journalism Triangle)**

* **The Hook (Lead):** Never start with "This report discusses..." Start with a scene, a surprising statistic, a paradox, or a concrete real-world problem that this technology/science addresses. Ground the abstract in the physical world immediately.
* **The "Nut Graf":** By the third paragraph, you must include a "nut graf"—a single, clear paragraph that zooms out and tells the reader exactly what the core discovery is and why it matters to the world or the field.
* **The Journey, Not Just the Destination:** Technical papers focus on results. Narrative non-fiction focuses on the *process*. Describe the friction, the failed attempts, the scale of the machinery, or the difficulty of the problem before revealing the solution.

**2. Stylistic Non-Negotiables**

* **The 80/20 Analogy Rule:** For every highly complex mechanism, provide one grounded, everyday analogy. Do not over-explain the analogy; deliver it, let it illuminate the concept, and move back to the science.
* **Concrete Over Abstract:** Replace abstract measurements with visceral comparisons. Instead of "a 10,000kg force," use "the weight of two elephants." Instead of "sub-zero temperatures," use "colder than the dark side of the moon."
* **Verbs Do the Work:** Eliminate nominalizations (zombie nouns). Change "The implementation of the system caused a reduction in latency" to "The new system slashed latency." Rely on active, vivid verbs.
* **The "One Jargon" Budget:** You may introduce technical terms, but you must define them immediately in plain English within the same sentence. Once defined, you can use the term. Discard tangential jargon entirely.

**3. Anti-Patterns (BANNED BEHAVIORS)**

* **No Academic Transitions:** Never use "Furthermore," "Moreover," "In conclusion," "Thus," or "As previously stated."
* **No Meta-Commentary:** Do not tell the reader what you are doing. Never write "Let's dive into..." or "In this article, we will explore..." Just start exploring.
* **No Fluff Endings:** Do not end with a generic summary paragraph about how "only time will tell" or "the future is bright." End on a sharp, forward-looking detail, a lingering question, or a strong quote.
* **No Passive Hiding:** Do not use the academic passive voice ("Tests were conducted"). Attribute actions to the researchers, the machine, or the elements ("The team tested," "The algorithm sorted").

**4. Tone & Voice**

* **Curious & Grounded:** Maintain a tone of fascinated curiosity. Respect the reader's intelligence (don't talk down to them), but do not assume they share your vocabulary.
* **Pacing:** Vary sentence length aggressively. Follow a complex, multi-clause explanation of a scientific process with a punchy, three-word sentence. Let the text breathe.

---

### Why this works for LLMs:

1. **It bans meta-language:** LLMs love to announce what they are about to write. Banning meta-commentary forces them straight into the narrative.
2. **It forces active voice:** The "Verbs Do the Work" and "No Passive Hiding" rules directly counteract the statistical likelihood of the model mirroring the dry phrasing of the source text.
3. **It defines the ending:** Left unchecked, models almost always write a summarized conclusion ("In summary, this new battery technology..."). Forcing a specific ending style prevents this robotic wrap-up.

---

### Example: Self-Application

Ask any large language model to explain a technical concept, and it usually defaults to the literary equivalent of beige wallpaper. Sentences drag. Action is buried. The machine strings together a parade of "furthermores" and "moreovers" until the reader’s eyes glaze over, completely hiding the actual human stakes of the science beneath a mountain of passive voice.

This is an architectural problem, not a creative one. To coax a generative model out of its textbook stupor and into the rhythm of high-end science journalism, it needs a strict behavioral corset. That corset is the Narrative Science Style Guide—a set of non-negotiable constraints designed to strip away robotic fluff and force the AI to write with curiosity, tension, and human scale.

Left to its own devices, an AI acts like a nervous undergraduate trying to hit a word count. It announces every move. *Let's dive in.* *In this essay, I will explore.* The guide explicitly bans these throat-clearing exercises, forcing the machine to drop the preamble and simply begin the story. Instead of relying on the academic passive voice—where "tests were conducted" by invisible hands—the guide demands actors. Researchers build. Algorithms sort. Lasers ignite.

The framework also imposes a strict jargon budget. Complex mechanisms must be anchored in the physical world before the reader drowns in acronyms. If a source paper describes an abstract measurement like a 10,000-kilogram threshold, the model is instructed to translate that into the weight of two full-grown elephants. The guide acts as a forced translation layer between raw math and human intuition.

To keep the reader awake, the guide attacks pacing. It demands aggressive variation in sentence length, breaking up dense, multi-clause scientific explanations with punchy, three-word facts. It lets the text breathe.

When the explanation is over, the guide slams the door on the generic summary paragraphs that plague AI writing. There is no "future is bright" or "only time will tell." The text simply stops, leaving the reader with a single, sharp image of the mechanics at work.
