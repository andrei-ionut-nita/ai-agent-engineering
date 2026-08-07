# Lesson 10: Filling and submitting forms

## Why forms deserve their own lesson

A form is the main way a human hands structured input to a web page:
a username, a password, a checkbox for "remember me," a dropdown for
"country." An agent that can browse but can't fill in a form can only
read the web, never act on it. This lesson covers the three form
controls you'll meet constantly: text fields, checkboxes, and
dropdowns, plus how to confirm a submission actually worked instead of
just hoping.

## The code, piece by piece

```python
page.locator("#username").fill("agent-student")
page.locator("#password").fill("does-not-matter")
```

`.fill()` clears the field first, then types the given text in one
step. That matters: if you used `.type()` instead (which simulates
individual keystrokes, appending to whatever's already there), any
placeholder or pre-filled value would still be sitting in the field,
mixed in with your new text. `.fill()` is almost always what you want
for form inputs.

```python
page.locator("input[type='submit']").click()
```

Submitting a form is nothing special, it's just clicking the button
that triggers it. Playwright doesn't distinguish "submit" from any
other click.

```python
logged_in = page.locator("a[href='/logout']").is_visible()
```

Never assume a form submission worked just because the click didn't
error. Check for real evidence: here, a "Logout" link only exists on
the page after a successful login. `.is_visible()` returns `True` or
`False` immediately, it doesn't wait or raise, which makes it the
right tool for a yes/no check like this (compare that to
`.wait_for_selector()` from Lesson 9, which blocks until something
appears or times out).

```python
checkboxes.nth(0).check()
checkboxes.nth(1).uncheck()
```

`.locator()` can match more than one element at once; `.nth(0)` picks
the first match, `.nth(1)` the second. `.check()` and `.uncheck()` are
**idempotent**: calling `.check()` on a box that's already checked
does nothing, no error, no double-toggle. That's different from
`.click()`, which would flip whatever state the box was already in.
When you know the exact end state you want, prefer `.check()` /
`.uncheck()` over `.click()`.

```python
dropdown.select_option(label="Option 2")
```

`.select_option()` targets a real HTML `<select>` element. You can
choose by `value` (the underlying attribute), `label` (what's visible
on screen), or `index` (position). Picking by `label` is usually the
most readable choice, since it matches what a human sees.

## Running it

```bash
uv run python lessons/playwright/02_intermediate/10_filling_and_submitting_forms/lesson.py
```

## Expected output

```
1. Login form (text fields + submit):
   Logged in successfully: True

2. Checkboxes:
   Checkbox 1 checked: True, checkbox 2 checked: False

3. Dropdown:
   Selected option: Option 2
```

## Checkpoint

- **`.fill()`**: clears a field, then sets its value in one step, the
  right choice for text inputs.
- **Submitting a form**: just a normal `.click()` on the button that
  triggers it, nothing special.
- **Confirming success**: check for real evidence the action worked
  (a new element, a changed URL), don't assume a click without an
  error means success.
- **`.check()` / `.uncheck()`**: idempotent, they set a specific end
  state; `.click()` just toggles whatever state was already there.
- **`.select_option()`**: picks an option from a `<select>` dropdown,
  by value, label, or index.

If anything here still feels unclear, ask before moving to Lesson 11.
