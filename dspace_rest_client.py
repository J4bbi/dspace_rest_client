import datetime
import json
import logging
import requests
from requests import RequestException
import sys
import time
import urllib.parse as urlparse
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logging.basicConfig(filename='dspace_rest_client.log',
                    level=logging.INFO,
                    #format='%(asctime)s | %(message)s',
                    datefmt='%m/%d/%Y %I:%M:%S %p')


class DSpaceRestClientException(Exception):
    pass


class LoginException(DSpaceRestClientException):
    pass


class LogoutException(DSpaceRestClientException):
    pass


class UpdateItemException(DSpaceRestClientException):
    pass


class AbstractDSpaceObject:
    """ Empty DSpace blueprint object"""
    def __init__(self):
        self.uuid = None
        self.name = None
        self.handle = None
        self.type = None
        self.link = None


class Metadata:
    def __str__(self):
        return json.dumps(self.__dict__)

    def __init__(self, key, value, lang):
        self.key = key
        self.value = value
        self.language = lang


class Bitstream(AbstractDSpaceObject):
    """
    Bitstreams are files. They have a filename, size (in bytes), and a file format. Typically in DSpace, the Bitstream
    will the "full text" article, or some other media. Some files are the actual file that was uploaded (tagged with
    bundleName:ORIGINAL), others are DSpace-generated files that are derivatives or renditions, such as
    text-extraction, or thumbnails. You can download files/bitstreams. DSpace doesn't really limit the type of files
    that it takes in, so this could be PDF, JPG, audio, video, zip, or other. Also, the logo for a Collection or a
    Community, is also a Bitstream.

    GET /bitstreams - Return all bitstreams in DSpace.
    GET /bitstreams/{bitstream id} - Return bitstream.
    GET /bitstreams/{bitstream id}/policy - Return bitstream policies.
    GET /bitstreams/{bitstream id}/retrieve - Return data of bitstream.
    POST /bitstreams/{bitstream id}/policy - Add policy to item. You must post a ResourcePolicy
    PUT /bitstreams/{bitstream id}/data - Update data/file of bitstream. You must put the data
    PUT /bitstreams/{bitstream id} - Update metadata of bitstream. You must put a Bitstream, does not alter the file/data
    DELETE /bitstreams/{bitstream id} - Delete bitstream from DSpace.
    DELETE /bitstreams/{bitstream id}/policy/{policy_id} - Delete bitstream policy.

    You can access the parent object of a Bitstream (normally an Item, but possibly a Collection or Community when it
    is its logo) through: /bitstreams/:bitstreamID?expand=parent

    As the documentation may state "You must post a ResourcePolicy" or some other object type, this means that there
    is a structure of data types, that your XML or JSON must be of type, when it is posted in the body.
    """
    def __str__(self):
        return str(['{}: {}'.format(attr, value) for attr, value in self.__dict__.items()])

    def __init__(self, ds_client, item_json):
        super(Bitstream, self).__init__()
        self.ds_client = ds_client

        for k, v in item_json.items():
            self.__setattr__(k, v)


class Collection(AbstractDSpaceObject):
    """
    GET /collections - Return all collections of DSpace in array.
    GET /collections/{collectionId} - Return collection with id.
    GET /collections/{collectionId}/items - Return all items of collection.
    POST /collections/{collectionId}/items - Create posted item in collection. You must post an Item
    POST /collections/find-collection - Find collection by passed name.
    PUT /collections/{collectionId} - Update collection. You must put Collection.
    DELETE /collections/{collectionId} - Delete collection from DSpace.
    DELETE /collections/{collectionId}/items/{itemId} - Delete item in collection.

    {"id":730,
    "name":"Annual Reports Collection",
    "handle":"10766/10214",
    "type":"collection",
    "link":"/rest/collections/730",
    "expand":["parentCommunityList","parentCommunity","items","license","logo","all"],
    "logo":null,
    "parentCommunity":null,
    "parentCommunityList":[],
    "items":[],
    "license":null,
    "copyrightText":"",
    "introductoryText":"",
    "shortDescription":"",
    "sidebarText":"",
    "numberItems":3}
    """

    def __str__(self):
        return str(['{}: {}'.format(attr, value) for attr, value in self.__dict__.items()])

    def __init__(self, ds_client, item_json):
        super(Collection, self).__init__()
        self.ds_client = ds_client

        for k, v in item_json.items():
            self.__setattr__(k, v)


