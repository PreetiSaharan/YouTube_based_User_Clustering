
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import pymongo
import json
import httplib2
import os
import sys
import json
import re
from pymongo import MongoClient

from apiclient.discovery import build
from apiclient.errors import HttpError
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import argparser, run_flow

## Set DEVELOPER_KEY to the API key value from the APIs & auth
DEVELOPER_KEY = "AIzaSyBnqf2ktUzfanitbbPkoqEAYvwdIOFbLeM"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"


client=MongoClient('localhost',27017)
db=client['MyDatabase']
collection=db['mytable']

def youtube_search(options):
  youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
    developerKey=DEVELOPER_KEY)

## search.list method called to retrieve results matching the specified query term.
  search_response = youtube.search().list(
    q=options.q,
    part="id,snippet",
    maxResults=options.max_results
  ).execute()

  search_videos = []
  
  ## VideoIds are joined inorder to obtain the channel ids of the channels/users who posted the obtained videos
  videoId={}
  for search_result in search_response.get("items", []):
    if search_result["id"]["kind"] == "youtube#video":
      search_videos.append("%s (%s)" % (search_result["snippet"]["title"],
                                search_result["id"]["videoId"]))

      search_videos.append(search_result["id"]["videoId"])
      video_ids = ",".join(search_videos)
      videos_list_by_id(service,
          part='snippet',
          id= video_ids)

      


## The CLIENT_SECRETS_FILE variable specifies the name of a file that contains the OAuth 2.0 information for this application, including its client_id and client_secret.
CLIENT_SECRETS_FILE = "client_secrets.json"

## This OAuth 2.0 access scope allows for full read/write access to the authenticated user's account and requires requests to use an SSL connection.

YOUTUBE_READ_WRITE_SSL_SCOPE = "https://www.googleapis.com/auth/youtube.force-ssl"
API_SERVICE_NAME = "youtube"
API_VERSION = "v3"

## This variable defines a message to display if the CLIENT_SECRETS_FILE is missing.
MISSING_CLIENT_SECRETS_MESSAGE = "WARNING: Please configure OAuth 2.0" 

# Authorize the request and store authorization credentials.
def get_authenticated_service(args):
  flow = flow_from_clientsecrets(CLIENT_SECRETS_FILE, scope=YOUTUBE_READ_WRITE_SSL_SCOPE,
    message=MISSING_CLIENT_SECRETS_MESSAGE)

  storage = Storage("youtube-api-snippets-oauth2.json")
  credentials = storage.get()

  if credentials is None or credentials.invalid:
    credentials = run_flow(flow, storage, args)

  
  return build(API_SERVICE_NAME, API_VERSION,
      http=credentials.authorize(httplib2.Http()))


args = argparser.parse_args()
service = get_authenticated_service(args)


## Build a resource based on a list of properties given as key-value pairs.
## Leave properties with empty values out of the inserted resource.
def build_resource(properties):
  resource = {}
  for p in properties:

## Given a key like "snippet.title", split into "snippet" and "title", where "snippet" will be an object and "title" will be a property in that object.
    prop_array = p.split('.')
    ref = resource
    for pa in range(0, len(prop_array)):
      is_array = False
      key = prop_array[pa]
      # Convert a name like "snippet.tags[]" to snippet.tags, but handle
      # the value as an array.
      if key[-2:] == '[]':
        key = key[0:len(key)-2:]
        is_array = True
      if pa == (len(prop_array) - 1):

## Leave properties without values out of inserted resource.
        if properties[p]:
          if is_array:
            ref[key] = properties[p].split(',')
          else:
            ref[key] = properties[p]
      elif key not in ref:

## For example, the property is "snippet.title", but the resource does not yet have a "snippet" object. Create the snippet object here.Setting "ref = ref[key]" means that in the next time through the "for pa in range ..." loop, we will be setting a property in the resource's "snippet" object.
        ref[key] = {}
        ref = ref[key]
      else:

## For example, the property is "snippet.description", and the resource already has a "snippet" object.
        ref = ref[key]
  return resource

## Remove keyword arguments that are not set
def remove_empty_kwargs(**kwargs):
  good_kwargs = {}
  if kwargs is not None:
    for key, value in kwargs.iteritems():
      if value:
        good_kwargs[key] = value
  return good_kwargs


def videos_list_by_id(service, **kwargs):
  kwargs = remove_empty_kwargs(**kwargs) 
  results = service.videos().list(
    **kwargs
  ).execute()
  items=results.get("items")
  channels=[]
  for x in items:
     title= x["snippet"]["title"]
     description= x["snippet"]["description"]
     data={"title":title,
           "description":description
           }
     channels.append(data)

### filter the title and description of the videos by removing the STOP WORDS(extended the provided set in nltk)

     example_sent = title + description
     stop_words = set(stopwords.words('english'))
     word_tokens = word_tokenize(example_sent)
     word_tokens = set(map(lambda url: url.rstrip('/'),word_tokens )) ### here we are removing urls from the description (have plenty of Urls) and title

     filtered_sentence = [w for w in word_tokens if not w in      stop_words]
 
     filtered_sentence = []
 
     for w in word_tokens:
         if w not in stop_words:
            filtered_sentence.append(w) ###stop words removed
     
  
    # word_tokens = re.sub(r'\w+:\/{2}[\d\w-]+(\.[\d\w-]+)*(?:(?:\/[^\s/]*))*', '', filtered_sentence  )
     
    
 
    # print(word_tokens)
     print(filtered_sentence)
    # record=db.collection.insert(channels)
     
#  print (channels)


 # record=db.collection.insert(channels)

if __name__ == "__main__":
  argparser.add_argument("--q", help="Search term", default="apple")
  argparser.add_argument("--max-results", help="Max results", default=15) ###### OUTPUT= 2 (I.E. 1 less than the default value set) happens in every code 

  args = argparser.parse_args()

  try:
    youtube_search(args)
  except HttpError, e:
     print "An HTTP error %d occurred:\n%s" % (e.resp.status, e.content)
  

  














 

