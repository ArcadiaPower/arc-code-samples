#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 12 09:49:44 2023
@author: ed.english@arcadia.com
please note these are illustrative code examples
you should review and test thoroughly before including
in a production implementation

"""

import json
import requests


# AUTHENTICATE TO UTILITY CLOUD
# -----------------------------

# this function returns the jwt token required to access your utility cloud
# account.  the returned token is used in the request headers

def getToken(username, password, authurl):    
    authdata = { 'username' : username, 'password' : password }
    authreq = requests.post(authurl, data=json.dumps(authdata), verify=False)
    token = None
    if authreq.status_code == 200:
        response = authreq.json()
        token = response['token']
    return token


baseurl = 'https://api.urjanet.com/'
authurl = baseurl+'auth/login'
token = getToken(username, password, authurl)
headers = { 'Authorization' : 'Bearer ' + token }




# CREATE A USER WITH THE API
# ------------------------


# this gets a list of all the roles and selects Admin role from the list

allroles = requests.get(baseurl+'roles', headers = headers).json()
for r in allroles['_embedded']['roles']:
    if r['name'] == 'ROLE_CUSTOMER_ADMIN':
        role = r['_links']['self']['href']

# this gets the organization Id

organization = 'https://api.urjanet.com/organizations/'+ str(requests.get(baseurl+'utility/organization', headers = headers).json()['entityId'])

# the organization and role fields take the form of
# https://api.urjanet.com/organizations/000 and 'https://api.urjanet.com/roles/00'

userdata = {
  "accountEnabled": True,
  "autoGeneratePassword": False,
  "credentialsExpired": False,
  "email": "...your email...",
  "name": "...your name...",
  "organization": organization,
  "password": "...your password...",
  "passwordConfirm": "...your password...",
  "roles": [role],
  "username": "...your username..."
}

# creates the new user with the attributes in userdata
# an http status code of 201 indicates success

newuser = requests.post(baseurl+'users', headers = headers, data=json.dumps(userdata))




# CREATE CUSTOM DATA FIELDS
# -------------------------

# lists the current custom data fields for your organization

customdatafields = requests.get(baseurl+'utility/organization', headers = headers).json()


# updates the labels for custom data.  there are up to 10 for account and meter level

datafields = {'accountCustomData1Name': '...your account data field 1....',
              'accountCustomData2Name': '...your second account data field...',
              'meterCustomData1Name': '...your meter data field 1...'}

customdata = requests.patch(baseurl+'utility/organization', headers = headers, data=json.dumps(datafields))




# CREATE SITES
# -------------


sitefields = {
  "city": "...yourcity...",
  "country": "...yourcountry...",
  "facilityType": None,
  "postalCode": "...yourzip...",
  "region": None,
  "siteCode": None,
  "siteName": "...yoursitename...",
  "siteNumber": None,
  "subRegion": None,
  "state": "...yourstate...",
  "streetLine1": "...yourstreet...",
  "streetLine2": None
}

# creates the new site

newsite = requests.post(baseurl+'utility/sites', headers = headers, data=json.dumps(sitefields)).json()

# the unique Id of the newly created site

newsiteId = newsite['entityId']

# lists the fields for the newly created site

siteinfo = requests.get(baseurl+'utility/sites/'+newsiteId, headers = headers).json()

# modifying an existing site

updatesitefields = {"country": "USA"}
updatedsite = requests.patch(baseurl+'utility/sites/'+newsiteId, headers = headers, data=json.dumps(updatesitefields)).json()




# FIND UTILITY WITH RSQL AND CREATE A CREDENTIAL
# -------------------------------------------------

# RSQL is a query language for parametrized filtering for RESTful APIs
# this returns a list of all utilities with "Virginia" in the name

providerquery = 'providerName==Virginia*'
utilitylist = requests.get(baseurl+'utility/providers?search='+providerquery, headers = headers).json()

# you will select the specific one that you need from the list
# this sample just picks the first one

utilityId = utilitylist['_embedded']['providers'][0]['providerId']

# normally a utility credential will be username/password but some utilities will
# have additional requirements, such as a PIN or challenge/response questions
# these inputs are contained in the usernameN and passwordN fields
# details on required fields are provided in the get utility response payload

credential = {
  "correlationId": "...yourcorrelationId...",
  "interactive": True,
  "providerId": utilityId,
  "username": "....utilityaccountusername....",
  "username2": "",
  "username3": "",
  "username4": "",
  "password": "....utilityaccountpassword",
  "password2": "",
  "password3": "",
  "password4": ""
}

# creates the credential for the selected utility

newcredential = requests.post(baseurl+'utility/credentials', headers = headers, data=json.dumps(credential))




# SUBMIT A STATEMENT DIRECTLY TO UTILITY CLOUD
# --------------------------------------------

# file submission suppored by local files only
uploadfile = {'file': open('....yourpdffilename','rb')}

# depding on your system configuration python requests module may not support redirects properly in which case you
# may be required to submit to the following URL instead 'https://downloads.urjanet.net/utility/files'

submitfile = requests.post(baseurl+’/utility/files', headers = headers, files=uploadfile, allow_redirects=True)

# OR alternatively, 
#curl --location 'https://api.urjanet.com/utility/files' \
#--header 'Content-Type: multipart/form-data' \
#--header 'Authorization: Bearer <token> \
#--form 'files=@"<file name>"'




# FINDING AND MOVING METERS TO NEW SITES
# --------------------------------------------

# this will find the sites with “Campus” in the name, and all the meters with “Virginia” in the utility name.  Note that other fields are searchable as well.

sitequery = 'siteName==Campus*'
sitelist = requests.get(baseurl+'utility/sites?search='+sitequery, headers = headers)

providerquery = 'providerName==Virginia*'
meterlist = requests.get(baseurl+'utility/meters?search='+providerquery, headers = headers)

# for the selected meterID to move to a new siteID found from the query above

﻿newsite = {"site": "yoursiteID"}

﻿updatedsite = requests.patch(baseurl+’utility/meters/'+yourmneterID, headers = headers, data=json.dumps(newsite))





# TESTING YOUR API WITH PAGINATED RESULTS
# --------------------------------------------

# by default, most data responses will return a paginated set of results
# below is a helper function to return all (or limited to a subset) of responses
# for the specified data in UC

def getpaginated(url, entity, goget):
    
    #url is the first result in a paginated set, typically for a list request
    #entity is the type of data to get:  statements, provider...
    #goget is the number of pages, which can be useful for limiting results for
    #testing purposes
    
    plist = []
    
    morepages = True
    plink = url+entity
    
    counter = 1
    
    while morepages:
    
        preq = requests.get(plink, headers=headers, verify=False)
        
        if preq.status_code == 200:
            resp = preq.json()
            page = resp['page']
            links = resp['_links']
            ps = resp['_embedded'][entity]
            
            for p in ps:
                plist.append(p)
            
            # checks if this is the last page and if not will go to next page
            if links['self']['href'] == links['last']['href']:
                morepages = False
            else:
                plink = links['next']['href']
    
        else:
            morepages = False
        
        counter = counter + 1
        
        if counter > goget:
            morepages = False
        
    return plist



queryurl = baseurl+'utility/'

# gets one page of statements
stmt = requests.get(queryurl+'statements', headers = headers).json()

# gets all statements
allstmt = getpaginated(queryurl, 'statements', 999999)
