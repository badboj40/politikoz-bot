import time
import tools

settings_all_assets = {
        'sort': 'price:1',
        'type': 'listing',
	'max pages': 1000,
	'sold': 'false',
}

while True:
	assets = tools.get_assets(settings_all_assets)
	tools.save_to_file(assets)	
	time.sleep(300)
	