class Community(AbstractDSpaceObject):
    """
    GET /communities - Returns array of all communities in DSpace.
    GET /communities/top-communities - Returns array of all top communities in DSpace.
    GET /communities/{communityId} - Returns community.
    GET /communities/{communityId}/collections - Returns array of collections of community.
    GET /communities/{communityId}/communities - Returns array of subcommunities of community.
    POST /communities - Create new community at top level. You must post community.
    POST /communities/{communityId}/collections - Create new collections in community. You must post Collection.
    POST /communities/{communityId}/communities - Create new subcommunity in community. You must post Community.
    PUT /communities/{communityId} - Update community. You must put Community
    DELETE /communities/{communityId} - Delete community.
    DELETE /communities/{communityId}/collections/{collectionId} - Delete collection in community.
    DELETE /communities/{communityId}/communities/{communityId2} - Delete subcommunity in community.

    {"id":456,
    "name":"Reports Community",
    "handle":"10766/10213",
    "type":"community",
    "link":"/rest/communities/456",
    "expand":["parentCommunity","collections","subCommunities","logo","all"],
    "logo":null,
    "parentCommunity":null,
    "copyrightText":"",
    "introductoryText":"",
    "shortDescription":"Collection contains materials pertaining to the Able Family",
    "sidebarText":"",
    "countItems":3,
    "subcommunities":[],
    "collections":[]}
    """

    def __str__(self):
        return str(['{}: {}'.format(attr, value) for attr, value in self.__dict__.items()])

    def __init__(self, ds_client, item_json):
        super(Community, self).__init__()
        self.ds_client = ds_client

        for k, v in item_json.items():
            self.__setattr__(k, v)

        self.countItems = int(self.countItems)

    def _get(self, rest_url, ds_obj, offset=0, limit=100, results=[]):
        """
        Get *
        :param offset:
        :param results:
        :param limit:
        :return:
        """
        response = None
        try:
            get_url = '{}/{}?offset={}&limit={}'.format(self.ds_client.base_url, rest_url, offset, limit)
            print(get_url)
            response = self.ds_client.request_get(get_url)
        except RequestException:
            logging.error('Could not get "{}". Status code: {}'.format(rest_url, response.status_code))

        if response.status_code == 200:
            results = results + [ds_obj(self.ds_client, obj) for obj in response.json()]

            if offset < limit and len(response.json()) == limit:
                return self._get(rest_url, ds_obj, offset + limit, limit, results)
            else:
                return results
        else:
            return 'Could not get "{}". Status code: {}. \n{}'.format(rest_url, response.status_code, response.content)

    def get_collections(self):
        return self._get('communities/{}/collections'.format(self.uuid), Collection)


