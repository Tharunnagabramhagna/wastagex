
import csv
import math
import numpy as np

from pathlib import Path
from collections import Counter, defaultdict


# ============================================================
# WASTAGEX - FOOD LOSS INTELLIGENCE SYSTEM
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATASET_PATH = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "FoodBalanceSheets_E_All_Data.csv"
)

OUTPUT_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "food_losses_cleaned.csv"
)

REPORT_PATH = (
    PROJECT_ROOT
    / "reports"
    / "analysis_report.txt"
)

MISSING_MARKERS = {
    "", "..", "...", "na", "n/a", "nan", "null"
}


# ============================================================
# TASK 1: IDENTIFY YEAR COLUMNS
# ============================================================

def get_year_columns(headers):

    return [
        column for column in headers
        if column.startswith("Y")
        and column[1:].isdigit()
    ]


# ============================================================
# TASK 2: PROCESS AND CLEAN THE ORIGINAL DATASET
# ============================================================

def process_dataset():

    if not DATASET_PATH.exists():
        raise FileNotFoundError(
            f"Dataset not found: {DATASET_PATH}"
        )

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    total_records = 0
    malformed_records = 0
    loss_records = 0

    valid_observations = 0
    missing_observations = 0
    invalid_observations = 0
    negative_observations = 0

    element_counts = Counter()
    unit_counts = Counter()

    countries = set()
    commodities = set()

    sample_records = []

    print("\n" + "=" * 60)
    print("             WASTAGEX DATA PROCESSING")
    print("=" * 60)

    with open(
        DATASET_PATH,
        "r",
        encoding="cp1252",
        newline=""
    ) as source:

        reader = csv.DictReader(source)

        headers = reader.fieldnames

        if not headers:
            raise ValueError("CSV has no headers.")

        year_columns = get_year_columns(headers)

        if not year_columns:
            raise ValueError("No year columns found.")

        required_columns = [
            "Area",
            "Item",
            "Element",
            "Unit"
        ]

        missing_columns = [
            column for column in required_columns
            if column not in headers
        ]

        if missing_columns:
            raise ValueError(
                f"Missing columns: {missing_columns}"
            )

        metadata_columns = [
            column for column in [
                "Area Code",
                "Area Code (M49)",
                "Area",
                "Item Code",
                "Item Code (FBS)",
                "Item",
                "Element Code",
                "Element",
                "Unit"
            ]
            if column in headers
        ]

        output_columns = metadata_columns + [
            "Year",
            "Losses",
            "Source_Flag",
            "Review_Note"
        ]

        # Locate the annual source flag columns.

        flag_columns = {}

        for year_column in year_columns:

            year_number = year_column[1:]

            candidates = [
                f"F{year_number}",
                f"{year_column}F",
                f"{year_column}_Flag",
                f"Flag_{year_column}",
                f"Flag{year_column}"
            ]

            flag_columns[year_column] = next(
                (
                    name for name in candidates
                    if name in headers
                ),
                ""
            )

        print("\n1. DATASET STRUCTURE")
        print("-" * 60)

        print("Total columns:", len(headers))
        print("Number of years:", len(year_columns))
        print("Available years:", ", ".join(year_columns))

        with open(
            OUTPUT_PATH,
            "w",
            encoding="utf-8-sig",
            newline=""
        ) as target:

            writer = csv.DictWriter(
                target,
                fieldnames=output_columns
            )

            writer.writeheader()

            print("\n2. FILTERING FOOD-LOSS RECORDS...")

            for row in reader:

                if row is None:
                    continue

                total_records += 1

                # Reject rows with malformed column structure.

                if (
                    None in row
                    or any(
                        row.get(column) is None
                        for column in headers
                    )
                ):
                    malformed_records += 1
                    continue

                element = (
                    row.get("Element") or ""
                ).strip()

                element_counts[element] += 1

                if element.casefold() != "losses":
                    continue

                loss_records += 1

                area = (row.get("Area") or "").strip()
                item = (row.get("Item") or "").strip()
                unit = (row.get("Unit") or "").strip()

                for year_column in year_columns:

                    raw_value = (
                        row.get(year_column) or ""
                    ).strip()

                    if raw_value.casefold() in MISSING_MARKERS:
                        missing_observations += 1
                        continue

                    # Convert text to a numerical value.

                    try:
                        value = float(raw_value)

                        if not math.isfinite(value):
                            raise ValueError()

                    except ValueError:
                        invalid_observations += 1
                        continue

                    if not unit:
                        invalid_observations += 1
                        continue

                    review_note = ""

                    if value < 0:
                        negative_observations += 1
                        review_note = "Negative value - review source"

                    # Find the associated source flag.

                    flag_column = flag_columns[year_column]

                    source_flag = (
                        row.get(flag_column, "")
                        if flag_column else ""
                    )

                    cleaned_record = {
                        column: row.get(column) or ""
                        for column in metadata_columns
                    }

                    cleaned_record.update({
                        "Year": year_column[1:],
                        "Losses": value,
                        "Source_Flag": source_flag,
                        "Review_Note": review_note
                    })

                    writer.writerow(cleaned_record)

                    valid_observations += 1
                    unit_counts[unit] += 1

                    countries.add(area)
                    commodities.add(item)

                    if len(sample_records) < 5:
                        sample_records.append(cleaned_record.copy())

    print("\n3. CLEANING SUMMARY")
    print("-" * 60)

    print(f"Total original records: {total_records:,}")
    print(f"Malformed records: {malformed_records:,}")
    print(f"Original loss records: {loss_records:,}")
    print(f"Valid yearly observations: {valid_observations:,}")
    print(f"Missing observations: {missing_observations:,}")
    print(f"Invalid observations: {invalid_observations:,}")
    print(f"Negative observations for review: {negative_observations:,}")

    print(f"Unique countries: {len(countries):,}")
    print(f"Unique commodities: {len(commodities):,}")

    print("\n4. MEASUREMENT UNITS")
    print("-" * 60)

    for unit, count in unit_counts.most_common():
        print(f"{unit}: {count:,}")

    print("\n5. FIRST FIVE CLEANED RECORDS")
    print("-" * 60)

    for index, record in enumerate(sample_records, start=1):

        print(f"\nRecord {index}")

        for key, value in record.items():
            print(f"{key}: {value}")

    print("\nCleaned dataset saved:")
    print(OUTPUT_PATH)


