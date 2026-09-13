# Shell hygiene for agents

Small traps that have cost real runs. Both bit a supervisor session on macOS with zsh.

- **Never name a loop variable `path` in zsh.** `path` is tied to `PATH`; assigning it inside
  a `for` loop clobbers the search path and every later command fails to resolve. Use `p`,
  `file`, `src`.
- **Quote every variable expansion.** zsh does not word-split unquoted variables the way bash
  does, so a script that "works in bash" can pass one argument where it meant several, or
  vice versa. `"$var"` everywhere; use arrays when you mean a list.
- **Prefer portable flags.** `date -v-10M` is BSD/macOS; `date -d '10 minutes ago'` is GNU.
  `grep -P` is GNU only. Say which platform a documented command targets.
- **Check strings before a batch edit.** A patch script that asserts on an exact anchor and
  aborts on the first mismatch can leave earlier files edited and later ones untouched. Verify
  every anchor exists first, or make the script all-or-nothing.
