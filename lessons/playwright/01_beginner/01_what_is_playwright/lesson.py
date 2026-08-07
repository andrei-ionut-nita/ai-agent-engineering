"""
Lesson 1: what is Playwright, and why does a web agent need a browser at all.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/playwright/01_beginner/01_what_is_playwright/lesson.py

Every LangChain lesson so far has been about talking to a model. This
course is about giving that model, or a plain Python script, a real
browser to control: a way to look at a web page and act on it, the same
way a person would with a mouse and a keyboard.
"""

# Nothing in this lesson touches the network or opens a browser yet.
# That starts in Lesson 3. This file is here so the ideas below have a
# place to run, not because there's code to demonstrate.

WHY_A_BROWSER = {
    "Reading rendered pages": (
        "A lot of the web is built with JavaScript that fills in content "
        "after the page loads. A plain HTTP request (e.g. requests.get) "
        "only sees the raw HTML the server sent, often close to empty. "
        "A real browser runs that JavaScript first, the same way it "
        "would for a person, so it sees the finished page."
    ),
    "Clicking and typing": (
        "Some things on the web only exist behind an action: a button "
        "that reveals a form, a dropdown that has to be opened before "
        "an option can be picked. There's no URL for that, you have to "
        "actually interact with the page."
    ),
    "Logging in": (
        "Many useful pages are behind a login. A browser can fill in a "
        "username and password and submit the form, exactly like a "
        "person would, then keep using the resulting session."
    ),
    "Looking like a real visitor": (
        "Some sites treat plain HTTP requests, with no browser behind "
        "them, as bots and block them outright. A real browser, with a "
        "real rendering engine, looks like an ordinary visitor."
    ),
}

WHAT_IS_PLAYWRIGHT = (
    "Playwright is a browser automation library: Python code that "
    "starts a real browser (Chromium, Firefox, or WebKit), then drives "
    "it, open a page, click this, read that, close it, all without a "
    "human touching a mouse. It was built by Microsoft, and it's the "
    "same kind of tool as Selenium, just newer and, for most people, "
    "considerably easier to use correctly."
)


def main() -> None:
    print("What is Playwright?")
    print(f"  {WHAT_IS_PLAYWRIGHT}\n")

    print("Why would an agent need a browser instead of a simple HTTP request?")
    for reason, explanation in WHY_A_BROWSER.items():
        print(f"\n  {reason}:")
        print(f"    {explanation}")


if __name__ == "__main__":
    main()
