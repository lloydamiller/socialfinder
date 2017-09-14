#!/usr/bin/python

################################################################################################
#
#       Query full contact database and return JSON of information
#
#################################################################################################

import requests
import re
import time
import json

def from_email(email):

    # validate email
    if not re.compile('[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+').match(email):
        print("[!] ERROR: Invalid Email Address")
        return
    else:
        email = email.lower()

    results = {}

    full_contact_api_key = "" # Enter Full Contact API Key

    headers = {'X-FullContact-APIKey': full_contact_api_key}

    print("[*] SEARCH accounts from email: %s" % email)

    url = "https://api.fullcontact.com/v2/person.json?email=%s" % email

    code = 0

    while code != 200:

        response = requests.get(url, headers=headers)

        code = response.status_code

        if response.status_code == 200:

            contact_object = response.json()

            if 'socialProfiles' in contact_object:

                for profile in contact_object['socialProfiles']:
                    results[profile.get("username", email)] = {
                        profile.get("typeName", "N/A"): {
                            'name': profile.get("typeName", "N/A"),
                            'username': profile.get("username", "N/A"),
                            'url': profile.get("url", "N/A"),
                            'source': 'FullContact Email',
                            'link': 'email: %s' % email,
                        }
                    }

            else:
                pass


        elif response.status_code == 202:
            print(" - Sleeping for 60 seconds...")
            time.sleep(60)

        else:
            response_message = response.json()
            if response_message["message"]:
                print(" !  ERROR: %s " % response_message["message"])
                code = 200

    print('[!] Found %i social media accounts' % len(results))

    return results

if __name__ == '__main__':
    email = input('[?] Enter Email Address: ')
    full_contact_api_key = '905dca998f3f69d2'
    headers = {'X-FullContact-APIKey': full_contact_api_key}
    url = 'https://api.fullcontact.com/v2/person.json?email=%s' % email
    print('[*] Querying FullContact Database')
    code = 0
    while code != 200:

        response = requests.get(url, headers=headers)

        code = response.status_code

        if response.status_code == 200:

            contact_object = response.json()
            filename = email.replace('@','_')
            filename = filename.replace('.', '_') + '_output.txt'
            print('[*] Printing output file %s' % filename)
            with open(filename, 'w') as outfile:
                json.dump(contact_object, outfile, sort_keys=True, indent=4, ensure_ascii=False)

        elif response.status_code == 202:
            print('[*] Sleeping for 60 seconds...')
            time.sleep(60)

        else:
            response_message = response.json()
            if response_message['message']:
                print('[!] ERROR: %s ' % response_message['message'])
                code = 200

    print('[*] Finished')