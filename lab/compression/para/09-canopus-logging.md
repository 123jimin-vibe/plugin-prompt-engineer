## Behavior

Optional. Any thread enqueues log entries without blocking via lock-free MPSC queue. A low-priority background thread writes to file. Initialized first so all subsequent init can log.

## Constraints

- Must never stall or add latency to any other thread.

## Anticipated Changes

- Planned to use Quill as the logging library.

## Dangers

- Queue overflow silently loses diagnostic data.
