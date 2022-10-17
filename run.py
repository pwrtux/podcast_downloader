
from dataclasses import dataclass
import requests
from pprint import pprint
import shutil
from tqdm.auto import tqdm
import podcastindex
from dotenv import load_dotenv
import os

load_dotenv()

config = {
    "api_key": os.getenv("api_key"),
    "api_secret": os.getenv("api_secret")
}



# Represent a Feed of a single Podcast
@dataclass
class Feed:
    id: int
    title: str
    url: str
    originalUrl: str
    link: str
    description: str
    author: str
    ownerName: str
    image: str
    artwork: str
    lastUpdateTime: int
    lastCrawlTime: int
    lastParseTime: int
    lastGoodHttpStatusTime: int
    lastHttpStatus: int
    contentType: str
    itunesId: int
    generator: str
    language: str
    type: str
    dead: bool
    crawlErrors: int
    parseErrors: int
    categories: str
    locked: bool
    explicit: bool
    episodeCount: int
    imageUrlHash: str


# Represents a single Podcast
@dataclass
class Podcast:
    status: bool 
    feeds: list[Feed]
    count: int
    query: str
    description: str



def pod_request(query):
    index = podcastindex.init(config)
    result = index.search(query)   
    return result

def get_all_feeds(Podcastobj: Podcast):
    all_feeds = []
    for x in Podcastobj.feeds:
        all_feeds.append(Feed(**x))
    return all_feeds

def display_pods(all_feeds):
    if isinstance(all_feeds, list):
        for index, podcast in enumerate(all_feeds):
            print("")
            print(f"#  No: {index}")
            print("🎵 Title: ", podcast.title)
            print("🥸  Author: ", podcast.author)
            print("📝 Description: ", podcast.description)
            print("📜 Episodes: ", podcast.episodeCount)
            
        print("=====================================")
        return

    elif not isinstance(all_feeds, list):
        print("=====================================")
        print("🎵 Title: ", all_feeds.title)
        print("🥸  Author: ", all_feeds.author)
        print("📝 Description: ", all_feeds.description)
        print("📜 Episodes: ", all_feeds.episodeCount)
        print("=====================================")
        return

def show_query_results(query):
    feed = Podcast(**pod_request(query))
    all_feeds = get_all_feeds(feed)
    if (feed.count) == 0:
        print(f"No Podcasts found for query: {query}")
        print("Please try another query")
        return
    print("")
    print("=====================================")
    print("Found Podcasts:")
    print("=====================================")
    display_pods(all_feeds)

    print("")
    podcast_choice = int(input("Choose your Podcast by entering the number: "))

    if podcast_choice >= len(all_feeds) or podcast_choice < 0:
        print("Invalid choice")
        return

    print("")
    display_pods(all_feeds[podcast_choice])
    return all_feeds[podcast_choice]
    
def get_episodes(podcast: Feed):
    index = podcastindex.init(config)
    episodes = index.episodesByFeedId(podcast.id, None, 1000) # 1000 is maximum
    return episodes



def download(data: Podcast):

    choice = input("Do you want to download all episodes now? (y/n)")

    if choice == 'n':
        print("Download aborted")
        return


    for episode in data['items']:
        print("Downloading: ", episode['title'])
        r = requests.get(episode['enclosureUrl'], stream=True)
        total_length = int(r.headers.get("Content-Length"))
        with tqdm.wrapattr(r.raw, "read", total=total_length, desc="") as raw:
            with open(f"{episode['title']}.mp3", 'wb') as f:
                shutil.copyfileobj(raw, f)
            print("Downloaded: ", episode['title'])
            print("=====================================")

    
    

if "__main__" == __name__:
    print("🎧Welcome to the Podcast Downloader🎧")
    print("=====================================")
    print("Please beware that this search is not typo tolerant.")
    print("Current maximum number of episodes per podcast is 1000.")
    print("=====================================")
    query = input("Enter your Podcast search query: ")
    pod = show_query_results(query)
    all_episodes = get_episodes(pod)
    items = all_episodes["items"]

    ep_choice = input(f"Do you want to list all {(pod.episodeCount)} episodes? (y/n)")
    if ep_choice == 'y':
        for item in items:
            print(item["title"])
            print("=====================================")
    
    download(all_episodes)





