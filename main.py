import argparse
import json
import subprocess
import sys
import typing as T

import popplerqt5


class PDFAnnotation(T.TypedDict):
    page: str
    author: str
    content: str


def extract(fn: str) -> list[PDFAnnotation]:
    doc = popplerqt5.Poppler.Document.load(fn)
    annotations: list[PDFAnnotation] = []
    for i in range(doc.numPages()):
        page = doc.page(i)
        for annot in page.annotations():
            contents = annot.contents()
            assert contents is not None
            if annot.author().strip():
                annotations.append(
                    {
                        "page": page.label(),
                        "author": annot.author(),
                        "content": annot.contents(),
                    }
                )

    return annotations


def load_issyes(repo: str) -> list[str]:
    cmd = [
        "gh",
        "issue",
        "list",
        "--repo",
        repo,
        "--json",
        "title",
        "--limit",
        "999",
        "--state",
        "all",
    ]
    result = subprocess.run(cmd, stdout=subprocess.PIPE)
    out: list[dict[str, str]] = json.loads(result.stdout)
    issues: list[str] = []
    for issue_dict in out:
        issues.append(issue_dict["title"])

    print(f"loaded {len(issues)} issues")

    return issues


def createIssue(repo: str, pdfanno: PDFAnnotation, curr_issues: list[str]) -> None:
    content = pdfanno["content"]
    title = (content[:60] + "…") if len(content) > 61 else content
    title = title.replace("\n", "")

    if any(title in issue for issue in curr_issues):
        print(f"Issue with tittle `{title}` already created")
        return

    reviewer_label = f"reviewer:{pdfanno['author']}"
    cmd = [
        "gh",
        "issue",
        "create",
        "--assignee",
        "@me",
        "--label",
        reviewer_label,
        "--title",
        title,
        "--body",
        f"Pagina: {pdfanno['page']}\n\n" + content,
        "--repo",
        repo,
    ]
    print("Will be executing the command bellow:")
    print(" \\\n\t".join(cmd))
    answer = input("Continue? [Y/N]")
    if answer.lower() in ["y", "yes"]:
        subprocess.run(
            [
                "gh",
                "label",
                "create",
                reviewer_label,
                "--repo",
                repo,
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        subprocess.run(cmd, stdout=sys.stdout, stderr=sys.stderr, check=True)
    else:
        print("skipped")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("repo")
    parser.add_argument("fn")
    args = parser.parse_args()

    curr_issues = load_issyes(args.repo)

    annoatations = extract(args.fn)
    for ann in annoatations:
        if not ann["content"].strip():
            print(f"WARN: empty annotation {ann=}")

        createIssue(args.repo, ann, curr_issues)
