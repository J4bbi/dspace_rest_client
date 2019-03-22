# DSpace REST API client

The idea for this Python DSpace REST API is to make CRUD and other querying easy.

It should be noted that [REST Based Quality Control Reports](https://wiki.duraspace.org/display/DSDOC6x/REST+Based+Quality+Control+Reports)
are accessible via a neat web UI. See for instance [here](https://demo.dspace.org/rest/static/reports/query.html).

Written in Python3 and requires no external packages.

There is a class for each respective [DSpace object type](https://wiki.duraspace.org/display/DSDOC6x/REST+API#RESTAPI-Model-Objectdatatypes):
Community, Collection, Item and Bitstream as well as a wee Metadata wrapper object.

By default the `load_item_metadata` parameter is set to `False` because usually we
don't want to download the entire metadata of each item. The REST API gets around
this overload problem by offering the optional
[expand](https://wiki.duraspace.org/display/DSDOC6x/REST+API#RESTAPI-RESTEndpoints)
parameter whereby you instruct the API explicitly to return related information. 

If `load_item_metadata` is set to `True` a separate API call will be made to
retrieve metadata on each time. This can take **quite** some time if say
querying all items in a 1000 item DSpace. So use with caution.

## Usage
The following example establishes a connection to a server and prints out the
name of the first top-level community.

 ```python
 import dspace_rest_client

d = DSpaceRestClient(user='dspacedemo+admin@gmail.com',
                     password=PASSWORD,
                     rest_url='https://demo.dspace.org/rest',
                     verify_ssl=False)
top_communites = d.get_top_communities()
print(top_communites[0].name)
d.logout()
 ```
 
 You can also do more complex queries. For instance, this query returns items
 that have been modified after March 18th 2019.
 
 ```python
 import dspace_rest_client

d = DSpaceRestClient(user='dspacedemo+admin@gmail.com',
                     password=PASSWORD,
                     rest_url='https://demo.dspace.org/rest',
                     verify_ssl=False)

t = datetime.date(2019, 3, 18).timetuple()

for i in d.get_items():
    if(i.lastModified > t):
        print(i)
d.logout()
 ```
 
 ## TODO
 