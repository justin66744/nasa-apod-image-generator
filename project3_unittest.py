'''
Unit testing
'''
import unittest
from simpleimage import SimpleImage
from art import (
    AppError,
    build_url,
    search_description,
    get_transforms,
    compose,
    NASA_API_KEY,
)

class TestArt(unittest.TestCase):
    '''
    Test class
    '''
    def test_build_url_with_dates(self):
        '''
        Date test
        '''
        url = build_url('2023-01-01', '2023-01-05')
        expected_url = f"https://api.nasa.gov/planetary/apod?api_key={NASA_API_KEY}&start_date=2023-01-01&end_date=2023-01-05"
        self.assertEqual(url, expected_url)

    def test_build_url_without_dates(self):
        '''
        Empty date test
        '''
        url = build_url('', '')
        expected_url = f"https://api.nasa.gov/planetary/apod?api_key={NASA_API_KEY}&start_date=2024-01-01&end_date=2024-01-31"
        self.assertEqual(url, expected_url)

    def test_search_description(self):
        '''
        Query test
        '''
        search_result = [
            {'explanation': 'This is a test with moon and stars', 'url': 'url1'},
            {'explanation': 'Test with planets and a moon', 'url': 'url2'},
            {'explanation': 'No query', 'url': 'url3'}
        ]
        query = 'moon'
        result = search_description(search_result, query, 2)
        self.assertEqual(result, ['url1', 'url2'])

    def test_search_description_no_matches(self):
        '''
        Empty test
        '''
        search_result = [] 
        query = 'empty'
        result = search_description(search_result, query, 2)
        self.assertEqual(result, ['No images found.'])

    def test_get_transforms(self):
        '''
        Transformation test
        '''
        image1 = SimpleImage.blank(100, 100)
        image2 = SimpleImage.blank(100, 100)
        image1.write('image1.jpg')
        image2.write('image2.jpg')
        transforms = get_transforms('image1.jpg', 'image2.jpg')
        self.assertEqual(len(transforms), 12)

    def test_compose(self):
        '''
        Compose test
        '''
        images = [SimpleImage.blank(10, 10) for i in range(12)]
        result = compose(images)
        self.assertEqual(result.width, 50)
        self.assertEqual(result.height, 50)

    def test_compose_incorrect_length(self):
        '''
        Incorrect compost test
        '''
        images = [SimpleImage.blank(10, 10) for i in range(11)]
        with self.assertRaises(AppError):
            compose(images)

def main():
    '''
    Main
    '''
    unittest.main()

if __name__ == '__main__':
    main()
