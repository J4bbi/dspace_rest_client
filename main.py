from dspace_rest_client import *
import bs4 as bs


d = DSpaceRestClient(user='hrafn.malmquist@ed.ac.uk',
                     password='Skila100hrofnum',
                     rest_url='https://digitalpreservation.is.ed.ac.uk/rest',
                     verify_ssl=True,
                     load_item_metadata=False)

root_community = d.find_community_by('uuid', '7cd0a581-f3ff-43b2-9326-bae225b26a78')[0]

soup = bs.BeautifulSoup(open('eerc/hierarchy.html'), "html.parser")

table = soup.table

table_rows = table.find_all('tr')

for tr in table_rows:
    table_cells = tr.find_all('td')

    # if
    # print(len(table_cells))

    for td in table_cells:
        # print(td['class'])
        if td['class'][0] == 'title':
            print(td.text)

            if 'Creedon' in td.text:
                root_community.create_collection(td.text + '22')

print(root_community)
# 7cd0a581-f3ff-43b2-9326-bae225b26a78

# TODO find object by name, or search string
# TODO find object by size, age, number of bitstreams,


'''DSpaceRestClient(user='dspacedemo+admin@gmail.com',
                 password='dspace',
                 rest_url='https://demo.dspace.org/rest',
                 verify_ssl=False,
                 load_item_metadata=True)'''

'''d = DSpaceRestClient(user='hrafn.malmquist@ed.ac.uk',
                     password='Skila100hrofnum',
                     rest_url='https://aura.abdn.ac.uk/rest',
                     verify_ssl=False,
                     load_item_metadata=False)'''

d = DSpaceRestClient(user='hrafn.malmquist@ed.ac.uk',
                     password='Skila100hrofnum',
                     rest_url='https://digitalpreservation.is.ed.ac.uk/rest',
                     verify_ssl=True,
                     load_item_metadata=False)

#for community in d.get_communities():
#    print(community)

#brexit_community = Community(name='Europe 2019')

#print(brexit_community)

logout()