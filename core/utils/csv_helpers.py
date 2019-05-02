import csv
from zipfile import ZipFile
# String (filepath) -> String
import os
import logging
logger = logging.getLogger('app')


def split_csv(source_filepath, dest_folder, split_file_prefix,
              records_per_file):
    """
    Split a source csv into multiple csvs of equal numbers of records,
    except the last file.

    Includes the initial header row in each split file.

    Split files follow a zero-index sequential naming convention like so:

        `{split_file_prefix}_0.csv`
    """
    if records_per_file <= 0:
        raise Exception('records_per_file must be > 0')

    with open(source_filepath, 'r') as source:
        reader = csv.reader(source, delimiter=',', quotechar='"', doublequote=True,
                            quoting=csv.QUOTE_ALL, skipinitialspace=True)
        headers = next(reader)

        file_idx = 0
        records_exist = True
        file_paths = []
        while records_exist:

            i = 0
            target_filename = '{}_{}.csv'.format(split_file_prefix, file_idx)
            target_filepath = os.path.join(dest_folder, target_filename)

            with open(target_filepath, 'w') as target:
                writer = csv.writer(target, delimiter=',', quotechar='"', doublequote=True,
                                    quoting=csv.QUOTE_ALL, skipinitialspace=True)

                while i < records_per_file:
                    if i == 0:
                        writer.writerow(headers)

                    try:
                        writer.writerow(next(reader))
                        i += 1
                    except:
                        records_exist = False
                        break

            if i == 0:
                # we only wrote the header, so delete that file
                os.remove(target_filepath)
            else:
                file_paths.append(target_filepath)

            file_idx += 1

        return file_paths


def count_csv_rows(file_path):
    reader = csv.reader(open(file_path, 'r'), delimiter=',', quotechar='"', doublequote=True,
                        quoting=csv.QUOTE_ALL, skipinitialspace=True)
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
        try:
            first_row = next(rows)
            # write headers and first row
            writer.writerow([*first_row.keys()])
            writer.writerow([*first_row.values()])
            for row in rows:
                writer.writerow([*row.values()])
        except Exception as e:
            logger.error(e)
            raise e
