import unittest

import photo_sort

class PhotoSortTests(unittest.TestCase):

    def test_folder_name(self):
        year = 2014
        event = 'Boom'
        photographer = 'Marcus'

        name = photo_sort.folder_name(year, event, photographer)
        self.assertEqual('2014 - Boom - Marcus', name)

        name = photo_sort.folder_name(year, event, photographer, 2)
        self.assertEqual('2014 - Boom - 2 - Marcus', name)

def main():
    unittest.main()

if __name__ == '__main__':
    main()