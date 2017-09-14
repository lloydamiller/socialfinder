#!/usr/bin/python

################################################################################################
#
#       Searches account-based websites for users with a specified username and returns
#           a json file of matching accounts.
#
#       Note: Includes some code borrowed from https://github.com/WebBreacher/WhatsMyName
#
#################################################################################################


import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import json
import random
import string

# Suppress HTTPS warnings
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                         'Chrome/45.0.2454.93 Safari/537.36'}

# Import data file with social media accounts
with open('social/web_accounts_list.json') as data_file:
    data = json.load(data_file)


def web_call(location):
    try:
        # Make web request for that URL, timeout in X secs and don't verify SSL/TLS certs
        r = requests.get(location, headers=headers, timeout=60, verify=False)
    except requests.exceptions.Timeout:
        return 'CONNECTION TIME OUT. Try increasing the timeout delay.'
    except requests.exceptions.TooManyRedirects:
        return 'TOO MANY REDIRECTS. Try changing the URL.'
    except requests.exceptions.RequestException as e:
        return 'CRITICAL ERROR. %s' % e
    except requests.exceptions.ConnectionError as e:
        return "CONNECTION ERROR: %s" % e
    else:
        return r


def check_username(username):

    username = str(username).lower()

    results = {username: {}}

    for site in data['sites']:
        code_match, string_match = False, False

        # Examine the current validity of the entry
        if not site['valid']:
            print(' *  Skipping %s - Marked as not valid.' % site['name'])
            continue
        if not site['known_accounts'][0] and not username:
            print(' *  Skipping %s - No valid user names to test.' % site['name'])
            continue

        # Perform initial lookup
        # Pull the first user from known_accounts and replace the {account} with it
        url_list = []
        if username:
            url = site['check_uri'].replace("{account}", username)
            url_list.append(url)
            uname = username
        else:
            account_list = site['known_accounts']
            for each in account_list:
                url = site['check_uri'].replace("{account}", each)
                url_list.append(url)
                uname = each

        for each in url_list:
            print('    Looking up %s' % site['name'])
            r = web_call(each)
            if isinstance(r, str):
                # web_call returns a string if there were an error
                print(' !  %s' % r)
                continue

            # Analyze the responses against what they should be
            if r.status_code == int(site['account_existence_code']):
                code_match = True
            else:
                code_match = False
            if r.text.find(site['account_existence_string']) > 0:
                string_match = True
            else:
                string_match = False

            if username:
                if code_match and string_match:
                    print(' +  Found user at %s' % each)
                    results[username][site['name']] = {
                        'name': site['name'],
                        'username': username,
                        'url': site['check_uri'].replace("{account}", username),
                        'source': 'Username check',
                        'link': '',
                    }
                continue

            # Check works if there is no passed username
            # Used for verifying the web_accounts_list.json file

            if code_match and string_match:
                print('[+] Response code and Search Strings match expected.')

                not_there_string = ''.join(
                    random.choice(string.ascii_lowercase + string.ascii_uppercase + string.digits)
                    for x in range(20))
                url_fp = site['check_uri'].replace("{account}", not_there_string)
                r_fp = web_call(url_fp)
                if isinstance(r_fp, str):
                    # If this is a string then web got an error
                    print(' ! ERROR on False Positive Check: %s' % r_fp)
                    continue

                if r_fp.status_code == int(site['account_existence_code']):
                    code_match = True
                else:
                    code_match = False
                if r_fp.text.find(site['account_existence_string']) > 0:
                    string_match = True
                else:
                    string_match = False
                if code_match and string_match:
                    print('[!]  ERROR: FALSE POSITIVE DETECTED. Response code and Search Strings match expected.')
                    results['sites'][site['name']]['notes'] = 'Possible False Positive'
                else:
                    results['sites'][site['name']]['verified'] = True
                    pass
            elif code_match and not string_match:
                # TODO set site['valid'] = False
                print('[!]  ERROR: BAD DETECTION STRING. "%s" was not found on resulting page' % site['account_existence_string'])
                results['sites'][site['name']]['notes'] = 'Bad detection string.'
            elif not code_match and string_match:
                # TODO set site['valid'] = False
                print('[!]  ERROR: BAD DETECTION RESPONSE CODE. HTTP Response code different than expected.')
                results['sites'][site['name']]['notes'] = 'Bad detection code. Received Code: %s; Expected Code: %s.' % (str(r.status_code), site['account_existence_code'])
            else:
                # TODO set site['valid'] = False
                print('[!]  ERROR: BAD CODE AND STRING. Neither the HTTP response code or detection string worked.')
                results['sites'][site['name']]['notes'] = 'Bad detection code and string. Received Code: %s; Expected Code: %s.' % (str(r.status_code), site['account_existence_code'])

    else:
        return results
