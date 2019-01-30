CounterFast
===========
The CounterFast block is a simplified version of the `Counter` block.  It outputs the same *count* and *cumulative_count*, but does not allow for resetting, persistence, grouping, or signal enrichment.

Properties
----------
- **frequency**: If **report frequency?** is `True` (checked), a seperate signal will be output every **report interval** containing the *count_frequency*.  The *count_frequency* is the number of signals received per **averaging interval**.

Inputs
------
- **default**: Any list of signals.

Outputs
-------
- **default**: Signal including the *count*, and *cumulative_count*. Optional signal with the *count_frequency*

Output Signal Attributes
------------------------
-   `count`: Number of signals processed.
-   `cumulative_count`: Number of signals since last reset.

Commands
--------
- **reset**: Notifies a signal with `count` equal to 0 and `cumulative_count` equal to the cumulative count. Cumulative count is then set to 0.
- **value**: Returns the cumulative count.

Dependencies
------------
None
