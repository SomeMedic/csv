import csv
import os
import requests
from PIL import Image
import logging

logging.basicConfig(filename='error_log.txt', level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')


def download_image(url, filename):
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        with open(filename, 'wb') as file:
            for chunk in response.iter_content(8192):
                file.write(chunk)
        return True
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to download image from {url}: {e}")
        return False


def resize_image(filename, scale=1.5):
    try:
        with Image.open(filename) as img:
            width, height = img.size
            new_width = int(width * scale)
            new_height = int(height * scale)
            img = img.resize((new_width, new_height), Image.BILINEAR)

            img = img.convert("RGB")

            img.save(filename, "JPEG")
        return True
    except Exception as e:
        logging.error(f"Failed to resize image {filename}: {e}")
        return False


def process_image_row(row):
    if len(row) < 2:
        logging.warning(f"Skipping row with insufficient data: {row}")
        return

    name, url = row.split(';')

    filename = os.path.join("avs", f"{name.strip()}.jpeg")

    if download_image(url.strip(), filename):
        if resize_image(filename):
            logging.info(f"Processed {name} successfully!")
        else:
            logging.error(f"Failed to resize {name}!")
    else:
        logging.error(f"Failed to download {name}!")


def main():
    desired_directory = r'Путь к папке avs'  # Замените на желаемый абсолютный путь

    if not os.path.exists(os.path.join(desired_directory, 'avs')):
        os.mkdir(os.path.join(desired_directory, 'avs'))

    csv_file_path = '1.csv'

    try:
        with open(csv_file_path, 'r', newline='', encoding='utf-8') as csvfile:
            lines = csvfile.readlines()

            retry_count = 0
            max_retry_count = 20

            for line in lines:
                process_image_row(line.strip())

                retry_count = 0

    except FileNotFoundError:
        logging.error(f"File not found: {csv_file_path}")
    except Exception as e:
        logging.error(f"An error occurred: {e}")

    logging.info("Job is done!")


if __name__ == "__main__":
    main()
