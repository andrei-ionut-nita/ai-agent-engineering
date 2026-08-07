# Lesson 1: What is Playwright?

## A request versus a browser

Most of the LangChain course, and most simple web scraping, works by
sending an HTTP request and reading back whatever text the server
sends. That's fast, cheap, and works fine for a lot of the web. It
breaks down the moment a page needs JavaScript to finish building
itself, needs a click to reveal something, or needs a login before it
will show anything useful at all.

Playwright solves that by not sending a request at all. Instead, it
starts an actual browser, the same kind of program you already use
every day, and drives it programmatically: open this URL, click that
button, type into that field, read back what's on screen now. The
browser does all the same work it would do for a human: downloading
the page, running its JavaScript, laying it out, and rendering it.
Playwright just sits in the driver's seat instead of you.

## Why an agent needs this

An AI agent that only knows how to send HTTP requests can read static
pages, but it can't do anything the web was actually built for:
logging in, submitting a search, clicking through a multi-step flow,
or waiting for content that only appears after some JavaScript runs.
Giving an agent a browser, through a library like Playwright, gives it
hands: the same basic actions a person has, click, type, read, scroll,
wait.

This course builds that up gradually. The beginner tier here is just
plain Python controlling a browser, no AI involved at all, exactly
like Lesson 13 in the LangChain course built a calculator tool before
any model ever touched it. The AI only gets wired in starting at
Lesson 16, once there's something real for it to control. See this
course's [README](../../README.md) for the full lesson list and
prerequisites.

## Playwright versus Selenium

If you've heard of browser automation before, it was probably through
Selenium, an older tool that does a similar job. Playwright, built by
Microsoft, is newer and was designed with the lessons of Selenium's
rough edges already learned: it waits for elements automatically
instead of making you write manual `sleep()` calls (more on this in
Lesson 9), it talks to Chromium, Firefox, and WebKit through one
consistent API, and its Python library ships with everything needed to
install real browser binaries with a single command (Lesson 2).

## The code, piece by piece

This lesson has no live browser code, that starts in Lesson 3. What's
here is a plain Python dictionary laying out the reasons a script
might need a browser instead of a simple request, printed out so you
can read them slowly instead of all at once in prose.

```python
WHY_A_BROWSER = {
    "Reading rendered pages": (...),
    "Clicking and typing": (...),
    ...
}
```

Each key is a short reason, each value is one or two sentences
explaining it. `main()` just loops over the dictionary and prints both.

```python
for reason, explanation in WHY_A_BROWSER.items():
    print(f"\n  {reason}:")
    print(f"    {explanation}")
```

`.items()` on a dictionary gives you both the key and the value
together, one pair at a time, which is the usual way to loop over a
dictionary in Python when you need both.

## Running it

```bash
uv run python lessons/playwright/01_beginner/01_what_is_playwright/lesson.py
```

## Expected output

```
What is Playwright?
  Playwright is a browser automation library: Python code that starts a real browser (Chromium, Firefox, or WebKit), then drives it, open a page, click this, read that, close it, all without a human touching a mouse. It was built by Microsoft, and it's the same kind of tool as Selenium, just newer and, for most people, considerably easier to use correctly.

Why would an agent need a browser instead of a simple HTTP request?

  Reading rendered pages:
    A lot of the web is built with JavaScript that fills in content after the page loads. A plain HTTP request (e.g. requests.get) only sees the raw HTML the server sent, often close to empty. A real browser runs that JavaScript first, the same way it would for a person, so it sees the finished page.

  Clicking and typing:
    Some things on the web only exist behind an action: a button that reveals a form, a dropdown that has to be opened before an option can be picked. There's no URL for that, you have to actually interact with the page.

  Logging in:
    Many useful pages are behind a login. A browser can fill in a username and password and submit the form, exactly like a person would, then keep using the resulting session.

  Looking like a real visitor:
    Some sites treat plain HTTP requests, with no browser behind them, as bots and block them outright. A real browser, with a real rendering engine, looks like an ordinary visitor.
```

## Checkpoint

- **Browser automation**: controlling a real browser (Chromium,
  Firefox, or WebKit) with code instead of a mouse and keyboard.
- **Playwright**: the library this course uses to do that, built by
  Microsoft, and this course's sync API only, not the async one.
- **Why a browser, not just requests**: JavaScript-rendered content,
  clicking and typing, logging in, and looking like a real visitor
  rather than a bot.
- **This tier is AI-free**: the beginner tier is plain Python
  controlling a browser. The AI only shows up starting at Lesson 16.

If anything here still feels unclear, ask before moving to Lesson 2.
