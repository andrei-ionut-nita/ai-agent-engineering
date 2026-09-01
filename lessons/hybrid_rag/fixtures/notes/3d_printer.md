# 3D Printer Notes

Prints had started coming out with faint horizontal ridges on every
vertical wall, visible even on parts that used to come out glass-smooth
on this same printer. Every slicer setting was checked and re-checked,
layer height, print speed, cooling, all unchanged from before the
problem started.

The actual cause was a worn brass nozzle. It had quietly gone from
0.4mm to closer to 0.44mm after enough hours of printing abrasive
filament, widening the extrusion just enough to leave visible ridging.
Swapping in a new hardened-steel CHT nozzle, part number E3D-CHT-04,
brought the walls back to smooth immediately, and should hold up far
longer against the abrasive filament than brass did.

Nothing about the slicer profile needed to change at all, which is
what made this one so slow to track down, everyone assumed a setting
had drifted rather than the nozzle itself wearing out.
