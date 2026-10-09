Daily chess problem for the blog of evgiz0r/chessproblemhelper. You are in a checkout of that repository on
`main`; the repository owner, Evgeni Bourd (IM for chess compositions, the mentor), set up this daily run on
2026-10-06 and authorized it to push its post directly to `main`, which GitHub Pages publishes.

This is an UNATTENDED run: nobody will send a second message. Do every step below in this one turn and do
not end your turn until the final report is written.

1. `git fetch origin main && git checkout main && git pull --ff-only origin main`.
   `pip install -q --use-pep517 -r requirements.txt pytest`.
   If the pull refuses because the local `main` has diverged (a stale checkout: on 9 Oct 2026 it held 54
   commits of an old history), do not reset or delete it: `git checkout -b daily-run origin/main`, work there,
   and publish with `git push origin HEAD:main`.
2. Read CLAUDE.md (the constitution), then read and follow `.claude/skills/daily-problem/SKILL.md` from start
   to end, reading every skill and reference file it names: act on answered mentor issues first, then theme,
   study, compose, gate, judge, write the post, self-review with one tested improvement to the kit, publish,
   open the mentor issue. Use `gh api` for GitHub issues, as the skill shows.
3. Never publish a diagram that fails `python tools/blog.py check "<FEN>"`. If nothing passes within the
   time budget, use the skill's fallback.
4. Publish by committing on `main` and pushing to origin main; if the push is rejected, `git pull --rebase
   origin main` and push again; retry network errors after 2, 4, 8 and 16 seconds.
5. Finish with four lines: the post URL (https://evgiz0r.github.io/ChessProblemHelper/blog/<slug>.html), the
   mentor issue URL, the gate result, and the improvement made to the kit.

This file is the run's own prompt: a run may improve it like any other part of the kit, and must keep it
working for the next run.
