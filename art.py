import datetime
import json 
import urllib.request
import urllib.parse
import random
import sys
from simpleimage import SimpleImage


# NASA API Key
NASA_API_KEY = 'AVEFCQi0prul2RXKFEMKyS0PrBLSUFfeqeCF2zaO'

BASE_NASA_URL = 'https://api.nasa.gov/planetary/apod'

class AppError(Exception):
    '''
    Custom Exception
    '''
    

def get_input():
    '''
    Takes in user-input
    '''
    while True:
        try:
            start_date = input("Start date: ")
            end_date = input("End date: ")
            query = input("Query: ").strip()
            if not query:
                print("Query can't be empty.")
            res = (start_date, end_date, query)
            return res
        except ValueError:
            print("Error: Please enter a valid date.")


# Helper function to build the URL for querying the API
def build_url(start_date: str, end_date: str) -> str:
    '''
    Creates URL from query
    '''
    if len(start_date.strip()) > 0:
        datetime.datetime.strptime(start_date, "%Y-%m-%d")
    else:
        start_date = '2024-01-01'

    if len(end_date.strip()) > 0:
        datetime.datetime.strptime(end_date, "%Y-%m-%d")
    else:
        end_date = '2024-01-31'
    url = f"{BASE_NASA_URL}?api_key={NASA_API_KEY}&start_date={start_date}&end_date={end_date}"

    return url

# Function to get results from the NASA APOD API
def get_result(url: str) -> list:
    '''
    Retrieves data from API
    '''
    attempts = 0
    final = 3
    for attempts in range(final):
        try:
            with urllib.request.urlopen(url) as res:
                data = json.loads(res.read().decode())
                if isinstance(data, dict):
                    data = [data]
                return data
        except urllib.error.HTTPError:
            print("HTTP error")
        except urllib.error.URLError:
            print("Network error")
        except json.JSONDecodeError as e:
            raise AppError("Error decoding JSON") from e
        attempts += 1
        if attempts == final:
            raise AppError("Failed after multiple attempts.")

# Function to score and filter results based on query
def search_description(search_result: list, query: str, max: int) -> list:
    '''
    Gets the top two results
    '''
    query_total = query.lower().split()
    scores = []
    result = []

    if not max:
        max = 2
    else:
        max = int(max)

    for item in search_result:
        explanation = item.get('explanation', '').lower()
        score = 0
        for token in query_total:
            token_count = explanation.count(token)
            score += token_count
        scores.append((score, item))

    total = len(scores)
    for i in range(total):
        for j in range(0, total - i - 1):
            if scores[j][0] < scores[j + 1][0]:
                scores[j], scores[j + 1] = scores[j + 1], scores[j]

    high_score = scores[:max]

    for score in high_score:
        item = score[1]
        result.append(item['url'])

    if not high_score:
        result.append("No images found.")

    return result

# Function to download images based on the filtered results
def get_images(urls: list) -> None:
    '''
    Grabs images from urls
    '''
    if len(urls) < 2:
        raise AppError("Not enough images.")

    for i, url in enumerate(urls[:2], start=1):
        try:
            response = urllib.request.urlopen(url)
            image_data = response.read()
            filename = f"image{i}.jpg"
            with open(filename, "wb") as file:
                file.write(image_data)
            print(f"{filename} saved.")
        except (urllib.error.HTTPError) as e:
            raise AppError(f"Failed to download image {i}: {e}") from e
        except (urllib.error.URLError) as e:
            raise AppError(f"Failed to download image {i}: {e}") from e
        except IOError as e:
            raise AppError(f"Error saving file image{i}.jpg") from e

# Function to apply transformations and return a list of transformed images
def get_transforms(file1: str, file2: str) -> list:
    '''
    List of 12 images
    '''
    image1 = SimpleImage(file1)
    image2 = SimpleImage(file2)

    image1 = SimpleImage.shrink(image1, 5)
    image2 = SimpleImage.shrink(image2, 5)

    transforms = []
    transforms.append(image1.copy())

    gray = SimpleImage.grayscale(image1.copy())
    transforms.append(gray)

    sep = SimpleImage.sepia(image1.copy())
    transforms.append(sep)

    blurred = SimpleImage.blur(image1.copy())
    transforms.append(blurred)

    red_filtered = SimpleImage.filter(image1.copy(), 'red', 100)
    transforms.append(red_filtered)

    green_filtered = SimpleImage.filter(image1.copy(), 'green', 100)
    transforms.append(green_filtered)

    blue_filtered = SimpleImage.filter(image1.copy(), 'blue', 100)
    transforms.append(blue_filtered)

    flip_h = SimpleImage.flip(image1.copy(), 0)
    transforms.append(flip_h)

    flip_v = SimpleImage.flip(image1.copy(), 1)
    transforms.append(flip_v)

    greenscreen_red = SimpleImage.greenscreen(image1.copy(), 'red', 100, image2.copy())
    transforms.append(greenscreen_red)

    greenscreen_green = SimpleImage.greenscreen(image1.copy(), 'green', 100, image2.copy())
    transforms.append(greenscreen_green)

    greenscreen_blue = SimpleImage.greenscreen(image1.copy(), 'blue', 100, image2.copy())
    transforms.append(greenscreen_blue)

    return transforms

# Function to compose the final 5x5 grid of images
def compose(img_list: list) -> SimpleImage:
    '''
    Creates the final image
    '''
    if len(img_list) != 12:
        raise AppError("Needs to be exactly 12 images.")
    img = img_list[0]
    canvas_width = img.width * 5
    canvas_height = img.height * 5
    res = SimpleImage.blank(canvas_width, canvas_height)

    for col in range(5):
        for row in range(5):
            selected_images = random.choice(img_list)
            for y in range(img.height):
                for x in range(img.width):
                    pix = selected_images.get_pixel(x, y)
                    final_x = col * img.width + x
                    final_y = row * img.height + y
                    rpix = res.get_pixel(final_x, final_y)
                    rpix.red = pix.red
                    rpix.green = pix.green
                    rpix.blue = pix.blue
    res.write("pop.jpg")

    return res

# Main function to run the complete process
def run():
    '''
    Main function
    '''
    try:
        start_date, end_date, query = get_input()
        url = build_url(start_date, end_date)
        search_result = get_result(url)
        top_results = search_description(search_result, query, max=2)
        get_images(top_results)
        transforms = get_transforms("image1.jpg", "image2.jpg")
        res = compose(transforms)
        res.show()
    except AppError as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    run()
