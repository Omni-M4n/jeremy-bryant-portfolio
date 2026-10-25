# Worked example: Library resource register

Open this after your guided prediction. Today is day 10. r1 expires on day
10, so its tag calls for review now. Use `review-due`. r2 has no owner or
expiry value, so use `owner-missing+expiry-missing`.
These findings call for review. They are not orders to delete items.

r1 depends on r2. Draw `r1 -> r2`, which means r1 uses r2.
The plan deletes only r1. Nothing depends on r1, and it has no hold.
Use `plan=order-valid-in-model`.

r2 remains. Its daily cost is 2 practice units, so use `cost=residual-cost`.
The running total of 80 is below the alert level of 100.
Use `budget=below-alert-threshold`. Neither result promises a spending cap.

A useful handover says: "The order works for the links shown here.
But r2 remains at 2 units per day and needs an owner."
This explains more than saying the removal work is done.
