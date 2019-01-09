import csv
from zipfile import ZipFile
# String (filepath) -> String


def count_csv_rows(file_reader):
    reader = csv.reader(file_reader)
    import pdb
    pdb.set_trace()
    return (sum(1 for row in reader) - 1)  # subtract headers


def extract_csvs_from_zip(file_path):
    """
    Combines all content in all CSVs (.csv) in the zip file.

    Uses the header from the first csv file and
    excludes the header from the rest of the csvs.

    Returns generator
    """
    with ZipFile(file_path, 'r') as zip_f:
        csv_files = [f for f in zip_f.namelist() if f[-3:].lower() == 'csv']
        for (idx, csv_file) in enumerate(csv_files):
            with zip_f.open(csv_file) as f:
                firstline = f.readline().decode('UTF-8', 'ignore')
                if idx == 0:
                    yield firstline
                for line in f:
                    yield line.decode('UTF-8', 'ignore')


def gen_to_csv(rows, new_path):
    with(open(new_path, 'w')) as new_csv:
        writer = csv.writer(new_csv, delimiter=',')
        first_row = next(rows)
        # write headers and first row
        writer.writerow([*first_row.keys()])
        writer.writerow([*first_row.values()])
        for row in rows:
            writer.writerow([*row.values()])
