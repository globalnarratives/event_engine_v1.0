# CIE Reference Guide
## Compressed Information Expression for Global Narratives

**Last Updated:** October 31, 2025  
**Version:** 0.9 (Pre-release - Functional Grammar In Development)

---

## Table of Contents

1. [Introduction](#introduction)
2. [Core Structure](#core-structure)
3. [Event Codes](#event-codes)
4. [Actor Codes (AIP System)](#actor-codes-aip-system)
5. [Action Codes](#action-codes)
6. [Modifiers and Context](#modifiers-and-context)
7. [Reference Operators](#reference-operators)
8. [Complete Examples](#complete-examples)
9. [Geographic Region Codes](#geographic-region-codes)
10. [Best Practices](#best-practices)

---

## Introduction

### What is CIE?

**Compressed Information Expression (CIE)** is a structured coding language designed for capturing international political, social, and economic events in a machine-readable format that preserves analytical nuance.

### Design Philosophy

CIE balances three competing demands:

1. **Human Readability:** Analysts must be able to read and write CIE without constant reference to documentation
2. **Machine Parsability:** Structure must be consistent enough for computational analysis
3. **Analytical Precision:** Must capture the complexity of real-world political events

### Key Innovation

Unlike natural language (too ambiguous) or pure numerical coding (too rigid), CIE uses **hierarchical dot notation** and **symbolic operators** to represent:

- Who did what to whom
- Under what circumstances
- In what context
- With what references to other events/actors

---

## Core Structure

### Basic Event Format

```
e.ddmmyyyy.region.ordinal
actor [action] target
- modifiers/context
```

### Minimal Complete Event

```
e.09102025.nam.0001
usa.min.def.exc.01 [s-st]
```

**Translation:** On October 9, 2025, the US Defense Secretary made a statement. (First North American event of the day)

### Complex Multi-Line Event

```
e.09102025.nam.0001
usa.jdc.07.nil.mgs.08 [rl] 25-12174 $ usa.min.def.exc.01
- x [pm] {dy} usa.sbs.tex.gnd.062 $ usa.sbs.ill
```

**Translation:** Federal magistrate (Northern Illinois, 7th Circuit) rules in case 25-12174 (which involves/references Defense Secretary), does not permit deployment of Texas Gendarmerie Unit 062 to Illinois.

---

## Event Codes

### Structure: `e.ddmmyyyy.region.ordinal`

| Component | Description | Example |
|-----------|-------------|---------|
| `e.` | Event prefix (constant) | `e.` |
| `ddmmyyyy` | Date (day-month-year) | `09102025` = Oct 9, 2025 |
| `region` | Three-letter region code | `nam` = North America |
| `ordinal` | Daily sequence number | `0001` = First event of day |

### Examples

```
e.17102025.eeu.001    # First Eastern Europe event, Oct 17, 2025
e.17102025.eeu.002    # Second Eastern Europe event, same day
e.18102025.mea.001    # First Middle East event, Oct 18, 2025
```

### Ordinal Numbering

- Resets daily per region
- Zero-padded to 3 or 4 digits (system dependent)
- No semantic meaning beyond sequence
- Gaps in numbering are acceptable (e.g., if event 002 is deleted)

---

## Actor Codes (AIP System)

### Hierarchical Dot Notation

Actor codes follow the pattern:
```
country.category.subcategory.role.individual
```

Each level provides increasingly specific identification.

### Country/Region Prefix

Three-letter code identifying the primary country of operation:

```
usa    # United States
rus    # Russia
chn    # China
isr    # Israel
irn    # Iran
```

See [Geographic Region Codes](#geographic-region-codes) for complete list.

### Institutional Categories

Common top-level categories:

| Code | Category | Example |
|------|----------|---------|
| `min` | Ministries/Departments | `usa.min` |
| `jdc` | Judicial system | `usa.jdc` |
| `sbs` | Subnational entities | `usa.sbs` |
| `uh` | Upper House (legislature) | `usa.uh` |
| `lh` | Lower House (legislature) | `usa.lh` |
| `pty` | Political parties | `gbr.pty` |
| `com` | Commercial entities | `rus.com` |
| `ngo` | Non-governmental orgs | `isr.ngo` |

**Note:** In unicameral legislatures, use `lh` for the single chamber.

### Example Actor Breakdowns

#### Example 1: Cabinet Official
```
usa.min.def.exc.01
```
- `usa` = United States
- `min` = Ministry/Department
- `def` = Defense
- `exc` = Executive (leadership level)
- `01` = Highest-level holder of this position (Secretary of Defense)

#### Example 2: Federal Judge
```
usa.jdc.07.nil.mgs.08
```
- `usa` = United States
- `jdc` = Judicial system
- `07` = Seventh Circuit
- `nil` = Northern Illinois
- `mgs` = Magistrate
- `08` = Specific judge (individual #8)

#### Example 3: Subnational Gendarmerie Unit
```
usa.sbs.tex.gnd.062
```
- `usa` = United States
- `sbs` = Subnational entity
- `tex` = Texas
- `gnd` = Gendarmerie (paramilitary police forces)
- `062` = Specific unit identifier

#### Example 4: Foreign Minister
```
egy.min.for.exc.01
```
- `egy` = Egypt
- `min` = Ministry
- `for` = Foreign Affairs
- `exc` = Executive (minister level)
- `01` = Badr Abdelatty (current Foreign Minister)

### Individual vs. Position Codes

**Important distinction:**

- Final numerical codes (`.01`, `.08`, etc.) refer to **specific individuals**
- Truncated codes refer to **positions or institutions**

Examples:
```
isr.hog        # Position: Israeli Head of Government (Prime Minister)
isr.hog.01     # Individual: Benjamin Netanyahu (current PM)

usa.min.def    # Institution: US Department of Defense
usa.min.def.exc.01  # Individual: Lloyd Austin (current SecDef)
```

### Tenure Changes

When an individual leaves a position:

```
# Benjamin Netanyahu's first term
isr.hog.01     # 1996-1999

# After Ehud Barak, Ariel Sharon, etc.
isr.hog.01     # 2009-present (Netanyahu returns, keeps .01)
```

The system tracks tenures separately in the database - the same individual code can have multiple tenure periods.

---

## Action Codes

### Basic Structure

Actions are enclosed in **square brackets** for verbs or **curly brackets** for nouns/gerunds:

```
[s-st]    # Verb: "makes statement"
{s-st}    # Noun: "statement" (when referencing an existing statement)
```

### Action Taxonomy

**[TO BE COMPLETED - Full action taxonomy under development]**

This section will contain the complete categorized list of action codes including:
- Speech acts (s-)
- Administrative acts (a-)
- Legal/judicial acts
- Military acts (m-)
- Economic acts (e-)

Selected examples currently in use:

```
[s-st]    # Makes statement
[s-tr]    # Threatens
[s-cr]    # Criticizes
[rl]      # Rules (judicial)
[pm]      # Permits
[a-mt]    # Meets with
[a-in]    # Intends / Announces intention
[m-st]    # Strikes (military)
```

### Verb vs. Noun Forms

Actions have both verb forms (square brackets) and noun forms (curly brackets). The noun form is used when **referencing an action that has already occurred**:

```
# Event 1 - The action occurs
actor1 [s-st]
# "Actor 1 makes statement"

# Event 2 - Referencing that statement
actor2 [s-cr] $ actor1 {s-st}
# "Actor 2 criticizes [with respect to] Actor 1's statement"
```

The curly brackets indicate "the statement" as a noun/object that already exists, not the act of making a new statement.

### Important: Actions Are Discrete

Each action in CIE appears on its own line. There are no compound actions. If an actor performs multiple actions, they are recorded as separate lines in the event structure.

---

## Modifiers and Context

### Negation Operator: `x`

Prefix `x` negates an action:

```
- x [pm]           # Does NOT approve/permit
- x [a-ag]         # Does NOT agree
```

**Important:** Negation applies only to actions that occur. CIE does not record non-events or absences. The negation operator indicates an actor explicitly did NOT take an action that was under consideration, not that something simply didn't happen.

### Context Markers

**[TO BE COMPLETED - Context markers under development]**

Additional modifiers and context markers exist for specialized situations. Full taxonomy to be documented in future versions.

Examples currently in use:
```
{dy}      # Deployment (noun)
```

---

## Reference Operators

### The `$` Operator

The `$` symbol indicates a **reference relationship** - pointing to another actor, event, or piece of context.

#### Basic Reference

```
actor1 [action] actor2 $ reference
```

**Example:**
```
rus.min.for.exc.01 [s-tr] tur.hos $ tur.hos {s-st}
```
**Translation:** Russian FM threatens Turkish Head of State **with respect to** Turkish Head of State's statement.

#### Multiple References

```
usa.min.def.exc.01 [s-st] $ irn.mil $ event.reference.123
```
**Translation:** US Defense Secretary makes statement **regarding** Iranian military **in reference to** (specific event).

#### Nested References

```
actor1 [action] actor2 
- $ actor3 {action-noun} $ actor4
```

**Example from earlier:**
```
usa.jdc.07.nil.mgs.08 [rl] 25-12174 $ usa.min.def.exc.01
- x [pm] {dy} usa.sbs.tex.gnd.062 $ usa.sbs.ill
```

**Breakdown:**
- CENTCOM commander receives order 25-12174 from Defense Secretary
- Does not approve deployment of Texas Guard unit to Illinois

### Document/Order References

Numerical codes between actions and `$` symbols indicate specific documents:

```
[rl] 25-12174 $    # Receives order number 25-12174
[s-st] UN-2024-157 $   # Makes statement regarding UN resolution 2024-157
```

---

## Complete Examples

### Example 1: Diplomatic Meeting

```
e.21082017.weu.083
gbr.sbs.scl.exc.001 [a-mt] gbr.sbs.wal.exc.001 $ eur(brx)
[a-in] $ gbr.brx.pol.22186
 > x[vu]
scl.exc [s-st] $ eur.brx
```

**Translation:**
First Minister of Scotland meets with First Minister of Wales regarding Brexit. Announces intent with respect to [specific proposed policy]. Does not approve [of this policy]. First Minister of Scotland releases a statement on Brexit.

### Example 2: Military Action

```
e.07102024.mea.142
isr.mil.idf.air.03 [m-st] lbn.mil.hez.cmd.south
- $ lbn.mil.hez [m-at] $ isr.sbs.north.civ
```

**Translation:**
Israeli Air Force commander orders strike on Hezbollah southern command, in response to Hezbollah attack on Israeli northern civilian areas.

### Example 3: Presidential Nomination

```
e.15012025.nam.003
usa.hos.01 [a-ap] usa.min.sta.exc.01
```

**Translation:**
US President nominates individual for Secretary of State position.

**Note:** The fact that this appointment requires Senate confirmation is procedural context, not part of this event. If/when Senate confirmation occurs, that would be a separate event.

### Example 4: Complex Judicial Ruling

```
e.09102025.nam.0001
usa.jdc.07.nil.mgs.08 [rl] 25-12174 $ usa.min.def.exc.01
- x [pm] {dy} usa.sbs.tex.gnd.062 $ usa.sbs.ill
```

**Translation:**
Federal magistrate (Northern Illinois, 7th Circuit) rules in case 25-12174 (which involves/references Defense Secretary). Does not permit deployment of Texas Gendarmerie Unit 062 to Illinois.

**Actor Breakdown:**
- `usa.jdc.07.nil.mgs.08` = Federal Magistrate, Northern Illinois District, 7th Circuit
- `usa.min.def.exc.01` = US Secretary of Defense
- `usa.sbs.tex.gnd.062` = Texas Gendarmerie Unit 062
- `usa.sbs.ill` = State of Illinois

---

## Geographic Region Codes

### Three-Letter Regional Codes

| Code | Region |
|------|--------|
| `nam` | North America |
| `sam` | South America |
| `weu` | Western Europe |
| `eeu` | Eastern Europe |
| `nea` | Northeast Asia |
| `sea` | Southeast Asia |
| `sas` | South & Central Asia |
| `mea` | Middle East & North Africa |
| `ssa` | Sub-Saharan Africa |
| `oce` | Oceania |

**Note:** Regional codes are custom to the Global Narratives System and distinct from ISO standards.

### Country Codes (Selected Examples)

**Country codes follow ISO 3166-1 alpha-3 standard.**

#### North America
```
usa    # United States
can    # Canada
mex    # Mexico
```

#### Europe
```
gbr    # United Kingdom
fra    # France
deu    # Germany
rus    # Russia
ukr    # Ukraine
```

#### Middle East
```
isr    # Israel
irn    # Iran
sau    # Saudi Arabia
tur    # Turkey
egy    # Egypt
```

#### Asia-Pacific
```
chn    # China
jpn    # Japan
ind    # India
pak    # Pakistan
aus    # Australia
nzl    # New Zealand
png    # Papua New Guinea
```

### Supra-National Entities

```
eur    # European Union
nato   # NATO
un     # United Nations
```

**For complete country code reference, see [ISO 3166-1 alpha-3](https://en.wikipedia.org/wiki/ISO_3166-1_alpha-3).**

---

## Best Practices

### Temporal Handling in CIE

**CIE records actions that occur on the event date, not predictions about future actions.**

- ❌ WRONG: "French president will travel to Istanbul next week"
- ✅ RIGHT: "French president announces intent to travel to Istanbul on [specific dates]"

The announcement (which happened today) is the event. The future travel, if it occurs, will be a separate event on that date.

**There is no future tense in CIE.** All events describe actions taken on the date specified in the event code.

### When Creating Events

1. **Start with the event code:** Establish date and region first
2. **Identify primary actors:** Use most specific codes available
3. **Choose precise actions:** Avoid generic codes when specific ones exist
4. **Add context progressively:** Use indentation for subordinate clauses
5. **Reference systematically:** Use `$` to link related actors/events

### Coding Conventions

**DO:**
- Use consistent indentation (2 or 4 spaces)
- Include natural language summaries below CIE
- Document ambiguous cases
- Update actor codes when tenures change

**DON'T:**
- Mix verb and noun forms of the same action arbitrarily
- Create ad-hoc abbreviations
- Skip reference operators when context is unclear
- Use overly generic action codes

### Hierarchy Principle

When multiple specificity levels are valid, prefer:
1. **Most specific available** for primary actors
2. **Institutional level** for references
3. **Individual level** only when the specific person matters

**Example:**
```
# Good: Specific individual as primary actor
usa.min.def.exc.01 [s-st]

# Good: Institutional reference
usa.min.def.exc.01 [s-st] $ irn.mil

# Avoid: Unnecessary specificity in reference
usa.min.def.exc.01 [s-st] $ irn.mil.irgc.qds.cmd.03
# (Unless that specific IRGC-QF commander is the point)
```

---

## Future Development

### Coming in v1.2

- **Full functional grammar:** Formal syntax specification
- **Parser implementation:** Automated CIE validation
- **Extended action taxonomy:** Expanded action codes for economic, social, environmental domains
- **Wildcard queries:** Support for `*.min.for` (all foreign ministers) type searches

---

## Revision History

- **v0.9** (October 2025): Initial reference documentation
- **v1.0** (Target: January 2026): Full functional grammar implementation

---

**For questions or clarifications, see GitHub Issues or contact project maintainer.**
