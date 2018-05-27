# coding: utf-8
import datetime
import unittest
from wallabag import Wallabag


class TestWallabag(unittest.TestCase):

    host = 'http://bag.foxmask'
    client_id = ''
    client_secret = ''
    token = ''

    def setUp(self):
        access_token = self.test_get_token()
        self.format = 'json'
        self.w = Wallabag(host=self.host,
                          token=access_token,
                          client_id=self.client_id,
                          client_secret=self.client_secret)

    def test_get_token(self):
        params = {"grant_type": "password",
                  "client_id": '1_3to3042y05gk8g4wcsk40w40k8kk00s04gwcoo4sows8wskcg0',
                  "client_secret": 'ift9k07vd20ccg4ocosg0cw4kkgk4o8080848scwg0oosowow',
                  "username": 'foxmask',
                  "password": 'ratatab00m'}

        data = Wallabag.get_token(host=self.host, **params)
        self.assertTrue(isinstance(data, str), True)
        return data

    def create_entry(self):
        title = 'foobar title'
        url = 'https://somwhere.over.the.raibow.com/'
        tags = ['foo', 'bar']
        starred = 0
        archive = 0
        content = '<p>Additional content</p>'
        language = 'FR'
        published_at = datetime.datetime.now()
        authors = 'John Doe'
        public = 0
        original_url = 'http://localhost'
        data = self.w.post_entries(url, title, tags, starred, archive, content, language, published_at, authors,
                                   public, original_url)
        return data

    def test_get_entries(self):
        params = {'archive': 0,
                  'star': 0,
                  'delete': 0,
                  'sort': 'created',
                  'order': 'desc',
                  'page': 1,
                  'perPage': 30,
                  'tags': []}
        data = self.w.get_entries(**params)
        self.assertIsInstance(data, dict)

    def test_get_entry(self):
        entry = 1
        self.assertTrue(isinstance(entry, int), True)
        data = self.w.get_entry(entry)
        self.assertTrue(data, str)

    def test_get_entry_tags(self):
        entry = 1
        self.assertTrue(isinstance(entry, int), True)
        data = self.w.get_entry_tags(entry)
        self.assertIsInstance(data, list)

    def test_get_tags(self):
        data = self.w.get_tags()
        self.assertIsInstance(data, list)

    def test_post_entries(self):
        data = self.create_entry()
        self.assertTrue(data, True)

    def test_patch_entries(self):
        entry = 1
        params = {'title': 'I change the title',
                  'archive': 0,
                  'tags': ["bimbo", "pipo"],
                  'star': 0,
                  'delete': 0}
        self.assertTrue(isinstance(entry, int), True)
        self.assertTrue(isinstance(params, dict), True)
        data = self.w.patch_entries(entry, **params)
        self.assertTrue(data, True)

    def test_delete_entries(self):
        entry = self.create_entry()
        self.assertTrue(isinstance(entry['id'], int), True)
        data = self.w.delete_entries(entry['id'])
        self.assertTrue(data, True)

    def test_post_entry_tags(self):
        entry = 1
        self.assertTrue(isinstance(entry, int), True)
        tags = ['foo', 'bar']
        self.assertTrue(isinstance(tags, list), True)
        data = self.w.post_entry_tags(entry, tags)
        self.assertTrue(data, True)


if __name__ == '__main__':
    unittest.main()
