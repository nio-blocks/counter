TallyCounter
=======
An extension of the [Counter](docs/counter.md) block, incoming signals are enriched with the total cumulative count for all groups processed since the last reset.

Properties
----------
- **Reset Info**: If **resetting** is `True`, the *cumulative_count* output will reset after the specified interval or time. When **scheme** is set to `INTERVAL` then *cumulative_count* will reset every **interval**. When **scheme** is set to `CRON` then *cumulative_count* will reset at every **at** (in UTC time).

Advanced Properties
-------------------
- **Clear Groups on Reset**: If `True`, when reset `_groups` and `_cumulative_count` will be emptied.
- **Exclude Existing**: If checked (true), the attributes of the incoming signal will be excluded from the outgoing signal. If unchecked (false), the attributes of the incoming signal will be included in the outgoing signal.
- **Group By**: The signal attribute on the incoming signal whose values will be used to define groups on the outgoing signal.
- **Load From Persistence**: If `True`, the block’s state will be saved when the block is stopped, and reloaded once the block is restarted.

Inputs
------
- **default**: Any list of signals.

Outputs
-------
- **default**: Signal including the `count`, `group`, and `tally`.

Output Signal Attributes
------------------------
-   **count**: Number of signals that were sent into the signal.
-   **tally**: Dictionary of all groups and their cumulative counts since reset.
-   **group**: The group that the counts relate to as defined by `group_by`.

Commands
--------
- **groups**: Returns a list of the block’s current signal groupings.
- **reset**: Notifies a signal with `count` equal to 0 and `cumulative_count` equal to the cumulative count. The group(s) reset are removed from `tally`
