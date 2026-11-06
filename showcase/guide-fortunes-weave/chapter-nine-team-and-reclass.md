---
skill: guide-fortunes-weave
title: Choosing a Chapter 9 team and checking an Archer reclass
source: fictional
model: claude-sonnet-5-5
date: 2026-11-04
skillSha256: e6878b651358518384bd7068c40229e5626bab1bef4b4a0b9b6f37d24a4ba124
---

## Request

I'm about to start Chapter 9 on my Fortune's Weave run. Using my planner export and project notes, which four units should I deploy, and is it worth reclassing Iselle to Archer first? I can't tell if the boss needs magic or arrows.

## Inputs

**Dry run.** This skill normally works on live systems or its owner's own setup. Here the system state is invented in the inputs below, and nothing was changed anywhere. Run of the built `guide-fortunes-weave` task package. The recording session invented this scenario, the request and the inputs below before running the skill. It had no connectors, accounts or network access and could not execute scripts, so any scripted step was done by hand and the answer says so.

#### project-router.md

#### Planner project router

File name is a leftover from the first playthrough: `crimson-router.md`.

Active route: **Azure route** (switched at Chapter 5; confirmed in roster export header).
Route source: `notes/azure-route-notes.md` (excerpt below).
Planner: https://planner.example.com/runs/azure-main (read-only export supplied; no live access in this session).

##### Azure route notes (excerpt)

###### Chapter 9, Ashfall Bridge
- Map: narrow bridge, three deploy slots on the north bank, one forced slot (Corwin).
- Deploy limit: 5 total including the forced unit, so 4 free picks.
- Enemies: 6 lancers, 3 armored knights, 2 archers, boss Warden Halvek (armored, mounted).
- Armored knights: researched as resistant to sword and axe hits; take full damage from magic and arrows.
- Boss Warden Halvek: **resistance and defense values not yet researched.** Notes say "check the wiki before committing."
- Archers on the far bank hit units standing on the bridge's middle tiles.

###### Class: Archer (researched)
- Reclass requires Bow rank D. Reclass takes effect at once; skill carryover not documented in these notes.

###### Formula notes
- None recorded for damage against mounted units.

#### roster-export.txt

PLANNER EXPORT  run: azure-main  route: Azure  chapter: 8 cleared  exported: 2026-11-03

Unit      Lv  Class         Ranks            Equipment          Note (user)
Corwin    11  Knight        Lance C, Axe D   Iron Lance         forced slot Ch9
Iselle    10  Mage          Tome C, Bow E    Wind Tome          "want her on arrows?"
Brannoch   9  Fighter       Axe C            Steel Axe
Tamsin    10  Cleric        Staff C          Heal Staff         keep alive
Odric     11  Cavalier      Sword C, Lance D Steel Sword
Pell       8  Archer        Bow C            Iron Bow
Veyra      9  Mage          Tome D           Fire Tome          low durability
Hask       7  Thief         Dagger C         Iron Dagger

## Output

**Don't reclass Iselle to Archer: she can't. Archer needs Bow rank D, and her Bow rank is E.** She is also a Mage with Tome C, and the notes say armored knights take full damage from magic, so she is more useful as she is.

I can't say whether the boss needs magic or arrows. Warden Halvek's resistance and defense values are marked "not yet researched" in your Chapter 9 notes. I won't guess them. Look them up before you commit, then compare Iselle's Wind Tome against Pell's Iron Bow.

#### Suggested team (not a confirmed roster)

Corwin is already forced into one of the five slots, so you have four free picks.

| Pick | Unit | Why, from your export and notes |
|---|---|---|
| Forced | Corwin (Knight, Lv 11) | Required by the map. |
| 1 | Iselle (Mage, Lv 10, Tome C) | Magic does full damage to the three armored knights. |
| 2 | Pell (Archer, Lv 8, Bow C) | Arrows do full damage to the knights. He is already an Archer, so you don't need the reclass. |
| 3 | Tamsin (Cleric, Lv 10) | Your note says "keep alive". She heals on a map with two archers covering the bridge. |
| 4 | Veyra (Mage, Lv 9, Tome D) | A second magic source. Her note says "low durability", so keep her off the middle bridge tiles. |

Left out: Brannoch (axe hits are resisted by the knights), Hask (no researched role on this map) and Odric. Odric is the closest call. The notes cover sword and axe resistance on the knights but say nothing about lances, so I can't judge how his Steel Sword or lance would do against them. If you want a sturdier fourth pick than Veyra, Odric is the swap to consider.

#### What the notes don't settle

- **Boss damage:** Halvek is armored and mounted, but no values are recorded. The notes also have no formula for damage against mounted units.
- **Archer positioning:** The two far-bank archers hit units on the middle bridge tiles. That is a reason to hold Veyra and Tamsin back. It is not a tested placement plan.
- **Skills:** Your notes don't document skill carryover on reclass. This doesn't affect Iselle now, but it matters for any later reclass.

#### Basis and limits

- I used the read-only export for `azure-main` (Chapter 8 cleared, exported 2026-11-03) and the Azure route notes. The router file is named `crimson-router.md`, but the export header and the router's own text both confirm the Azure route, so I followed that.
- I had no live access to https://planner.example.com/runs/azure-main. If you changed levels, ranks or equipment after the export, send a fresh one and I'll recheck.
- I made no edits to your planner. The team above is a suggestion only.
- The writing checker script was not run. I reviewed this text by hand.

**Next step:** Find Halvek's resistance and defense values and add them to the Chapter 9 notes. Then I can say whether Iselle's tome or Pell's bow should lead the boss fight.
