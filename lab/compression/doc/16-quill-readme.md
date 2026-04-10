# Quill: Asynchronous Low Latency C++ Logging Library

## Overview

Quill is a high-performance asynchronous logging library written in C++17. It's designed for low-latency, performance-critical applications where microsecond response times matter.

## Key Characteristics

**Performance-Focused**: Consistently outperforms popular logging libraries in benchmarks.

**Feature-Rich**: Includes advanced capabilities for diverse logging needs.

**Battle-Tested**: Production-proven with extensive sanitizer testing and fuzzing across various inputs.

**Well-Documented**: Comprehensive guides and examples available.

**Community-Driven**: Open to contributions and feedback.

## Quick Start

### Installation

Available through multiple package managers:
- vcpkg: `vcpkg install quill`
- Conan: `conan install quill`
- Homebrew: `brew install quill`
- Meson WrapDB: `meson wrap install quill`
- Conda: `conda install -c conda-forge quill`

### Quickest Setup

```cpp
#include "quill/SimpleSetup.h"
#include "quill/LogFunctions.h"

int main()
{
  auto* logger = quill::simple_logger();
  quill::info(logger, "Hello from {}!", "Quill");
  
  auto* logger2 = quill::simple_logger("test.log");
  quill::warning(logger2, "This message goes to a file");
}
```

### Detailed Setup

```cpp
#include "quill/Backend.h"
#include "quill/Frontend.h"
#include "quill/LogMacros.h"
#include "quill/Logger.h"
#include "quill/sinks/ConsoleSink.h"

int main()
{
  quill::Backend::start();
  
  quill::Logger* logger = quill::Frontend::create_or_get_logger(
    "root", quill::Frontend::create_or_get_sink<quill::ConsoleSink>("sink_id_1"));
  
  LOG_INFO(logger, "Hello from {}!", "Quill");
}
```

## Core Features

- **High-Performance**: Ultra-low latency with asynchronous background processing
- **Asynchronous Processing**: Background thread handles formatting and I/O
- **Minimal Header Includes**: Lightweight frontend headers, single backend `.cpp` file
- **Compile-Time Optimization**: Eliminate specific log levels at compile time
- **Custom Formatters**: Define custom log output patterns
- **Timestamp-Ordered Logs**: Chronologically ordered logs for multithreaded debugging
- **Flexible Timestamps**: Support for rdtsc, chrono, or custom clocks
- **Backtrace Logging**: Ring buffer storage for on-demand display
- **Multiple Output Sinks**: Console (with color), files (with rotation), JSON, custom sinks
- **Log Filtering**: Process only relevant messages
- **JSON Logging**: Structured log output
- **Configurable Queue Modes**: Bounded/unbounded and blocking/dropping options
- **Crash Handling**: Built-in signal handler for log preservation
- **Huge Pages Support**: Linux huge pages optimization
- **Wide Character Support**: Windows ASCII-encoded wide strings compatibility
- **Exception-Free Option**: Configurable builds with/without exceptions
- **Clean Codebase**: Warning-free at strict compiler levels
- **Type-Safe API**: Built on the {fmt} library

## Performance Benchmarks

### System Configuration
- **OS**: Linux RHEL 9.4
- **CPU**: Intel Core i5-12600 @ 4.8 GHz
- **Compiler**: GCC 13.1
- **Measurements**: Nanoseconds (lower is better)

### Logging Numbers (1 Thread)

| Library | 50th | 75th | 90th | 95th | 99th | 99.9th |
|---------|------|------|------|------|------|--------|
| Quill Bounded Dropping | 8 | 8 | 9 | 9 | 10 | 12 |
| Quill Unbounded | 8 | 8 | 9 | 9 | 11 | 13 |
| fmtlog | 8 | 9 | 9 | 10 | 12 | 13 |
| PlatformLab NanoLog | 13 | 14 | 16 | 18 | 21 | 24 |
| MS BinLog | 21 | 21 | 21 | 22 | 59 | 93 |
| spdlog | 145 | 148 | 151 | 154 | 162 | 171 |

### Logging Numbers (4 Threads)

| Library | 50th | 75th | 90th | 95th | 99th | 99.9th |
|---------|------|------|------|------|------|--------|
| Quill Unbounded | 8 | 9 | 9 | 9 | 12 | 15 |
| fmtlog | 8 | 9 | 9 | 10 | 12 | 13 |
| XTR | 7 | 8 | 9 | 10 | 32 | 39 |
| Quill Bounded Dropping | 8 | 9 | 10 | 11 | 13 | 15 |

### Large Strings (1 Thread)

| Library | 50th | 75th | 90th | 95th | 99th | 99.9th |
|---------|------|------|------|------|------|--------|
| fmtlog | 10 | 12 | 13 | 13 | 15 | 17 |
| Quill Unbounded | 11 | 12 | 14 | 14 | 16 | 18 |
| Quill Bounded Dropping | 12 | 13 | 14 | 15 | 16 | 19 |
| MS BinLog | 23 | 23 | 24 | 25 | 62 | 96 |

## Architecture

### Frontend (Caller Thread)
The frontend captures log messages with minimal overhead using lock-free queues. The caller thread only enqueues the message and returns immediately.

### Backend
The backend thread handles:
- Message formatting
- File I/O operations
- Sink management
- All heavy lifting asynchronously

## Integration Methods

### External CMake
Install Quill separately and link in your CMakeLists.txt:
```cmake
find_package(quill REQUIRED)
target_link_libraries(your_target PRIVATE quill::quill)
```

### Embedded CMake
Include Quill as a subdirectory in your project and use `add_subdirectory()`.

## Design Philosophy

Quill separates concerns between the caller thread (frontend) and background processing (backend). This architecture minimizes latency on the critical path while handling intensive operations asynchronously.

## License

Quill is released under the MIT License.
