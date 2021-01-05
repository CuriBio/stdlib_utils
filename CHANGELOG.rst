Changelog for stdlib_utils
==========================


0.3.11 (2020-12-31)
-------------------

- Added timeout_secs kwarg to ``safe_get`` and ``drain_queue``.


0.3.10 (2020-12-14)
-------------------

- Added pause and unpause methods to ``InfiniteLoopingParallelismMixIn``.


0.3.8 (2020-12-10)
------------------

- Added ``confirm_parallelism_is_stopped``.


0.3.7 (2020-12-08)
------------------

- Added ``confirm_queue_is_eventually_empty``.


0.3.6 (2020-11-12)
------------------

- Added ``confirm_queue_is_eventually_of_size``. Note, this is currently not supported on MacOS because MacOS does not implement ``queue.qsize()``.

- Added 50 msec delay between polling to check if queue was empty or checking ``qsize``.


0.3.5 (2020-10-23)
------------------

- Added ``is_queue_eventually_of_size``. Note, this is currently not supported on MacOS because MacOS does not implement ``queue.qsize()``.


0.3.2 (2020-10-22)
------------------

- Added kwarg for ``is_queue_eventually_empty`` and ``is_queue_eventually_empty`` for timeout.

- Added ``put_object_into_queue_and_raise_error_if_eventually_still_empty`` helper function for unit testing.


0.3.1 (2020-09-17)
------------------

- Added notebook logging format.


0.3.0 (2020-09-11)
------------------

- Added tracking of 5 longest iterations to ``InfiniteLoopingParallelismMixIn``.
