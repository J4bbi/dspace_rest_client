from dspace_rest_client import DSpaceRestClient, Metadata, Collection
import datetime


# TODO find object by name, or search string
# TODO find object by size, age, number of bitstreams,

d = DSpaceRestClient(user='dspacedemo+admin@gmail.com',
                     password='dspace',
                     rest_url='https://demo.dspace.org/rest',
                     verify_ssl=False,
                     load_item_metadata=True)

# items = d.get_items(limit=5)
#print(len(items))


#print(d.find_community('Sample'))

t = datetime.date(2019, 3, 18).timetuple()



#for c in d.find_item_by('uuid', '3'):
#    print(c)

for i in d.get_items():
    if(i.lastModified > t):
        print(i)

#for c in d.get_communities():
#    if c.countItems > 10:
#        print(c)
    #for cl in c.get_collections():

#        print(cl)



'''comm = d.get_top_communities()

print(comm[1].name)
print(comm[1].collections)

print(len(comm))'''

# print(items[0]['handle'])
#for item in d.get_items():
#    for m in item.metadata:
#        print(m)

# metadata = Metadata('dc.subject', 'Coldplay', 'en_GB')
# metadata2 = Metadata('dc.subject', 'Led Zeppelin', 'en_GB')

# print(json.dumps([metadata.__dict__]))

# print([str(m) for m in [metadata]])

# items[0].add_metadata([metadata, metadata2])

#for m in items[0].metadata:
#    print(m)

#d.update_record(items[0]['handle'], [d.format_metadata('dc.subject', 'interesting5')])
# d.add_metadata(items[0]['handle'], [d.format_metadata('dc.subject', 'go-kart')])
# for i in items:
#    print(json.dumps(d.get_metadata(i['handle']), indent=4, sort_keys=True))

# print(json.dumps(d.get_items(), indent=4, sort_keys=True))

d.logout()