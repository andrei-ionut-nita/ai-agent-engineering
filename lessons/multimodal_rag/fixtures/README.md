Five short notes (`notes/`) plus four synthetic diagram images and one
single-page PDF (`images/`), used by every lesson in this course. Every
image (and the PDF's embedded image) encodes a specific fact that its
matching note deliberately omits, on purpose, so retrieval over text
alone genuinely cannot answer certain questions, only retrieval over
the images can. This is what makes Lesson 7's cross-modal retrieval
demo real rather than staged.

## How the images were made

All four are generated with Pillow (`PIL.ImageDraw`), not photographs,
drawn shapes, lines, and text labels standing in for a hand-drawn
diagram or an annotated photo. That's enough for this course's purpose:
Gemini's image understanding works the same way over a synthetic
diagram as over a real photo, and a synthetic image keeps the fixture
set small, deterministic, and free of any real-world sourcing or
licensing question. The generation script is not part of the lesson
content; the point is the images themselves and what's readable in
them.

## The four images, and what each hides from its note

| Image | Belongs to | What the image shows | Fact that is NOT in the text note |
|---|---|---|---|
| `observatory-finder-scope.png` | `home-observatory.md` (fig. 1) | A finder-scope crosshair diagram | Alignment offset: **3 mm left, 2 mm up** |
| `observatory-mount-wiring.png` | `home-observatory.md` (fig. 2) | Motor wiring between the RA and DEC motors | Cable color code: **RA = red, DEC = blue** |
| `starter-jar-markings.png` | `sourdough-starter.md` | A jar with two rubber-band fill lines | Feed line **150 mL**, discard line **50 mL** |
| `derailleur-hanger-diagram.png` | `bike-repair.md` | A rear derailleur hanger close-up | Torque spec printed on the part: **8 Nm** |
| `circuit-board-notebook.pdf` | `circuit-board.md` | A one-page PDF (built with `Image.save(..., "PDF")`) whose single embedded image is a scanned notebook page | Pin 3 output frequency: **2 Hz** |

`circuit-board-notebook.pdf` is used starting in Lesson 17 (extracting
images embedded in a PDF page, via `pypdf`'s `page.images`), the only
fixture that isn't a plain `.png`, standing in for how a real document
often arrives as a PDF with figures embedded inside it rather than as
separate image files.

`home-observatory.md` is the only note with two figures, used starting
in Lesson 10 (captioning multiple images per document). The other two
notes with images (`sourdough-starter.md`, `bike-repair.md`) each have
exactly one. `terrarium.md` and `circuit-board.md` have no images at
all, on purpose, so this course's mixed store always has some documents
that are text-only, keeping "modality" a real per-chunk attribute
rather than something true of every chunk.

Each note text explicitly *mentions* that a photo exists ("see fig. 1",
"see jar photo") without repeating what's in it, mirroring how a real
note-taker actually behaves: the photo is the record of the detail, the
prose is just a pointer to it. A question like "What's the torque spec
on the derailleur hanger bolt?" has no answer anywhere in
`bike-repair.md`'s text, embedding and retrieving that note's text chunk
will never surface "8 Nm", only captioning and embedding
`derailleur-hanger-diagram.png` can. That's the case Lesson 7 uses to
prove cross-modal retrieval is doing real work, not just narrating it.
