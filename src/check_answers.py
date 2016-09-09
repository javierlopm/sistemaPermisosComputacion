# -*- coding: utf-8 -*-
from __future__ import print_function
import gspread
from oauth2client.service_account import ServiceAccountCredentials

SCOPE = ["https://spreadsheets.google.com/feeds"]
SECRETS_FILE = "client_secret.json"




# Authenticate using the signed key
credentials = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', SCOPE)

gc = gspread.authorize(credentials)


print("Hojas de cálculo disponibles \n\n")
for sheet in gc.openall():
    print("{} - {}".format(sheet.title, sheet.id))
    print("▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔")
    for i,line in enumerate(sheet.get_worksheet(0).get_all_values()):
        print(str(i) + ".- " + str(line))
    print("\n\n")        