class Item(AbstractDSpaceObject):
    """
    A DSpace Item
    GET /items - Return list of items.
    GET /items/{item id} - Return item.
    GET /items/{item id}/metadata - Return item metadata.
    GET /items/{item id}/bitstreams - Return item bitstreams.
    POST /items/find-by-metadata-field - Find items by metadata entry. You must post a MetadataEntry.
    POST /items/{item id}/metadata - Add metadata to item. You must post an array of MetadataEntry.
    POST /items/{item id}/bitstreams - Add bitstream to item. You must post a Bitstream.
    PUT /items/{item id}/metadata - Update metadata in item. You must put a MetadataEntry.
    DELETE /items/{item id} - Delete item.
    DELETE /items/{item id}/metadata - Clear item metadata.
    DELETE /items/{item id}/bitstreams/{bitstream id} - Delete item bitstream.

    {"id":14301,
    "name":"2015 Annual Report",
    "handle":"123456789/13470",
    "type":"item",
    "link":"/rest/items/14301",
    "expand":["metadata","parentCollection","parentCollectionList","parentCommunityList","bitstreams","all"],
    "lastModified":"2015-01-12 15:44:12.978",
    "parentCollection":null,
    "parentCollectionList":null,
    "parentCommunityList":null,
    "bitstreams":null,
    "archived":"true",
    "withdrawn":"false"}

    """
    def __str__(self):
        return str(['{}: {}'.format(attr, value) for attr, value in self.__dict__.items()])

    def __init__(self, ds_client, item_json, collection=None):
        super(Item, self).__init__()
        self.ds_client = ds_client

        for k, v in item_json.items():
            self.__setattr__(k, v)

        self.lastModified = time.strptime(self.lastModified, "%Y-%m-%d %H:%M:%S.%f")
        self.archived = bool(item_json['archived'])
        self.withdrawn = bool(item_json['withdrawn'])
        self.metadata = self.get_metadata() if self.ds_client.load_item_metadata else None

    def create(self, metadata, ds_collection):
        """
        Create a item
        :param metadata:
        :param ds_collection:
        :return:
        """
        item = {  # Structure necessary to create DSpace item
            "type": "item",
            "metadata": metadata
        }

        logging.info("Item: %s", item)

        collection_url = self.base_url + '/collections/' + ds_collection + '/items'
        logging.info(collection_url)

        # Create item
        try:
            response = requests.post(collection_url,
                                     headers=self.headers,
                                     cookies={'JSESSIONID': self.session},
                                     data=json.dumps(item),
                                     verify=self.verify_ssl)
        except RequestException:
            logging.info('Could not create DSpace item: {}'.format(collection_url))

        logging.info(response)
        logging.info(response.json())

        return response.json()

    def delete(self, handle):
        """
        Delete item
        :param handle:
        :return:
        """
        response = None
        item_id = self.get_id_by_handle(handle)

        try:
            response = requests.delete(self.base_url + '/items/' + item_id,
                                       headers=self.headers,
                                       cookies={'JSESSIONID': self.session},
                                       verify=self.verify_ssl)
        except RequestException:
            logging.info('Could not delete item: {}'.format(item_id))

        if response.status_code != 200:
            logging.error('No item to delete at handle: {}'.format(handle))

        logging.info('Deleted item: {}'.format(item_id))

    def get_id_by_handle(self):
        # Get item id
        response = None
        try:
            response = requests.get(self.ds_client.base_url + '/handle/' + self.handle,
                                    headers=self.ds_client.headers,
                                    cookies={'JSESSIONID': self.ds_client.session},
                                    verify=self.ds_client.verify_ssl)
        except RequestException:
            msg = 'Could not get id for: {}'.format(self.handle)
            logging.info(msg)

        if response.status_code == 200:
            return response.json()['uuid']

        return 'No item at handle: ' + self.handle

    def get_metadata(self):
        try:
            response = self.ds_client.request_get('/items/{}/metadata'.format(self.uuid))
        except RequestException:
            logging.error('Could not get metadata for DSpace item: {}'.format(self.handle))

        return [Metadata(m['key'], m['value'], m['language']) for m in response.json()]

    def update_item(self, metadata):
        item_id = self.get_id_by_handle(self.handle)
        try:
            response = requests.put('{}/items/{}/metadata'.format(self.ds_client.base_url, item_id),
                                    headers=self.ds_client.headers,
                                    cookies={'JSESSIONID': self.ds_client.session},
                                    data=json.dumps(metadata),
                                    verify=self.ds_client.verify_ssl)

            if response.status_code != 200:
                raise UpdateItemException()

            logging.info('Updated item {} width {} metadata items.'.format(self.handle, len(metadata)))

        except UpdateItemException as e:
            logging.error('Could not update DSpace item: {}\n{}'.format(self.handle, e))
        except RequestException:
            logging.error('Could not update DSpace item: {}'.format(self.handle))

    def get_bitstreams(self):
        try:
            response = requests.get('{}/items/{}/bitstreams'.format(self.ds_client.base_url, self.uuid),
                                    headers=self.ds_client.headers,
                                    cookies={'JSESSIONID': self.ds_client.session},
                                    verify=self.ds_client.verify_ssl)
        except RequestException:
            logging.info('Could not get items')

        return response.json()

    def add_metadata(self, metadata):
        """
        Add metadata to a item
        :param handle:
        :param metadata:
        :return:
        """
        metadata = [m.__dict__ for m in metadata]

        try:
            response = requests.post(self.ds_client.base_url + '/items/' + self.uuid + '/metadata',
                                     headers=self.ds_client.headers,
                                     cookies={'JSESSIONID': self.ds_client.session},
                                     data=json.dumps(metadata),
                                     verify=self.ds_client.verify_ssl)
        except RequestException:
            logging.info('Could not add metadata to item: {}'.format(self.handle))

        if response.status_code != 200:
            logging.error('Could not add metadata to handle: {}'.format(self.handle))
            logging.error(response.status_code)
            logging.error(response.content)

        logging.info('Added {} metadata items to item: {}'.format(len(metadata), self.handle))