# ============================================================
# TASK 3: NUMPY STATISTICAL ANALYSIS
# ============================================================

def analyze_statistics(values_by_unit, log):

    log("\n" + "=" * 60)
    log("NUMPY STATISTICAL ANALYSIS")
    log("=" * 60)

    for unit, values in sorted(values_by_unit.items()):

        data = np.array(values, dtype=float)

        if data.size == 0:
            continue

        mean_value = np.mean(data)
        median_value = np.median(data)
        std_value = np.std(data, ddof=0)

        max_value = np.max(data)
        min_value = np.min(data)

        q25 = np.percentile(data, 25)
        q75 = np.percentile(data, 75)

        log(f"\nMeasurement unit: {unit}")
        log(f"Valid observations: {data.size:,}")

        log(f"Mean: {mean_value:.3f}")
        log(f"Median: {median_value:.3f}")
        log(f"Standard deviation: {std_value:.3f}")

        log(f"Maximum: {max_value:.3f}")
        log(f"Minimum: {min_value:.3f}")

        log(f"25th percentile: {q25:.3f}")
        log(f"75th percentile: {q75:.3f}")


# ============================================================
# TASK 4: COUNTRY AND COMMODITY ANALYSIS
# ============================================================

def display_group_analysis(title, groups, unit, log):

    log("\n" + "=" * 60)
    log(title)
    log("=" * 60)

    # Include groups having at least five observations.

    results = []

    for (group_unit, name), details in groups.items():

        if group_unit != unit:
            continue

        total, count = details

        if count < 5:
            continue

        average = total / count

        results.append((name, average, count))

    results.sort(
        key=lambda record: record[1],
        reverse=True
    )

    if not results:
        log("No groups have enough observations.")
        return

    for rank, (name, average, count) in enumerate(
        results[:10],
        start=1
    ):

        log(
            f"{rank}. {name} | "
            f"Average: {average:.3f} {unit} | "
            f"Observations: {count:,}"
        )


# ============================================================
# TASK 5: YEAR-WISE TREND ANALYSIS
# ============================================================

def display_yearly_analysis(year_groups, unit, log):

    log("\n" + "=" * 60)
    log("YEAR-WISE FOOD-LOSS OBSERVATION ANALYSIS")
    log("=" * 60)

    yearly_results = []

    for (group_unit, year), details in year_groups.items():

        if group_unit != unit:
            continue

        total, count = details

        if count == 0:
            continue

        average = total / count

        yearly_results.append(
            (year, average, count)
        )

    yearly_results.sort(key=lambda record: record[0])

    for year, average, count in yearly_results:

        log(
            f"{year} | "
            f"Average: {average:.3f} {unit} | "
            f"Observations: {count:,}"
        )


# ============================================================
# TASK 6: READ CLEANED DATA AND GENERATE REPORT
# ============================================================

