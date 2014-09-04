import os
import shutil
import tempfile
import unittest

import photo_sort

class PhotoSortTests(unittest.TestCase):

    def setUp(self):
        self.temp_dir = os.path.join(tempfile.gettempdir(), 'photo_sort')
        
        if not os.path.exists(self.temp_dir):
            os.makedirs(self.temp_dir)

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_folder_name(self):
        year = 2014
        event = 'Boom'

        result = photo_sort.folder_name(year, event)
        self.assertEqual('2014 - Boom', result)        

        photographer = 'Marcus'

        result = photo_sort.folder_name(year, event, photographer)
        self.assertEqual('2014 - Boom - Marcus', result)

        result = photo_sort.folder_name(year, event, photographer, 2)
        self.assertEqual('2014 - Boom - 2 - Marcus', result)

    def test_folder_path(self):
        output = self.temp_dir
        year = 2014
        event = 'Boom'

        result = photo_sort.folder_path(output, year, event)
        self.assertEqual(os.path.join(output, '2014 - Boom'), result)

        photographer = 'Marcus'

        result = photo_sort.folder_path(output, year, event, photographer=photographer)
        self.assertEqual(os.path.join(output, '2014 - Boom - Marcus'), result)

        os.makedirs(result)

        result = photo_sort.folder_path(output, year, event, photographer=photographer)
        self.assertEqual(os.path.join(output, '2014 - Boom - 2 - Marcus'), result)

    def test_index_mask(self):
        result = photo_sort.get_index_mask(1)
        self.assertEqual('%d', result)

        result = photo_sort.get_index_mask(10)
        self.assertEqual('%02d', result)       

        result = photo_sort.get_index_mask(100)
        self.assertEqual('%03d', result)

        result = photo_sort.get_index_mask(1000)
        self.assertEqual('%04d', result)

        result = photo_sort.get_index_mask(10000)
        self.assertEqual('%05d', result)

def main():
    unittest.main()

if __name__ == '__main__':
    main()