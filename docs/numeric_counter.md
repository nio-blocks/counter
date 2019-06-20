NumericCounter
==============
The NumericCounter block is the same as the `Counter` block but rather than summing the number of signals is sums the value of the incoming signal specified by the **count** property.  This allows for use of the cumulative count and reset functionality of the counter block, but does not require large numbers of signals to be passed if the count data is already available.

Properties
----------
- **Count**: The incoming signal attribute value to sum and output as the *cumulative_count*.
- **Send Zero Counts**: If `False` (unchecked), an output signal will not be sent when the *count* = 0
- **Reset Info**: If **resetting** is `True`, the *cumulative_count* output will reset after the specified interval or time. When **scheme** is set to `INTERVAL` then *cumulative_count* will reset every **interval**. When **scheme** is set to `CRON` then *cumulative_count* will reset at every **at** (in UTC time).

Advanced Properties
-------------------
- **Clear Groups on Reset**: If `True`, when reset `_groups` and `_cumulative_count` will be emptied.
- **Emit Signals on Reset**: If `True` (default), when reset a signal will be notified for each group with the `cumulative_count` since last reset, and a `count` value of 0.
- **Exclude Existing**: If checked (true), the attributes of the incoming signal will be excluded from the outgoing signal. If unchecked (false), the attributes of the incoming signal will be included in the outgoing signal.
- **Group By**: The signal attribute on the incoming signal whose values will be used to define groups on the outgoing signal.
- **Load From Persistence**: If `True`, the block’s state will be saved when the block is stopped, and reloaded once the block is restarted.

Inputs
------
- **default**: Any list of signals.

Outputs
-------
- **default**: Signal including the count, cumulative count, and group.

Output Signal Attributes
------------------------
-   `count`: Number of signals that were sent into the signal.
-   `cumulative_count`: Number of signals since reset.
-   `group`: The group that the counts relate to as defined by `group_by`.

Commands
--------
- **groups**: Returns a list of the block’s current signal groupings.
- **reset**: Notifies a signal with `count` equal to 0 and `cumulative_count` equal to the cumulative count. Cumulative count is then set to 0.