def analyze_and_generate_report():

    if not OUTPUT_PATH.exists():
        raise FileNotFoundError(
            "Cleaned CSV not found."
        )

    REPORT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    report_lines = []

    def log(message=""):
        print(message)
        report_lines.append(str(message))

    # Group data using dictionaries.

    values_by_unit = defaultdict(list)

    country_groups = defaultdict(lambda: [0.0, 0])
    commodity_groups = defaultdict(lambda: [0.0, 0])
    year_groups = defaultdict(lambda: [0.0, 0])

    flag_counts = Counter()

    total_records = 0
    used_records = 0
    negative_records = 0
    invalid_records = 0

    log("\nLoading cleaned dataset for analysis...")

    with open(
        OUTPUT_PATH,
        "r",
        encoding="utf-8-sig",
        newline=""
    ) as file:

        reader = csv.DictReader(file)

        for row in reader:

            total_records += 1

            # Count source flags.

            flag = (row.get("Source_Flag") or "").strip()

            flag_counts[
                flag if flag else "Not available"
            ] += 1

            # Convert observations.

            try:
                value = float(row["Losses"])

                if not math.isfinite(value):
                    raise ValueError()

            except (ValueError, TypeError):
                invalid_records += 1
                continue

            # Negative records need separate review.

            if value < 0:
                negative_records += 1
                continue

            unit = (row.get("Unit") or "").strip()
            area = (row.get("Area") or "").strip()
            item = (row.get("Item") or "").strip()
            year = (row.get("Year") or "").strip()

            if not unit:
                invalid_records += 1
                continue

            used_records += 1

            # Store observations for NumPy.

            values_by_unit[unit].append(value)

            # Country grouping.

            country_key = (unit, area)

            country_groups[country_key][0] += value
            country_groups[country_key][1] += 1

            # Commodity grouping.

            commodity_key = (unit, item)

            commodity_groups[commodity_key][0] += value
            commodity_groups[commodity_key][1] += 1

            # Year grouping.

            year_key = (unit, year)

            year_groups[year_key][0] += value
            year_groups[year_key][1] += 1

    # Start generating report.

    log("\n" + "#" * 60)
    log("              WASTAGEX ANALYSIS REPORT")
    log("#" * 60)

    log("\n1. GENERAL SUMMARY")
    log("-" * 60)

    log(f"Cleaned records read: {total_records:,}")
    log(f"Valid observations analyzed: {used_records:,}")
    log(f"Negative observations excluded: {negative_records:,}")
    log(f"Invalid observations excluded: {invalid_records:,}")

    log("\n2. SOURCE FLAG DISTRIBUTION")
    log("-" * 60)

    for flag, count in flag_counts.most_common():
        log(f"{flag}: {count:,}")

    # Calculate NumPy statistical results.

    analyze_statistics(values_by_unit, log)

    # Grouped analyses, separately for every unit.

    for unit in sorted(values_by_unit):

        display_group_analysis(
            f"COUNTRY-WISE AVERAGE OBSERVATIONS ({unit})",
            country_groups,
            unit,
            log
        )

        display_group_analysis(
            f"COMMODITY-WISE AVERAGE OBSERVATIONS ({unit})",
            commodity_groups,
            unit,
            log
        )

        display_yearly_analysis(
            year_groups,
            unit,
            log
        )

    log("\n" + "=" * 60)
    log("IMPORTANT INTERPRETATION NOTE")
    log("=" * 60)

    log(
        "Grouped averages represent mean reported observations, "
        "not country-wide or global total food losses."
    )

    log(
        "Different countries may contain different commodity "
        "mixes and overlapping aggregate categories."
    )

    log(
        "Source flags have been retained for traceability. "
        "They should be interpreted using the dataset codebook."
    )

    log(
        "Negative values were excluded from statistics "
        "but retained in the cleaned dataset for review."
    )

    # Save the complete analysis report.

    REPORT_PATH.write_text(
        "\n".join(report_lines),
        encoding="utf-8"
    )

    print("\n" + "=" * 60)
    print("ANALYSIS REPORT GENERATED SUCCESSFULLY")
    print("=" * 60)

    print(REPORT_PATH)


# ============================================================
# TASK 7: MAIN APPLICATION
# ============================================================

def main():

    try:

        # Step 1: Process and clean original data.

        process_dataset()

        # Step 2: Analyze and generate the report.

        analyze_and_generate_report()

    except (
        FileNotFoundError,
        ValueError,
        OSError,
        csv.Error
    ) as error:

        print("\nWASTAGEX ERROR:", error)


# ============================================================
# APPLICATION ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()
