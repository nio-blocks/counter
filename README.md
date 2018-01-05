Counter
=======
The Counter block counts the number of signals that pass through the block. It outputs the `count`, which is the length of each incoming list of signals processed by the block, and a `cumulative_count` which is the total number of signals (a sum of all the previous `count`s) that have been processed by the block since the last reset.

Properties
----------
- **backup_interval**: An interval of time that specifies how often persisted data is saved.
- **enrich**: If checked (true), the attributes of the incoming signal will be excluded from the outgoing signal. If unchecked (false), the attributes of the incoming signal will be included in the outgoing signal.
- **group_by**: The signal attribute on the incoming signal whose values will be used to define groups on the outgoing signal.
- **load_from_persistence**: If `True`, the block’s state will be saved when the block is stopped, and reloaded once the block is restarted.
- **reset_info**: If **resetting** is `True`, the *cumulative_count* output will reset after the specified interval or time. When **scheme** is set to `INTERVAL` then *cumulative_count* will reset every **interval**. When **scheme** is set to `CRON` then *cumulative_count* will reset at every **at** (in UTC time).

Inputs
------
- **default**: Any list of signals.

Outputs
-------
- **default**: Signal including the count, cumulative count, and group.

Commands
--------
- **groups**: Returns a list of the block’s current signal groupings.
- **reset**: Notifies a signal with `count` equal to 0 and `cumulative_count` equal to the cumulative count. Cumulative count is then set to 0.

Dependencies
------------
[GroupBy Block Supplement](https://github.com/nio-blocks/block_supplements/tree/master/group_by)

Output Signal Attributes
------------------------
-   **count**: Number of signals that were sent into the signal.
-   **cumulative_count**: Number of signals since reset.
-   **group**: The group that the counts relate to as defined by `group_by`.

CounterFast
===========
The CounterFast block is a simplified version of the [Counter block](https://blocks.n.io/Counter).  It outputs the same *count* and *cumulative_count*, but does not allow for resetting, persistence, grouping, or signal enrichment.

Properties
----------
- **frequency**: If **report frequency?** is `True` (checked), a seperate signal will be output every **report interval** containing the *count_frequency*.  The *count_frequency* is the number of signals received per **averaging interval**.

Inputs
------
- **default**: Any list of signals.

Outputs
-------
- **default**: Signal including the *count*, and *cumulative_count*. Optional signal with the *count_frequency*

Commands
--------
- **reset**: Notifies a signal with `count` equal to 0 and `cumulative_count` equal to the cumulative count. Cumulative count is then set to 0.
- **value**: Returns the cumulative count.

Dependencies
------------
None

Output Signal Attributes
------------------------
-   `count`: Number of signals processed.
-   `cumulative_count`: Number of signals since last reset.

NumericCounter
==============
The NumericCounter block is the same as the [Counter block](https://blocks.n.io/Counter) but rather than summing the number of signals is sums the value of the incoming signal specified by the **count** property.  This allows for use of the cumulative count and reset functionality of the counter block, but does not require large numbers of signals to be passed if the count data is already available.

Properties
----------
- **backup_interval**: An interval of time that specifies how often persisted data is saved.
- **count_expr**: The incoming signal attribute value to sum and output as the *cumulative_count*.
- **enrich**: If checked (true), the attributes of the incoming signal will be excluded from the outgoing signal. If unchecked (false), the attributes of the incoming signal will be included in the outgoing signal.
- **group_by**: The signal attribute on the incoming signal whose values will be used to define groups on the outgoing signal.
- **load_from_persistence**: If `True`, the block’s state will be saved when the block is stopped, and reloaded once the block is restarted.
- **reset_info**: If **resetting** is `True`, *cumulative_count* will reset at a specified interval or time. When **scheme** is set to `INTERVAL` then *cumulative_count* will reset every **interval**. When **scheme** is set to `CRON` then *cumulative_count* will reset at every **at** (in UTC time).
- **send_zeroes**: If `False` (unchecked), an output signal will not be sent when the *count* = 0

Inputs
------
- **default**: Any list of signals.

Outputs
-------
- **default**: Signal including the count, cumulative count, and group.

Commands
--------
- **groups**: Returns a list of the block’s current signal groupings.
- **reset**: Notifies a signal with `count` equal to 0 and `cumulative_count` equal to the cumulative count. Cumulative count is then set to 0.

Dependencies
------------

Output Signal Attributes
------------------------
-   `count`: Number of signals that were sent into the signal.
-   `cumulative_count`: Number of signals since reset.
-   `group`: The group that the counts relate to as defined by `group_by`.

