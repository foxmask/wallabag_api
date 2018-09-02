# coding: utf-8
import logging
import aiohttp
from aiohttp.http_exceptions import HttpProcessingError
from aiohttp.client_exceptions import ClientResponseError

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
    aio_sess = None

    def __init__(self,
                 host='',
                 token='',
                 client_id='',
                 client_secret='',
                 extension='json',
                 user_agent="WallabagPython/1.2.2 "
                            " +https://github.com/push-things/wallabag-api",
                 aio_sess=None):
        """
        init variable
        :param host: string url to the official API Wallabag
        :param token: string of the key provided by Wallabag
        :param client_id client id
        :param client_secret client secret
        :param extension: xml|json|txt|csv|pdf|epub|mobi|html
        :param user_agent
        :param aio_sess aiohttp session
        """
        self.host = host
        self.client_id = client_id
        self.client_secret = client_secret
        self.token = token
        self.format = extension
        self.user_agent = user_agent
        self.aio_sess = aio_sess
        if self.format not in self.EXTENTIONS:
            raise ValueError("format invalid {0} should be one of {1}".format(
                self.format, self.EXTENTIONS))

    async def query(self, path, method='get', **params):
        """
        Do a query to the System API

        :param path: url to the API
        :param method: the kind of query to do
        :param params: a dict with all the
        necessary things to query the API
        :return json data
        """
        if method in ('get', 'post', 'patch', 'delete', 'put'):
            full_path = self.host + path
            if method == 'get':
                resp = await self.aio_sess.get(full_path, params=params)
            elif method == 'post':
                resp = await self.aio_sess.post(full_path, data=params)
            elif method == 'patch':
                resp = await self.aio_sess.patch(full_path, data=params)
            elif method == 'delete':
                resp = await self.aio_sess.delete(full_path, params=params, headers=params)
            elif method == 'put':
                resp = await self.aio_sess.put(full_path, data=params)

            async with resp:
                # return the content if its a binary one
                if resp.content_type.startswith('application/pdf') or \
                        resp.content_type.startswith('application/epub'):
                    return await resp.read()

                return await self.handle_json_response(resp)
        else:
            raise ValueError('method expected: get, post, patch, delete, put')

    @staticmethod
    async def handle_json_response(responses):
        """
        get the json data response
        :param responses: the json response
        :return the json data without 'root' node
        """
        json_data = {}
        if responses.status != 200:
            err_msg = HttpProcessingError(code=responses.status,
                                          message=await responses.json())
            logging.error("Wallabag: aiohttp error {err_msg}".format(
                err_msg=err_msg))
        else:
            try:
                json_data = responses.json()
            except ClientResponseError as e:
                # sometimes json_data does not return any json() without
                # any error. This is due to the grabbing URL which "rejects"
                # the URL
                logging.error("Wallabag: aiohttp error {code} {message}"
                              .format(code=e.code, message=e.message))
        return await json_data

    @staticmethod
    def __get_attr(what, type_attr, value_attr, **kwargs):
        """
        get the value of a parm
        :param what: string parm
        :param type_attr: type of parm
        :param value_attr:
        :param kwargs:
        :return: value of the parm
        """
        if what in kwargs:
            value = int(kwargs[what]) if type_attr == 'int' else kwargs[what]
            if value in value_attr:
                return value

    # ENTRIES
    async def get_entries(self, **kwargs):
        """
        GET /api/entries.{_format}

        Retrieve all entries. It could be filtered by many options.

        :param kwargs: can contain one of the following filters
            archive:  '0' or '1', default '0' filter by archived status.
            starred: '0' or '1', default '0' filter by starred status.
            sort: 'created' or 'updated', default 'created'
            order: 'asc' or 'desc', default 'desc'
            page: int default 1 what page you want
            perPage: int default 30 result per page
            tags: list of tags url encoded.
            since: int default 0 from what timestamp you want
            Will returns entries that matches ALL tags
        :return data related to the ext
        """
        # default values
        params = dict({'access_token': self.token,
                       'sort': 'created',
                       'order': 'desc',
                       'page': 1,
                       'perPage': 30,
                       'tags': '',
                       'since': 0})

        if 'archive' in kwargs and int(kwargs['archive']) in (0, 1):
            params['archive'] = int(kwargs['archive'])
        if 'starred' in kwargs and int(kwargs['starred']) in (0, 1):
            params['starred'] = int(kwargs['starred'])
        if 'order' in kwargs and kwargs['order'] in ('asc', 'desc'):
            params['order'] = kwargs['order']
        if 'page' in kwargs and isinstance(kwargs['page'], int):
            params['page'] = kwargs['page']
        if 'perPage' in kwargs and isinstance(kwargs['perPage'], int):
            params['perPage'] = kwargs['perPage']
        if 'tags' in kwargs and isinstance(kwargs['tags'], list):
            params['tags'] = ', '.join(kwargs['tags'])
        if 'since' in kwargs and isinstance(kwargs['since'], int):
            params['since'] = kwargs['since']

        path = '/api/entries.{ext}'.format(ext=self.format)

        return await self.query(path, "get", **params)

    async def post_entries(self, url, title='', tags='', starred=0, archive=0, content='', language='', published_at='',
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
        return await self.query(path, "post", **params)

    async def get_entry(self, entry):
        """
        GET /api/entries/{entry}.{_format}

        Retrieve a single entry

        :param entry: \w+ an integer The Entry ID
        :return data related to the ext
        """
        params = {'access_token': self.token}
        url = '/api/entries/{entry}.{ext}'.format(entry=entry,
                                                  ext=self.format)
        return await self.query(url, "get", **params)

    async def reaload_entry(self, entry):
        """
        PATCH /api/entries/{entry}/reload.{_format}

        Reload a single entry

        :param entry: \w+ an integer The Entry ID
        :return data related to the ext
        """
        params = {'access_token': self.token}
        url = '/api/entries/{entry}/reload.{ext}'.format(entry=entry,
                                                         ext=self.format)
        return await self.query(url, "patch", **params)

    async def patch_entries(self, entry, **kwargs):
        """
        PATCH /api/entries/{entry}.{_format}

        Change several properties of an entry

        :param entry: the entry to 'patch' / update
        :param kwargs: can contain one of the following
            title: string
            tags: a list of tags tag1,tag2,tag3
            archive:  '0' or '1', default '0' archived the entry.
            starred: '0' or '1', default '0' starred the entry
            In case that you don't want to *really* remove it..
        :return data related to the ext
        """
        # default values
        params = {'access_token': self.token,
                  'title': '',
                  'tags': []}

        if 'title' in kwargs:
            params['title'] = kwargs['title']
        if 'tags' in kwargs and isinstance(kwargs['tags'], list):
            params['tags'] = ', '.join(kwargs['tags'])

        params['archive'] = self.__get_attr(what='archive',
                                            type_attr=int,
                                            value_attr=(0, 1),
                                            **kwargs)
        params['starred'] = self.__get_attr(what='starred',
                                            type_attr=int,
                                            value_attr=(0, 1),
                                            **kwargs)
        params['order'] = self.__get_attr(what='order',
                                          type_attr=str,
                                          value_attr=('asc', 'desc'),
                                          **kwargs)

        path = '/api/entries/{entry}.{ext}'.format(
            entry=entry, ext=self.format)
        return await self.query(path, "patch", **params)

    async def get_entry_export(self, entry):
        """
        GET /api/entries/{entry}/export.{_format}

        Retrieve a single entry as a predefined format.

        :param entry: \w+ an integer The Entry ID
        :return data related to the ext
        """
        params = {'access_token': self.token}
        url = '/api/entries/{entry}/export.{ext}'.format(entry=entry,
                                                         ext=self.format)
        return await self.query(url, "get", **params)

    async def patch_entry_reload(self, entry):
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
        return await self.query(url, "patch", **params)

    async def delete_entries(self, entry):
        """
        DELETE /api/entries/{entry}.{_format}

        Delete permanently an entry

        :param entry: \w+ an integer The Entry ID
        :return result
        """

        params = {'Authorization': 'Bearer {}'.format(self.token)}
        path = '/api/entries/{entry}.{ext}'.format(
            entry=entry, ext=self.format)
        return await self.query(path, "delete", **params)

    async def entries_exists(self, url, urls=''):
        """
        GET /api/entries/exists.{_format}

        Check if an entry exist by url.

        :param url 	string 	true 	An url 	Url to check if it exists
        :param urls string 	false 	An array of urls
        (?urls[]=http...&urls[]=http...) Urls (as an array)
        to check if it exists

        :return result
        """
        params = {'access_token': self.token,
                  'url': url,
                  'urls': urls}

        path = '/api/entries/exists.{ext}'.format(ext=self.format)
        return await self.query(path, "get", **params)

    # TAGS

    async def get_entry_tags(self, entry):
        """
        GET /api/entries/{entry}/tags.{_format}

        Retrieve all tags for an entry

        :param entry: \w+ an integer The Entry ID
        :return data related to the ext
        """
        params = {'access_token': self.token}
        url = '/api/entries/{entry}/tags.{ext}'.format(
            entry=entry, ext=self.format)
        return await self.query(url, "get", **params)

    async def post_entry_tags(self, entry, tags):
        """
        POST /api/entries/{entry}/tags.{_format}

        Add one or more tags to an entry

        :param entry: \w+ an integer The Entry ID
        :param tags: list of tags (urlencoded)
        :return result
        """
        params = {'access_token': self.token, 'tags': []}
        if len(tags) > 0 and isinstance(tags, list):
            params['tags'] = ', '.join(tags)
        path = '/api/entries/{entry}/tags.{ext}'.format(
            entry=entry, ext=self.format)
        return await self.query(path, "post", **params)

    async def delete_entry_tag(self, entry, tag):
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
        return await self.query(url, "delete", **params)

    async def get_tags(self):
        """
        GET /api/tags.{_format}

        Retrieve all tags

        :return data related to the ext
        """
        params = {'access_token': self.token}
        path = '/api/tags.{ext}'.format(ext=self.format)
        return await self.query(path, "get", **params)

    async def delete_tag(self, tag):
        """
        DELETE /api/tags/{tag}.{_format}

        Permanently remove one tag from every entry

        :param tag: string The Tag
        :return data related to the ext
        """
        path = '/api/tags/{tag}.{ext}'.format(tag=tag, ext=self.format)
        params = {'access_token': self.token}
        return await self.query(path, "delete", **params)

    async def delete_tag_label(self, tag):
        """
        DELETE /api/tag/label.{_format}

        Permanently remove one tag from every entry.

        :param tag: string The Tag
        :return data related to the ext
        """
        path = '/api/tag/label.{ext}'.format(ext=self.format)
        params = {'access_token': self.token,
                  'tag': tag}
        return await self.query(path, "delete", **params)

    async def delete_tags_label(self, tags):
        """
        DELETE /api/tags/label.{_format}

        Permanently remove some tags from every entry.

        :param tags: list of tags (urlencoded)
        :return data related to the ext
        """
        path = '/api/tag/label.{ext}'.format(ext=self.format)
        params = {'access_token': self.token, 'tags': []}
        if len(tags) > 0 and isinstance(tags, list):
            params['tags'] = ', '.join(tags)
        return await self.query(path, "delete", **params)

    # ANNOTATIONS
    async def delete_annotations(self, annotation):
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
        return await self.query(url, "delete", **params)

    async def put_annotations(self, annotation):
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
        return await self.query(url, "put", **params)

    async def get_annotations(self, entry):
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
        return await self.query(url, "get", **params)

    async def post_annotations(self, entry, **kwargs):
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
        return await self.query(url, "post", **params)

    # VERSION
    @property
    async def version(self):
        """
        GET /api/version.{_format}

        Retrieve version number

        :return data related to the ext
        """
        params = {'access_token': self.token}
        url = '/api/version.{ext}'.format(ext=self.format)
        return await self.query(url, "get", **params)

    @classmethod
    async def get_token(cls, host, **params):
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
        async with aiohttp.ClientSession() as sess:
            async with sess.post(host + path, data=params) as resp:
                data = await cls.handle_json_response(resp)
                return data.get("access_token")
