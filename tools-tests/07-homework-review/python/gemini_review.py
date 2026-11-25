"""Send a prompt and text files (repository bundles, or a transcript) to the Gemini API (free tier).

Usage:
    python gemini_review.py <model> <prompt.md> <file1.txt> [<file2.txt> ...] [--out <answer.md>]

Examples:
    python gemini_review.py gemini-4-hydrogen ../review_prompt.md repo-a-bundle.txt repo-b-bundle.txt
    python gemini_review.py gemini-4-hydrogen summary_prompt.md transcript.txt --out summary.md

The API key is read from secrets/gemini_api_key.txt (blocked by .gitignore).
The answer is saved to --out if given, otherwise to
course-materials/homework-review/gemini-review-<model>.md. It is not printed.
Printed: the time of the request and the token counts the API returns.

Note: on the free tier, Google uses the content to improve its products.
Send only public repositories under anonymous names, or a transcript the lecturer approved.
"""
import pathlib
import sys
import time

from google import genai

ROOT = pathlib.Path(__file__).resolve().parents[3]
KEY_FILE = ROOT / "secrets" / "gemini_api_key.txt"
OUT_DIR = ROOT / "course-materials" / "homework-review"


def build_contents(prompt_file, bundle_files):
    """The prompt first, then each bundle with its file name as a header."""
    parts = [pathlib.Path(prompt_file).read_text(encoding="utf-8")]
    for f in bundle_files:
        p = pathlib.Path(f)
        parts.append(f"\n\n===== Attached file: {p.name} =====\n\n" + p.read_text(encoding="utf-8"))
    return "".join(parts)


def main():
    args = sys.argv[1:]
    out_path = None
    if "--out" in args:
        i = args.index("--out")
        if i + 1 >= len(args):
            print(__doc__)
            sys.exit(1)
        out_path = pathlib.Path(args[i + 1])
        del args[i:i + 2]
    if len(args) < 3:
        print(__doc__)
        sys.exit(1)
    model, prompt_file, bundles = args[0], args[1], args[2:]

    client = genai.Client(api_key=KEY_FILE.read_text(encoding="utf-8").strip())
    contents = build_contents(prompt_file, bundles)
    print(f"model: {model} | characters sent: {len(contents):,}")

    start = time.perf_counter()
    response = client.models.generate_content(model=model, contents=contents)
    elapsed = time.perf_counter() - start

    u = response.usage_metadata
    print(f"time: {elapsed:.1f} s")
    print(f"tokens in: {u.prompt_token_count} | out: {u.candidates_token_count} "
          f"| thinking: {u.thoughts_token_count} | total: {u.total_token_count}")
    print(f"model version (from the API): {response.model_version}")

    out = out_path or OUT_DIR / f"gemini-review-{model}.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(response.text or "", encoding="utf-8")
    print(f"answer saved: {out} ({len(response.text or ''):,} characters, {len((response.text or '').split()):,} words)")


if __name__ == "__main__":
    main()
