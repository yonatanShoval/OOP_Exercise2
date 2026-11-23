"""Homework review tools test: pack a student repository into one text file for an LLM chat.

The free chat cannot read a whole repository, so the bundle has:
  1. the full file tree, with sizes (binary data is listed, not included);
  2. the text files, most important first (README, docs, the demo main, source, tests),
     until a character budget is reached. Files that did not fit are listed at the end.
The bundle is written next to the repository, in course-materials/ (out of git).

Usage:
  python bundle_repo.py <repo folder> <label, e.g. "Repo A"> [budget_chars]
  python bundle_repo.py --list <file with one repository link per line> [budget_chars]
"""
import subprocess
import sys
from pathlib import Path

USAGE = ('Usage: python bundle_repo.py <repo folder> <label> [budget_chars]\n'
         '   or: python bundle_repo.py --list <links file> [budget_chars]')

TEXT_EXT = {".md", ".py", ".java", ".c", ".cpp", ".h", ".txt", ".toml", ".yml", ".yaml", ".cfg", ".csv"}
MAX_CSV = 5_000          # small CSV files only (inputs like the lecturer's example)
DEFAULT_BUDGET = 150_000  # characters per repository (100,000 left out the main code of a repo with long docs)


def priority(rel: str) -> int:
    """Lower number = included first."""
    low = rel.lower()
    name = low.rsplit("/", 1)[-1]
    if low == "readme.md":
        return 0
    if name in ("srs.md", "algorithm.md", "testing.md"):
        return 1
    if name == "ex0.py":
        return 2
    is_code = low.endswith((".py", ".java", ".c", ".cpp", ".h"))
    is_test = low.startswith(("tests/", "test/")) or name.startswith("test_")
    is_helper = "generat" in low or low.startswith("tools/")
    if is_code and not is_test and not is_helper:
        return 3  # the main source code, before the other docs
    if low.endswith(".md"):
        return 4
    if is_test:
        return 5
    if is_helper:
        return 6
    return 7


def main() -> None:
    if len(sys.argv) >= 3 and sys.argv[1] == "--list":
        budget = int(sys.argv[3]) if len(sys.argv) == 4 else DEFAULT_BUDGET
        bundle_list(Path(sys.argv[2]).resolve(), budget)
    elif len(sys.argv) in (3, 4):
        budget = int(sys.argv[3]) if len(sys.argv) == 4 else DEFAULT_BUDGET
        bundle(Path(sys.argv[1]).resolve(), sys.argv[2], budget)
    else:
        raise SystemExit(USAGE)


def bundle_list(list_file: Path, budget: int) -> None:
    """One repository link per line -> clone each one (if needed) and write one bundle per link.

    The repos get anonymous names (Repo A, Repo B, ...). The key from name to link is written
    next to the list, in index.txt, and stays out of git with the list itself.
    """
    urls = [line.strip() for line in list_file.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.strip().startswith("#")]
    index = []
    for i, url in enumerate(urls):
        letter = chr(ord("A") + i)
        dest = list_file.parent / f"repo-{letter.lower()}"
        if not dest.exists():
            subprocess.run(["git", "clone", "--depth", "1", url, str(dest)], check=True)
        bundle(dest, f"Repo {letter}", budget)
        index.append(f"Repo {letter}\t{url}")
    (list_file.parent / "index.txt").write_text("\n".join(index) + "\n", encoding="utf-8")


def bundle(repo: Path, label: str, budget: int) -> None:
    files = sorted(p for p in repo.rglob("*") if p.is_file() and ".git" not in p.relative_to(repo).parts)
    rel = {p: p.relative_to(repo).as_posix() for p in files}
    tree = "\n".join(f"{p.stat().st_size:>10,}  {rel[p]}" for p in files)

    candidates = [p for p in files if p.suffix.lower() in TEXT_EXT
                  and not (p.suffix.lower() == ".csv" and p.stat().st_size > MAX_CSV)]
    candidates.sort(key=lambda p: (priority(rel[p]), rel[p]))

    parts, used, skipped = [], 0, []
    for p in candidates:
        text = p.read_text(encoding="utf-8", errors="replace")
        if used + len(text) > budget:
            skipped.append(rel[p])
            continue
        parts.append(f"\n===== FILE: {rel[p]} =====\n{text}")
        used += len(text)

    bundle = (f"##### {label} #####\n\n--- File tree (bytes) ---\n{tree}\n"
              + "".join(parts)
              + f"\n\n--- Not included (over the {budget:,}-character budget) ---\n"
              + ("\n".join(skipped) or "(none)") + "\n")
    out = repo.parent / f"{repo.name}-bundle.txt"
    out.write_text(bundle, encoding="utf-8")
    print(f"{label}: {len(files)} files, {len(parts)} text files included ({used:,} chars), "
          f"{len(skipped)} left out; bundle {len(bundle):,} chars -> {out}")


if __name__ == "__main__":
    main()
