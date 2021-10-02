import requests
import json
import math
from prettytable import PrettyTable

# Import credentials
with open("credentials.json") as f:
    data = json.load(f)

clientId = data["client-id"]
clientSecret = data["client-secret"]

def validation(input):
    return (input == "") or not (input.replace(" ", "").isalnum())

artist = ""
while validation(artist):
    artist = input("Which artist do you want to search for? ")

    if validation(artist):
        print("- Not a valid input, please try again.\n")

# Make POST request and store auth token
response = requests.post("https://accounts.spotify.com/api/token", {
    'grant_type': 'client_credentials',
    'client_id': clientId,
    'client_secret': clientSecret,
})

if response.status_code != 200:
    print("Unable to authenticate due to following error code:", response.status_code)
    quit()

# Convert response to json Object
response = response.json()

# Add the auth token to the headers
authStr = str(response["token_type"]) + " " + str(response["access_token"])
headers = {
    'Accept': 'application/json',
    'Content-Type': 'application/json',
    'Authorization' : authStr
}

# Format the params
params = (
    ('type', 'artist'),
    ('q', artist),
)

page = requests.get("https://api.spotify.com/v1/search", headers=headers, params=params).json()

# Check if the request was successfull
if "error" in page:
    print("\nSomething went wrong!")
    print(f"- {str(page['error']['status'])}: {page['error']['message']}")
    quit()

# Sends warning if query success
total = page["artists"]["total"]
if total > 300:
    resume = ""
    while resume.lower() not in ["y", "n"]:
        resume = input(f"\nAre you sure you want to search for {str(total)} artists?\nThis will query the api a total of {math.ceil(int(total)/20)} times. y/n ")
    if resume.lower() == "n":
        quit()
    else:
        print("Fetching results...")

# Visualizing Content
t = PrettyTable()
t.field_names = ["id", "name", "genres", "popularity", "followers", "uri"]

# function that is used to add the artists of a page to the table
def addPageToTable(artists):
    for artist in artists:
        t.add_row([artist["id"], artist["name"], artist["genres"], artist["popularity"], artist["followers"]["total"], artist["uri"]])

# Iterate over all "pages", each page contains max. 20 artists
nextUrl = page["artists"]["next"]
while nextUrl != None:
    # Add each artist from the page to the PrettyTable
    addPageToTable(page["artists"]["items"])

    # Get artists of next pages url
    page = requests.get(nextUrl, headers=headers).json()
    nextUrl = page["artists"]["next"]

# Add artists from the last page to the PrettyTable
addPageToTable(page["artists"]["items"])

# Print the table
print(t)
