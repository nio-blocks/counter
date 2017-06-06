Counter Blocks
==============

This repository comprises several different types of counters.
 * [Counter](#counter)
 * [CounterFast](#counterfast)
 * [NumericCounter](#numericcounter)

***

Counter
=======

Counts the number of signals that pass through the block. It outputs the `count` for each list of signals that is processed by the block and a `cumulative_count` which is the total number of signals that have been processed by the block since the last rest.

Signals can optionally be grouped using the `group_by` property. This is an evaluable expression that will group the counts and specify the group in the `group` attribute in the output signal.

Persistence is used to maintain the cumulative count between stopping and starting the block.

The cumulative count can be reset by using the *reset* command or by using one of the `reset_info` options. The `reset_info` properties allow for configuration of the block to reset the cumulative count based on a recurring `INTERVAL` or a specific time by using the `CRON` setting. On reset, a signal is notified. It contains the *cumulative_count* right before the reset and the *count* is zero.

Properties
--------------

-   **reset_info**: If **resetting** is `True`, *cumulative_count* will reset at a specified interval or time. When **scheme** is set to `INTERVAL` then *cumulative_count* will reset every **interval**. When **scheme** is set to `CRON` then *cumulative_count* will reset at every **at** (in UTC time).
-   **group_by**: The value by which signals are grouped. Output signals will have `group` set to this value.


Dependencies
----------------
[GroupBy Block Supplement](https://github.com/nio-blocks/block_supplements/tree/master/group_by)

Commands
----------------

-   **reset**: Notifies a signal with `count` equal to 0 and `cumulative_count` equal to the cumulative count. Cumulative count is then set to 0.

Input
-------
Any list of signals.

Output
---------

-   **count**: Number of signals that were sent into the signal.
-   **cumulative_count**: Number of signals since reset.
-   **group**: The group that the counts relate to as defined by `group_by`.

***

CounterFast
===========

A faster counter that ignores groups and provides functionality to return signal frequency over a configured period. There is no interaction with persistence.

The cumulative count can be reset by the *reset* command.

Properties
----------

- **frequency**:
   * **enabled** (type:bool): Is frequency reporting enabled?
   * **report_interval** (type:timedelta): The interval at which to report frequencies.
   * **averaging_interval** (type:timedelta): The interval over which to calculate frequencies.

Dependencies
------------

None

Commands
--------

- **reset**: Cumulative count is then set to 0. Returns `True`.
- **value**: Returns the cumulative count.

Input
-------
Any list of signals.

Output
---------

-   `count`: Number of signals processed.
-   `cumulative_count`: Number of signals since last reset.

***

NumericCounter
=======

The same as the [Counter Block](#counter) but it expects count values to be passed to the block rather than lists of signals to be counted.

This allows for use of the cumulative count and reset functionality of the counter block, but does not require large numbers of signals to be passed if count data is already available.

Properties
--------------

-   **count_expr**: (type:expression) The expression to be applied to each signal to extract the count
-   **reset_info**: If **resetting** is `True`, `cumulative_count` will reset at a specified interval or time. When **scheme** is set to `INTERVAL` then `cumulative_count` will reset every **interval**. When **scheme** is set to `CRON` then `cumulative_count` will reset at every **at** (in UTC time).
-   **group_by**: The value by which signals are grouped. Output signals will have `group` set to this value.


Dependencies
----------------
[GroupBy Block Supplement](https://github.com/nio-blocks/block_supplements/tree/master/group_by)

Commands
----------------

-   **reset**: Notifies a signal with `count` equal to 0 and `cumulative_count` equal to the cumulative count. Cumulative count is then set to 0.

Input
-------
Any list of signals.

Output
---------

-   `count`: Number of signals that were sent into the signal.
-   `cumulative_count`: Number of signals since reset.
-   `group`: The group that the counts relate to as defined by `group_by`.
