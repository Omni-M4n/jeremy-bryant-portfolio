# Guided case: review after your first attempt

The first order sends `"Pear"` and integer `2`. It meets both field rules,
so status 201 returns the accepted order.

The second sends `"2"`, a string. It is valid JSON, but it is the wrong type
for count. Status 422 gives the public schema rule. The third omits count and
also gets 422. These are validation failures, not internal server errors.

Expected status sequence: 201, 422, 422. Check the actual error bodies for
unexpected internal information. Then use the changed case to examine the
edges. “Looks like a number” is not enough to meet the count rule.
