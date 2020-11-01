import csv
import django
import logging
import os
import sys
import uuid
import yaml

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "MakeRPG.settings")
django.setup()

from oscar.apps.catalogue.categories import create_from_breadcrumbs
from oscar.apps.partner.importers import CatalogueImporter


class ItemImporter(CatalogueImporter):

    def __init__(self):
        logger = logging.getLogger('oscar.catalogue.import')
        super().__init__(logger)

    def _import(self, system_yaml):
        with open(system_yaml,'r') as yamlfile:
            tree = yaml.load(yamlfile)

        file_path = os.path.join( os.path.dirname(system_yaml) , 'items.csv' )

        with open(file_path, 'w') as csvfile:
            product_type = 'Item'
            fulfillment_partner = 'Item partner'
            stock = 1
            description = 'NULL'
            for item_cat in tree['items']:
                for item_type in tree['items'][item_cat]:
                    category = ' > '.join([ item_cat , item_type ])
                    for item in tree['items'][item_cat][item_type]:
                        uid = uuid.uuid5( uuid.NAMESPACE_OID , ' > '.join([ category , item ]) )
                        price = tree['items'][item_cat][item_type][item]['cost']
                        if not price:
                            price = 0

                        line = ','.join([
                            product_type,
                            category,
                            str(uid),
                            item,
                            description,
                            fulfillment_partner,
                            str(uid),
                            str(price),
                            str(stock)
                            ]) + '\n'
                        
                        csvfile.write(line)

        super()._import(file_path)


if __name__ == '__main__':
    system_yaml = 'Examples/shadowrun_5e/system.yaml'

    # needs error handling
    with open(system_yaml,'r') as yamlfile:
        tree = yaml.load(yamlfile)

    categories = []
    if 'items' not in tree:
        print('items not contained in tree: ' + system_yaml)
        sys.exit()

    for item_cat in tree['items']:
        for item_type in tree['items'][item_cat]:
            categories.append( ' > '.join([ item_cat , item_type ]) )

    # for breadcrumbs in categories:
    #     create_from_breadcrumbs(breadcrumbs)

    ItemImporter()._import(system_yaml)