class DSpaceRestClient:
    def __init__(self, user, password, rest_url, verify_ssl, load_item_metadata=False):
        # Parameters for establishing connection
        self.user = user
        self.password = password
        self.rest_url = rest_url
        self.verify_ssl = verify_ssl
        self.session = None
        self.headers = {
            'Accept': 'application/json',
            "Content-Type": 'application/json',
        }

        self._parse_and_clean_urls()
        self.base_url = self.rest_url.scheme + '://' + self.rest_url.netloc + self.rest_url.path

        # Parameters for efficiency, i.e. don't get again what you should already have
        self.communities = None
        self.collections = None
        self.items = None
        self.load_item_metadata = bool(load_item_metadata)
        self.bitstreams = None

        self._login()

    def _login(self):
        """
         Log in to get DSpace REST API token.
        :return:
        """
        body = {'email': self.user, 'password': self.password}

        try:
            response = requests.post(self.base_url + '/login',
                                     data=body,
                                     verify=self.verify_ssl)

            if response.status_code != 200:
                raise LoginException()

            logging.info('Logged in to REST API.')
        except LoginException as e:
            logging.error('FATAL Error {} logging in to DSpace REST API, aborting'.format(response.status_code))
            sys.exit(1)
        except RequestException as e:
            logging.error('FATAL Error {} logging in to DSpace REST API, aborting\n{}'.format(response.status_code, e))
            sys.exit(1)

        set_cookie = response.headers['Set-Cookie'].split(';')[0]

        self.session = set_cookie[set_cookie.find('=') + 1:]

    def logout(self):
        """
        Logout from DSpace API
        :return:
        """

        try:
            response = requests.post(self.base_url + '/logout',
                                     headers=self.headers,
                                     cookies={'JSESSIONID': self.session},
                                     verify=self.verify_ssl)

            if response.status_code != 200:
                raise LogoutException()

            logging.info('Logged out of REST API.')
        except LogoutException as e:
            logging.error('Error logging out of DSpace REST API.\n{}'.format(e))
        except RequestException as e:
            logging.error('Error logging out of DSpace REST API.\n{}'.format(e))

    def _parse_and_clean_urls(self):
        self.rest_url = urlparse.urlparse(self.rest_url)

        if self.rest_url.scheme != 'https':
            self.rest_url = self.rest_url._replace(scheme='https')

        if not self.rest_url.port:
            self.rest_url = self.rest_url._replace(netloc=self.rest_url.netloc + ":443")

        logging.info('DS REST Cleaned: {}'.format(self.rest_url))

    def request_get(self, url):
        return requests.get(self.base_url + url,
                            headers=self.headers,
                            cookies={'JSESSIONID': self.session},
                            verify=self.verify_ssl)

    def _get(self, rest_url, ds_obj, offset, limit, results=[]):
        """
        Get *
        :param offset:
        :param results:
        :param limit:
        :return:
        """
        response = None
        try:
            response = self.request_get('/{}?offset={}&limit={}'.format(rest_url, offset, limit))
        except RequestException:
            logging.error('Could not get {}'.format(rest_url))

        if response.status_code == 200:
            results = results + [ds_obj(self, obj) for obj in response.json()]

            if offset < limit and len(response.json()) == limit:
                return self._get(rest_url, ds_obj, offset + limit, limit, results)
            else:
                return results
        else:
            return 'Could not get {}. \n{}'.format(rest_url, response.content)

    def get_items(self, offset=0, limit=100):
        """
        Get items
        :param offset:
        :param results:
        :param limit:
        :return:
        """
        items = self._get('items', Item, offset, limit)
        if not self.items:  # Store items a prop of client for future ref.
            self.items = items
        return items

    def get_top_communities(self, offset=0, limit=100):
        """
        Get items
        :param offset:
        :param results:
        :param limit:
        :return:
        """
        return self._get('communities/top-communities', Community, offset, limit)

    def get_communities(self, offset=0, limit=100):
        """
        Get communities
        :param offset:
        :param results:
        :param limit:
        :return:
        """
        communities = self._get('communities', Community, offset, limit)
        if not self.communities:  # Store communities a prop of client for future ref.
            self.communities = communities
        return self.communities

    def find_item_by(self, search_variable, search_string):
        if not self.items:
            self.get_items()

        return [c for c in self.items if search_string in getattr(c, search_variable)]

    def find_community_by(self, search_variable, search_string):
        if not self.communities:
            self.get_communities()

        return [c for c in self.communities if search_string in getattr(c, search_variable)]

    def delete_bitstream(self, file_name, items=None):
        if items is None:
            items = self.get_items()

        for item in items:
            bitstream_url = '{}://{}{}/bitstreams'.format(self.rest_url.scheme, self.rest_url.netloc, item['link'])
            bitstreams = json.loads(requests.get(bitstream_url,
                                                 headers=self.headers,
                                                 cookies={'JSESSIONID': self.session},
                                                 verify=False).content)

            for bitstream in bitstreams:
                # logging.info(bitstream)
                if 'name' in bitstream and bitstream['name'] == file_name:
                    delete_url = '{}/bitstreams/{}'.format(self.base_url, bitstream['uuid'])
                    logging.info(delete_url)
                    response = requests.delete(delete_url,
                                               headers=self.headers,
                                               cookies={'JSESSIONID': self.session},
                                               verify=False)

    @staticmethod
    def format_metadata(key, value, lang):
        """Reformats the metadata for the REST API."""
        return {'key': key, 'value': value, 'language': lang}
