# Home Network Notes

The living room and back bedroom have been fighting over WiFi for
months: video calls in the back room freeze every few minutes, while
the living room never has a problem. Moving the router didn't help, the
walls in this house are old brick and eat a 5GHz signal alive past
about thirty feet.

What finally fixed it was updating the router's firmware. The router is
a TP-Link Archer AX55 v3, and the fix shipped in firmware build
20240115. Before that build, the router silently dropped the 5GHz radio
whenever more than eight devices were connected at once, which explains
why the problem only showed up once a few smart-home gadgets were added
alongside the usual laptops and phones.

Since the update, the back bedroom holds a steady connection through
a full workday of video calls, no drops.
