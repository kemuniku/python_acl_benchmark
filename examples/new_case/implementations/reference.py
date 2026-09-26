"""Add other .py files here with LABEL and run(data) to compare them.

For code in this repository, omit SOURCE. External dependencies instead use
SOURCE = "<sources.lock.json key>"; the runner imports that pinned source.
"""

LABEL = "Local prefix sums (reference)"


def run(data):
    # Build fresh state on every invocation. Never modify data or retain state.
    total = 0
    result = []
    for value in data["values"]:
        total += value
        result.append(total)
    return result
