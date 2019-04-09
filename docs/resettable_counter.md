ResettableCounter
=======
Basically the same thing as the `Counter` block but with an additional input that allows you to reset a group's cumulative count with an incoming signal. The `Counter` block includes a `reset` command that lets you reset all cumulative counts, but sometimes it is necessary to reset a count within a service.

The Counter block counts the number of signals that pass through the block. It outputs the `count`, which is the length of each incoming list of signals processed by the block, and a `cumulative_count` which is the total number of signals (a sum of all the previous `count`s) that have been processed by the block since the last reset.

Properties
----------
- **Reset Info**: If **resetting** is `True`, the *cumulative_count* output will reset after the specified interval or time. When **scheme** is set to `INTERVAL` then *cumulative_count* will reset every **interval**. When **scheme** is set to `CRON` then *cumulative_count* will reset at every **at** (in UTC time).

Advanced Properties
-------------------
- **Backup Interval**: An interval of time that specifies how often persisted data is saved.
- **Exclude Existing**: If checked (true), the attributes of the incoming signal will be excluded from the outgoing signal. If unchecked (false), the attributes of the incoming signal will be included in the outgoing signal.
- **Group By**: The signal attribute on the incoming signal whose values will be used to define groups on the outgoing signal.
- **Load From Persistence**: If `True`, the block’s state will be saved when the block is stopped, and reloaded once the block is restarted.

Inputs
------
- **count**: Any list of signals that should be counted
- **reset**: Signals to trigger a reset of the cumulative count. The signals must have the necessary group information on them in order to reset the proper group.

Outputs
-------
- **default**: Signal including the count, cumulative count, and group. On reset of a group a signal will be notified with a `count` of `0` and the `cumulative_count` having the cumulative count of the group at the time of reset.

Output Signal Attributes
------------------------
-   **count**: Number of signals that were sent into the signal.
-   **cumulative_count**: Number of signals since reset.
-   **group**: The group that the counts relate to as defined by `group_by`.

Commands
--------
- **groups**: Returns a list of the block’s current signal groupings.
- **reset**: Notifies a signal with `count` equal to 0 and `cumulative_count` equal to the cumulative count. The set of processed groups will be cleared.
