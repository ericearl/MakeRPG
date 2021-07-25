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
        super().__init__(logger, flush=True)

    def _import(self, system_yaml):
        with open(system_yaml,'r') as yamlfile:
            tree = yaml.load(yamlfile)

        file_path = os.path.join( os.path.dirname(system_yaml) , 'items.csv' )

        with open(file_path, 'w') as csvfile:

            product_type = 'Item'
            fulfillment_partner = 'Item partner'
            stock = 1

            for item_cat in tree['items']:
                for item_type in tree['items'][item_cat]:
                    category = ' > '.join([ item_cat , item_type ])

                    item_list = [item for item in tree['items'][item_cat][item_type]]
                    for item in reversed(item_list):
                        item_dict = tree['items'][item_cat][item_type][item]

                        uid = uuid.uuid5( uuid.NAMESPACE_OID , ' > '.join([ category , item ]) )
                        price = item_dict['cost']
                        if not price:
                            price = 0

                        if ('qty' in item_dict or \
                            'unit' in item_dict or \
                            'skill' in item_dict or \
                            'require' in item_dict or \
                            'specifics' in item_dict):
                            description = ''
                        else:
                            description = 'NULL'

                        if 'qty' in item_dict:
                            description += 'Quantity: ' + str(item_dict['qty']) + '  |  '

                        if 'unit' in item_dict:
                            description += 'Units: ' + str(item_dict['unit']) + '  |  '

                        if 'skill' in item_dict:
                            description += 'Skill: ' + str(item_dict['skill']) + '  |  '

                        if 'require' in item_dict:
                            description += 'Requires: ' + str(item_dict['require']) + '  |  '

                        if 'specifics' in item_dict:
                            specifics = []

                            for key in item_dict['specifics']:
                                value = item_dict['specifics'][key]
                                specifics.append( str(key) + ': ' + str(value) )

                            description += '  |  '.join(specifics)

                        if 'specifics' in item_dict and 'mods' in item_dict:
                            description += '  |  '

                        if 'mods' in item_dict:
                            modifiers = []
                            levelly = {}

                            for being_modified in item_dict['mods']:
                                modifier_dict = item_dict['mods'][being_modified]

                                for modifier in modifier_dict:
                                    modifiers.append(modifier)
                                    levelly[modifier] = []
                                    for level in modifier_dict[modifier]:
                                        levelly[modifier].append(level)

                                modifiers = list(set(modifiers))

                            if modifiers:
                                description += 'MODIFIERS --> '

                            for modifier in modifiers:

                                for lev in levelly[modifier]:
                                    mods = []
                                    first_appearance = True

                                    for being_modified in item_dict['mods']:
                                        modifier_dict = item_dict['mods'][being_modified]

                                        for moddy in  modifier_dict:
                                            for level in modifier_dict[moddy]:
                                                if modifier == moddy and level == lev:
                                                    if first_appearance:
                                                        description += modifier + '(' + str(lev) + '): '
                                                        first_appearance = False

                                                    mods.append(being_modified + str(modifier_dict[modifier][level]))

                                    description += ' ; '.join(mods) + ' ; '

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
