# Owner profile

Fill this profile once per publication; the pipeline refuses to start without it.

```yaml
publication: ""
owner_name: ""
byline_people:            # real people who may sign pieces
  - name: ""
    credentials: ""
audiences:
  - name: ""
    knows: ""
    needs: ""
goals: ""                 # what publishing should do for the owner
assets:                   # the owner's own material
  data: []
  projects_or_cases: []
  tests_or_reviews: []
  positions_held: []      # stances the owner will argue
voice_profile: ""         # path or pasted text; required for owner-voice pieces
brand_rules: ""           # client brand, if any
high_stakes_reviewer: ""  # required for health, money or legal topics
banned_topics: []
writing_rules: ""        # folder holding rules.md, patterns.json, registers.md, voice-profile.md, corrections.md
ai_use_policy_url: ""     # the site-wide AI-use statement
disclosure_mode: "site_statement"   # site_statement | per_piece
reviewer_weekly_cap: 0
voice_exemplars: []       # 2-5 samples, matched by genre and form
case_study_defaults:
  variant: "portfolio"    # portfolio | customer | consulting
  page_caveats: "omit"    # omit | show
  anonymization: "names changed, results real"
  reference_on_request: true
brand_profile: ""         # a named brand profile; blank uses the estate neutral profile
brand_chart_roles:        # each mark a reader needs reaches 3:1 against its background (WCAG 1.4.11)
  light_hero: ""
  dark_hero: ""
  light_accent: ""
  context_grey: ""
visual_defaults:
  photoreal_ai: "never"
  max_callouts: 2
  alerts: "neutral surface, one accent, no coloured panel"
image_rights_log: ""
```

Keep a filled profile with the publication's own project files, outside this skill, and pass its path as a task input.
