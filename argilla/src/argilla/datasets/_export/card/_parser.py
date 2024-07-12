AVAILABLE_SIZE_CATEGORIES = {
    1_000: "n<1K",
    10_000: "1K<n<10K",
    100_000: "10K<n<100K",
    1_000_000: "100K<n<1M",
    10_000_000: "1M<n<10M",
    100_000_000: "10M<n<100M",
    1_000_000_000: "100M<n<1B",
    10_000_000_000: "1B<n<10B",
    100_000_000_000: "10B<n<100B",
    1_000_000_000_000: "100B<n<1T",
}


def size_categories_parser(input_size: int) -> str:
    for size, category in AVAILABLE_SIZE_CATEGORIES.items():
        if input_size < size:
            return category
    return "n>1T"
