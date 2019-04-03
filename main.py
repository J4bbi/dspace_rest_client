from dspace_rest_client import *


# TODO find object by name, or search string
# TODO find object by size, age, number of bitstreams,

DSpaceRestClient(user='dspacedemo+admin@gmail.com',
                 password='dspace',
                 rest_url='https://demo.dspace.org/rest',
                 verify_ssl=False,
                 load_item_metadata=True)

brexit_community = Community(name='Europe 2019')

print(brexit_community)

logout()