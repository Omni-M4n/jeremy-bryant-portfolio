# Guided case: review after your first attempt

The guided input is `Mira' OR '1'='1`. In the joined route, the first
apostrophe ends the name value. The added equality is true for each of the
three rows. The result therefore contains IDs 1, 2 and 3, with status 200.

In the bound route, the entire supplied value stays a name. No reader has
that full name, so status 200 contains an empty rows list. The fix is not
“block apostrophes”; it keeps the name separate from the query structure.

Check `O'Reed` in the changed case and `Mira` in your ordinary-input retest.
The bound route must still support those legitimate names. Save exact row
IDs and the supplied read-only scope. The finding applies only to `/joined`
in this toy app; do not turn it into a claim about other sites.
