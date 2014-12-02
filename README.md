Counter
=======

Counts the number of signals that pass through the block. It outputs the *count* for each list of signals that is processed by the block and a *cumluative_count* which is the total number signals that have been processed by the block since the last rest.

Signals can optionally be grouped using the *group_by* property. This is an evaluable expression that will group the counts and specify the group in the *group* attribute on the output signal.

Persistance is used to maintain the cumulative count between stopping and starting the block.

The cumulative count can be reset by using the *reset* command or by using one of the **reset_info** options. The **reset_info** properties allow for configuration of the block to reset the cumulative count based on a recurring *INTERVAL* or a specific time by using the *CRON* setting. On reset, a signal is notified. It contains the *cumulative_count* right before the reset and the *count* is zero. 

Properties
--------------

-   **reset_info**: If **resetting** is true, *cumulative_count* will reset at a specified interval or time. When **scheme** is set to *INTERVAL* then *cumulative_count* will reset every **interval**. When **scheme** is set to *CRON* then *cumulative_count* will reset at every **at** (in UTC time).
-   **group_by**: Expression proprety. The value by which signals are grouped. Output signals will have *group* set to this value.


Dependencies
----------------
[GroupBy Block Supplement](https://github.com/nio-blocks/block_supplements/tree/master/group_by)

Commands
----------------

-   **reset**: Notifes a signal with *count* equal to 0 and *cumulative_count* equal to the cumulative count. Cumulative count is then set to 0.

Input
-------
Any list of signals.

Output
---------

-   **count**: Number of signals that were sent into the signal.
-   **cumulative_count**: Number of signals since reset.
-   **group**: The group that the counts relate to as defined by **group_by**.
