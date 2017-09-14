#!/usr/bin/python

################################################################################################
#
#       Take an email addresses and find all related social media accounts
#
#################################################################################################


import fullcontact
import usernamesearch
import re

if __name__ == '__main__':

    # Get Name of Project

    projectname_raw = input("[?] Enter Subject Name: ")

    # Removes all special characters including spaces

    projectname_username = re.sub(r'\W+', '', projectname_raw).lower()

    entry = ''
    email_list, username_list = [], [projectname_username]
    blanks = ['n/a', '']

    while entry != 'run':
        entry = input('[?] Enter email/username, or type \'run\' to begin: ')
        email_verification = re.compile('[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+')

        if entry == 'run':
            pass

        elif email_verification.match(entry):
            email_list.append(entry)
            username_list.append(entry.split('@')[0].lower())

        else:
            username_list.append(entry.lower())

        email_list = list(set(email_list))

    email_results, username_results = {}, {}

    for email in email_list:
        email_results[email] = {}
        email_results[email] = fullcontact.from_email(email)

    for email in email_results:
        for sites in email_results[email]:
            for site in email_results[email][sites]:
                username_list.append(email_results[email][sites][site]['username'].lower())

    username_list = list(set(username_list) - set(blanks))

    for user in username_list:
        username_results.update(usernamesearch.check_username(user))

    #TODO merge username and email results into a unified system for looking at websites.
    # structure ['sites'][sitename][username][url + verification]

    '''
    # Loop through the username results and checks if matches existing email-linked account
    email_test = email_results
    for user in username_results:
        for account_user in username_results[user]:
            for email in email_test:
                for account_email in email_test[email]:
                    for source in email_test[email][account_email]:
                        if email_test[email][account_email][source]['name'] == account_user and email_test[email][account_email][source]['username'] == user:
                            #TODO Take some action here
    '''

    print("[*] Creating file for %s" % projectname_username)

    # Replace spaces with underscores
    filename = "%s_social_media_accounts.html" % re.compile('[\W_]+').sub('', projectname_username)

    title = "Possible Social Media Accounts For %s\n\n" % projectname_username

    opener = """<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
    "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
    <html>
        <head>
        <meta content="text/html; charset=ISO-8859-1" http-equiv="content-type">
        <title>%s</title>
        </head>
    <body>
    <h1>%s</h1>
    """ % (title, title)

    closer = """</body>
    </html>
    """

    with open(filename, "a") as f:

        f.write(opener)

        for email in email_results:

            f.write('<h3>Email: %s </h3>' % email)

            if len(email_results[email]) == 0:
                f.write('No accounts found for email address<br>\n')

            else:

                for user in email_results[email]:
                # TODO See if this works to catch email results with no accounts
                    for account in email_results[email][user]:
                        f.write('<a href="%s" target="_new">%s</a>\n<br \>\n' % (email_results[email][user][account]['url'], account))

        f.write('\n<br \><h3>Accounts With Associated Usernames</h3>')

        f.write('<div>\n')

        for user in username_results:
            f.write('<div style="float: left; width: 200px;"><h4>%s</h4>\n' % user)
            for account in username_results[user]:
                f.write('<a href="%s" target="_new">%s</a>\n<br>\n' % (username_results[user][account]['url'], account))
            f.write('</div>\n')
        f.write('</div>\n<br \>\n')

        f.write(closer)

    f.close()

    pass
