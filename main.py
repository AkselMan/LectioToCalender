from __future__ import print_function
import datetime
import os.path
import lectio

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Før du gør noget med det program skal du have oprettet et google project,
# oprette en client secret og importere den til projektet som "credentials.json"

SCOPES = ['https://www.googleapis.com/auth/calendar']

today = datetime.datetime.today()

print("Lectio To Calender v0.1")
i_skoleId = input("Skole id (cg er '5'): ")
i_username = input("Dit bruger navn: ")
i_password = input("Dit password: ")

try:
    client = lectio.sdk(brugernavn=i_username, adgangskode=i_password, skoleId=i_skoleId)
except:
    print("Åh nej! Noget gik galt, prøv et andet brugernavn eller kodeord :)")
    quit()
    

i_week = input("Hvilken uges skema vil du gerne have (det er uge " + str(today.isocalendar()[1]) + " nu): ")

def getSkema():
    return client.skema(uge=i_week, år=today.year, id=client.elevId)

def convertTime(i):
    iLen = len(i)

    startTime = datetime.datetime.strptime(i[0:iLen-10], "%d/%m-%Y %H:%M")
    endTime = datetime.datetime( 
        year=startTime.year,
        month=startTime.month,
        day=startTime.day,
        hour=int(i[iLen-5:iLen-3]),
        minute=int(i[iLen-2:iLen])
    )

    return [str(startTime).replace(' ', 'T'), str(endTime).replace(' ', 'T')]


def main():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('calendar', 'v3', credentials=creds)

        skema = getSkema()["moduler"]
        
        for modul in skema:
            tid = convertTime(modul["tidspunkt"])

            event = {
            'summary': modul["hold"],
            'location': modul["lokale"],
            'description': modul["navn"],
            'start': {
                'dateTime': tid[0]+"+02:00"
            },
            'end': {
                'dateTime': tid[1]+"+02:00"
            }}

            event = service.events().insert(calendarId='primary', body=event).execute()
            print(modul["hold"] + ' tilføjet til kalender:' + "&" + (event.get('htmlLink')))

        print("Import af skema færdig!")


    except HttpError as error:
        print('Der skete en fejl... :( %s' % error)


if __name__ == '__main__':
    main()