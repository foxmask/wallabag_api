# coding: utf-8
import requests
from requests import HTTPError
import logging

__author__ = 'foxmask'


logging.basicConfig(format='%(message)s', level=logging.INFO)

__all__ = ['Wallabag']


class Wallabag(object):
    """
        Python Class 'Wallabag' to deal with Wallabag REST API
        This class is able to handle any data from your Wallabag account
    """
    EXTENTIONS = ('xml', 'json', 'txt', 'csv', 'pdf', 'epub', 'mobi', 'html')
    host = ''
    token = ''
    client_id = ''
    client_secret = ''
    user_agent = ''
    format = ''
    username = ''
    password = ''

    def __init__(self,
                 host='',
                 token='',
                 client_id='',
                 client_secret='',
                 extension='json',
                 user_agent="WallabagPython/1.0 "
                            "+https://github.com/foxmask/wallabag-api"):
        """
        init variable
        :param host: string url to the official API Wallabag
        :param token: string of the key provided by Wallabag
        :param client_id client id
        :param client_secret client secret
        :param extension: xml|json|txt|csv|pdf|epub|mobi|html
        :param user_agent
        """
        self.host = host
        self.client_id = client_id
        self.client_secret = client_secret
        self.token = token
        self.format = extension
        self.user_agent = user_agent

        if self.format not in self.EXTENTIONS:
            raise ValueError("format invalid {0} should be one of {1}".format(
                self.format, self.EXTENTIONS))

    def get_host(self):
        """
            get the host from which to get API
            :return host
        """
        return self.host

    def query(self, path, method='get', **params):
        """
            Do a query to the System API
            :param path: url to the API
            :param method: the kind of query to do
            :param params: a dict with all the
            necessary things to query the API
            :return json data
        """
        if method in ('get', 'post', 'patch', 'delete', 'put', 'get_token'):
            if method == 'get':
                r = requests.get(self.get_host() + path, params=params)
            elif method == 'post':
                r = requests.post(self.get_host() + path, data=params)
            elif method == 'patch':
                r = requests.patch(self.get_host() + path, data=params)
            elif method == 'delete':
                r = requests.delete(self.get_host() + path, headers=params)
            elif method == 'put':
                r = requests.put(self.get_host() + path, params=params)
            return self.handle_json_response(r)
        else:
            raise ValueError('method expected : get, post, patch, delete or put')

    @staticmethod
    def handle_json_response(responses):
        """
            get the json data response
            :param responses: the json response
            :return the json data without 'root' node
        """
        json_data = {}
        if responses.status_code != 200:
            err_msg = HTTPError(responses.status_code, responses.reason)
            msg = "Wallabag: error {err_msg}".format(err_msg=err_msg)
            logging.error(msg)
            raise HTTPError(msg)
        else:
            try:
                json_data = responses.json()
            except:
                for error in json_data['errors']:
                    error_json = json_data['errors'][error]['content']
                    logging.error("Wallabag: {error}".format(error=error_json))
        return json_data

    # ENTRIES
    def get_entries(self, **kwargs):
        """

            GET /api/entries.{_format}

            Retrieve all entries. It could be filtered by many options.

            :param kwargs: can contain one of the following filters
                archive:  '0' or '1', default '0' filter by archived status.
                star: '0' or '1', default '0' filter by starred status.
                delete: '0' or '1', default '0' filter by deleted status.
                sort: 'created' or 'updated', default 'created'
                order: 'asc' or 'desc', default 'desc'
                page: int default 1 what page you want
                perPage: int default 30 result per page
                tags: list of tags url encoded.
                Will returns entries that matches ALL tags
            :return data related to the ext
        """
        # default values
        params = {'access_token': self.token,
                  'archive': 0,
                  'star': 0,
                  'delete': 0,
                  'sort': 'created',
                  'order': 'desc',
                  'page': 1,
                  'perPage': 30,
                  'tags': []}

        if 'archive' in kwargs and int(kwargs['archive']) in (0, 1):
            params['archive'] = int(kwargs['archive'])
        if 'star' in kwargs and int(kwargs['star']) in (0, 1):
            params['star'] = int(kwargs['star'])
        if 'delete' in kwargs and int(kwargs['delete']) in (0, 1):
            params['delete'] = int(kwargs['delete'])
        if 'order' in kwargs and kwargs['order'] in ('asc', 'desc'):
            params['order'] = kwargs['order']
        if 'page' in kwargs and isinstance(kwargs['page'], int):
            params['page'] = kwargs['page']
        if 'perPage' in kwargs and isinstance(kwargs['perPage'], int):
            params['perPage'] = kwargs['perPage']
        if 'tags' in kwargs and isinstance(kwargs['tags'], list):
            params['tags'] = kwargs['tags']

        path = '/api/entries.{ext}'.format(ext=self.format)

        return self.query(path, "get", **params)

    def post_entries(self, url, title='', tags='', starred=0, archive=0, content='', language='', published_at='',
                     authors='', public=1, original_url=''):
        """
        POST /api/entries.{_format}

        Create an entry

        :param url: the url of the note to store
        :param title: Optional, we'll get the title from the page.
        :param tags: tag1,tag2,tag3 a comma-separated list of tags.
        :param starred entry already starred
        :param archive entry already archived
        :param content additionnal html content
        :param language
        :param published_at
        :param authors
        :param public
        :param original_url
        :return result
        """
        params = {'access_token': self.token, 'url': url, 'title': title,
                  'tags': tags, 'starred': starred, 'archive': archive,
                  'content': content, 'language': language, 'published_at': published_at,
                  'authors': authors, 'public': public, 'original_url': original_url}
        if len(tags) > 0 and isinstance(tags, list):
            params['tags'] = ', '.join(tags)
        path = '/api/entries.{ext}'.format(ext=self.format)
        return self.query(path, "post", **params)

    def get_entry(self, entry):
        """
        GET /api/entries/{entry}.{_format}

        Retrieve a single entry

        :param entry: \w+ an integer The Entry ID
        :return data related to the ext
        """
        params = {'access_token': self.token}
        url = '/api/entries/{entry}.{ext}'.format(entry=entry, ext=self.format)
        return self.query(url, "get", **params)

    def patch_entries(self, entry, **kwargs):
        """
        PATCH /api/entries/{entry}.{_format}

        Change several properties of an entry

        :param entry: the entry to 'patch' / update
        :param kwargs: can contain one of the following
            title: string
            tags: a list of tags tag1,tag2,tag3
            archive:  '0' or '1', default '0' archived the entry.
            star: '0' or '1', default '0' starred the entry
            delete: '0' or '1', default '0' flag as deleted.
            In case that you don't want to *really* remove it..
        :return data related to the ext
        """
        # default values
        params = {'access_token': self.token,
                  'title': '',
                  'archive': 0,
                  'tags': [],
                  'star': 0,
                  'delete': 0}

        if 'title' in kwargs:
            params['title'] = kwargs['title']
        if 'tags' in kwargs and isinstance(kwargs['tags'], list):
            params['tags'] = ', '.join(kwargs['tags'])
        if 'archive' in kwargs and int(kwargs['archive']) in (0, 1):
            params['archive'] = int(kwargs['archive'])
        if 'star' in kwargs and int(kwargs['star']) in (0, 1):
            params['star'] = int(kwargs['star'])
        if 'delete' in kwargs and int(kwargs['delete']) in (0, 1):
            params['delete'] = int(kwargs['delete'])
        path = '/api/entries/{entry}.{ext}'.format(
            entry=entry, ext=self.format)
        return self.query(path, "patch", **params)

    def get_entry_export(self, entry):
        """
        GET /api/entries/{entry}/export.{_format}

        Retrieve a single entry as a predefined format.

        :param entry: \w+ an integer The Entry ID
        :return data related to the ext
        """
        params = {'access_token': self.token}
        url = '/api/entries/{entry}/export.{ext}'.format(entry=entry,
                                                         ext=self.format)
        return self.query(url, "get", **params)

    def patch_entry_reload(self, entry):
        """
        PATCH /api/entries/{entry}/reload.{_format}

        Reload an entry. An empty response with HTTP Status 304 will be send
        if we weren't able to update the content (because it hasn't changed
        or we got an error).

        :param entry: \w+ an integer The Entry ID
        :return data related to the ext
        """
        params = {'access_token': self.token}
        url = '/api/entries/{entry}/reload.{ext}'.format(entry=entry,
                                                         ext=self.format)
        return self.query(url, "patch", **params)

    def delete_entries(self, entry):
        """
        DELETE /api/entries/{entry}.{_format}

        Delete permanently an entry

        :param entry: \w+ an integer The Entry ID
        :return result
        """

        params = {'Authorization': 'Bearer {}'.format(self.token)}
        path = '/api/entries/{entry}.{ext}'.format(
            entry=entry, ext=self.format)
        return self.query(path, "delete", **params)

    def entries_exists(self, url, urls=''):
        """
        GET /api/entries/exists.{_format}

        Check if an entry exist by url.

        :param url 	string 	true 	An url 	Url to check if it exists
        :param urls string 	false 	An array of urls
        (?urls[]=http...&urls[]=http...) Urls (as an array)
        to check if it exists

        :return result
        """
        params = {'url': url,
                  'urls': urls}

        path = '/api/entries/exists.{ext}'.format(ext=self.format)
        return self.query(path, "get", **params)

    # TAGS
    def get_entry_tags(self, entry):
        """
        GET /api/entries/{entry}/tags.{_format}

        Retrieve all tags for an entry

        :param entry: \w+ an integer The Entry ID
        :return data related to the ext
        """
        params = {'access_token': self.token}
        url = '/api/entries/{entry}/tags.{ext}'.format(
            entry=entry, ext=self.format)
        return self.query(url, "get", **params)

    def post_entry_tags(self, entry, tags):
        """
        POST /api/entries/{entry}/tags.{_format}

        Add one or more tags to an entry

        :param entry: \w+ an integer The Entry ID
        :param tags: string
        :return result
        """
        params = {'access_token': self.token, 'tags': []}
        if isinstance(tags, list):
            params['tags'] = tags
        path = '/api/entries/{entry}/tags.{ext}'.format(
            entry=entry, ext=self.format)
        return self.query(path, "post", **params)

    def delete_entry_tag(self, entry, tag):
        """
        DELETE /api/entries/{entry}/tags/{tag}.{_format}

        Permanently remove one tag for an entry

        :param entry: \w+ an integer The Entry ID
        :param tag: string The Tag
        :return data related to the ext
        """
        params = {'access_token': self.token}
        url = '/api/entries/{entry}/tags/{tag}.{ext}'.format(
            entry=entry, tag=tag, ext=self.format)
        return self.query(url, "delete", **params)

    def get_tags(self):
        """
        GET /api/tags.{_format}

        Retrieve all tags

        :return data related to the ext
        """
        params = {'access_token': self.token}
        path = '/api/tags.{ext}'.format(ext=self.format)
        return self.query(path, "get", **params)

    def delete_tag(self, tag):
        """
        DELETE /api/tags/{tag}.{_format}

        Permanently remove one tag from every entry

        :param tag: string The Tag
        :return data related to the ext
        """
        path = '/api/tags/{tag}.{ext}'.format(tag=tag, ext=self.format)
        params = {'access_token': self.token}
        return self.query(path, "delete", **params)

    def delete_tag_label(self, tag):
        """
        DELETE /api/tag/label.{_format}

        Permanently remove one tag from every entry.

        :param tag: string The Tag
        :return data related to the ext
        """
        path = '/api/tag/label.{ext}'.format(ext=self.format)
        params = {'access_token': self.token,
                  'tag': tag}
        return self.query(path, "delete", **params)

    def delete_tags_label(self, tags):
        """
        DELETE /api/tags/label.{_format}

        Permanently remove some tags from every entry.

        :param tags: string tags as strings (comma splitted)
        :return data related to the ext
        """
        path = '/api/tag/label.{ext}'.format(ext=self.format)
        params = {'access_token': self.token,
                  'tags': tags}
        return self.query(path, "delete", **params)

    # ANNOTATIONS
    def delete_annotations(self, annotation):
        """
        DELETE /api/annotations/{annotation}.{_format}

        Removes an annotation.

        :param annotation 	\w+ 	string 	The annotation ID

        Will returns annotation for this entry
        :return data related to the ext
        """
        params = {'access_token': self.token}
        url = '/api/annotations/{annotation}.{ext}'.format(
            annotation=annotation, ext=self.format)
        return self.query(url, "delete", **params)

    def put_annotations(self, annotation):
        """
        PUT /api/annotations/{annotation}.{_format}

        Updates an annotation.

        :param annotation 	\w+ 	string 	The annotation ID

        Will returns annotation for this entry
        :return data related to the ext
        """
        params = {'access_token': self.token}
        url = '/api/annotations/{annotation}.{ext}'.format(
            annotation=annotation, ext=self.format)
        return self.query(url, "put", **params)

    def get_annotations(self, entry):
        """
        GET /api/annotations/{entry}.{_format}

        Retrieve annotations for an entry

        :param entry 	\w+ 	integer 	The entry ID

        Will returns annotation for this entry
        :return data related to the ext
        """
        params = {'access_token': self.token}
        url = '/api/annotations/{entry}.{ext}'.format(entry=entry,
                                                      ext=self.format)
        return self.query(url, "get", **params)

    def post_annotations(self, entry, **kwargs):
        """
        POST /api/annotations/{entry}.{_format}

        Creates a new annotation.

        :param entry 	\w+ 	integer 	The entry ID

        :return
        """
        params = dict({'access_token': self.token,
                       'ranges': [],
                       'quote': '',
                       'text': ''})
        if 'ranges' in kwargs:
            params['ranges'] = kwargs['ranges']
        if 'quote' in kwargs:
            params['quote'] = kwargs['quote']
        if 'text' in kwargs:
            params['text'] = kwargs['text']

        url = '/api/annotations/{entry}.{ext}'.format(entry=entry,
                                                      ext=self.format)
        return self.query(url, "post", **params)

    # VERSION
    @property
    def version(self):
        """
        GET /api/version.{_format}

        Retrieve version number

        :return data related to the ext
        """
        params = {'access_token': self.token}
        url = '/api/version.{ext}'.format(ext=self.format)
        return self.query(url, "get", **params)

    @classmethod
    def get_token(cls, host, **params):
        """
        POST /oauth/v2/token

        Get a new token

        :param host: host of the service
        :param params: will contain :

        params = {"grant_type": "password",
                  "client_id": "a string",
                  "client_secret": "a string",
                  "username": "a login",
                  "password": "a password"}

        :return: access token
        """
        params['grant_type'] = "password"
        path = "/oauth/v2/token"
        resp = requests.post(host + path, data=params)
        data = cls.handle_json_response(resp)
        return data.get('access_token')
