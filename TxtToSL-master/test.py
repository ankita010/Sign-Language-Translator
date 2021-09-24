import nltk 

class ansi:
  '''
  Contains ANSI escape characters for ANSI colour in the terminal.
  '''

  BLUE = '\033[94m'
  YELLOW = '\033[93m'
  GREEN = '\033[92m'
  RED = '\033[91m'

  BOLD = '\033[1m'

  END = '\033[0m'


from yaspin import yaspin
import requests
import os
import re
from bs4 import BeautifulSoup
import argparse
import copy
from moviepy.editor import VideoFileClip, concatenate_videoclips, TextClip, CompositeVideoClip


os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide" # Hide pygame / moviepy startup / welcome message

print()

cache = True
subtitles = True

phrases = []
autoskip = []

def get_word_synonyms(word):

  with yaspin(text="Getting synonyms for word '{}'".format(word)) as sp:
    r = requests.get("https://api.datamuse.com/words?ml={}&max=1000".format(word))

    if r.status_code == 200:
      sp.ok(ansi.GREEN + "✓" + ansi.END)

      return r.json()
    else:
      sp.fail(ansi.RED + "✗" + ansi.END)

      return False

def get_related_synonyms(word):
  word_synonyms = get_word_synonyms(word)
  first_word_synonyms = get_word_synonyms(word_synonyms[0]["word"])

  word_tags = None

  for synonym in first_word_synonyms:
    if synonym["word"] == word:
      word_tags = synonym["tags"]

  word_tags.remove("syn")

  print(word_tags)

  if word_tags == None:
    return False
  
  result = list()

  for synonym in word_synonyms:
    try:
      if synonym["tags"] == word_tags:
        result.append(synonym["word"])
    except:
      pass

  return result
  
def spellout(word):
  spellout = list(word)

  for char in spellout:
    if lang == "BSL" or lang == "ASL":
      content = signorg_getvid(char)

    if content != "cache":
      savevid(content, char)
        
  return spellout

def no_video(word):
  
  global lang

  if word[0] == "[": 
    if word[len(word) - 1] == "]":
      print("{}Auto spellout{}".format(ansi.BLUE, ansi.END))
      return spellout(word.replace('[', '').replace(']', ''))
  
  print("Attempting synonyms")

  # Auto synonym trying
  synonyms = get_related_synonyms(word.replace('[', '').replace(']', ''))

  for synonym in synonyms:
    if lang == "BSL":
      content = signorg_getvid(synonym, True)
    

    if content != "cache" and content is not False:
      print(synonym)

      savevid(content, synonym)

      return [ synonym ]
    

  return no_video_prompt(word)

def no_video_prompt(word):

  global lang

  while True:
      print("{}No videos found for '{}'.{} Please choose an option:\n1) Spellout\n2) Skip\n3) Abort (Exit Program)".format(ansi.RED, word, ansi.END))
      innum = input("Number: ")

      if innum == "1":
        print("{}Spellout{}".format(ansi.BLUE, ansi.END))
        return spellout(word)

      elif innum == "2":
        return False
      elif innum == "3":
        exit()

def signorg_getpage(word):

  global cache, lang

  with yaspin(text="Getting main page for word '{}'".format(word)) as sp:
    if not os.path.isfile('Data_TxtToSL/cache/{}/words/{}.mp4'.format(lang.lower(), word.replace(' ', '-'))) or not cache:
      if lang == "BSL": # Would use sign{}.com or sign{}.org but bsl is .com and asl is .org
        url = "https://signbsl.com/sign/{}".format(word.replace(' ', '-'))
      
      r = requests.get(url)

      if r.status_code == 200:
        sp.ok(ansi.GREEN + "✓" + ansi.END)

        return r.content
      else:
        sp.fail(ansi.RED + "✗" + ansi.END)

        return False
    else:
      sp.ok(ansi.YELLOW + "✓" + ansi.END)

      return "cache"

def signorg_getvid(word, synonym=False):
  global cache, lang

  replaced = word.replace('[', '').replace(']', '')
  page = signorg_getpage(replaced)

  if page == "cache":
    return page

  if page == False:
    if synonym:
      return False
    else:
      return no_video(word)

  soup = BeautifulSoup(page, features="html.parser")
  vids = soup.find_all('source')

  if len(vids) == 0: # No videos / word not in dict.
    if synonym:
      return False
    else:
      return no_video(word)
    
  for vid in vids:
    url = vid['src']

    provider = "unavaliable"

    try:
      provider = re.search("{}\ /.*\ /".format(lang.lower()), url).group().replace("{}/".format(lang.lower()), '').replace('/mp4/', '').replace('/', '')
    except:
      print("{}Unable to find provider{}".format(ansi.YELLOW, ansi.END))
    
    with yaspin(text="Getting video for '{}' with provider '{}'".format(word, provider)) as sp:
      r = requests.get(url)

      if r.status_code == 200:
        sp.ok(ansi.GREEN + "✓" + ansi.END)

        return r.content
      else:
        sp.fail(ansi.RED + "✗" + ansi.END)
  
# def dgs_apirequest(word):
#   with yaspin(text="Sending Signdict API Request for '{}'".format(word)) as sp:
#     # online beautifier
#     url = "https://signdict.org/graphql-api/graphiql" 
#     data = { "query": "{{ search(word: \"{}\") {{ id text type currentVideo {{ videoUrl license copyright originalHref user {{ name }} }} }} }}".format(word) }
    
#     r = requests.post(url, data=data)

#     if r.status_code == 200:
#       sp.ok(ansi.GREEN + "✓" + ansi.END)

#       return r.json()
#     else:
#       sp.fail(ansi.RED + "✗" + ansi.END)
    

# def dgs_getvid(word, synonym=False):
#   '''
#   Gets video of word by using Signdict's API.
#   Depends on global variables: cache, lang

#   :param word: Word to get video for.
#   :returns: Video content (mp4).
#   '''

#   global cache

#   replaced = word.replace('[', '').replace(']', '').replace(' ', '-')

#   if os.path.isfile('Data_TxtToSL/cache/dgs/words/{}.mp4'.format(replaced)) and cache:
#     return "cache"
#   else:
#     req = dgs_apirequest(replaced)

#     if len(req["data"]["search"]) == 0:
#       if synonym:
#         return False
#       else:
#         return no_video(word)
    
#     for video in req["data"]["search"]:
#       with yaspin(text="Getting video for '{}'".format(word)) as sp:
#         r = requests.get(video["currentVideo"]["videoUrl"])

#         if r.status_code == 200:
#           sp.ok(ansi.GREEN + "✓" + ansi.END)

#           return r.content
#         else:
#           sp.fail(ansi.RED + "✗" + ansi.END)

#           return False


def savevid(content, word):
  global lang

  replaced = word.replace('[', '').replace(']', '').replace(' ', '-')

  if content == None: # Unable to get / find word
    print("{}ERROR: Tried to save word '{}' but content is None. Press any key to skip word.{}".format(ansi.RED, word.replace('[', '').replace(']', ''), ansi.END))
    input()

    return False
  
  with yaspin(text="Saving video file 'Data_TxtToSL/cache/{}/words/{}.mp4'".format(lang.lower(), replaced)) as sp:
    if content != "cache":
      with open('Data_TxtToSL/cache/{}/words/{}.mp4'.format(lang.lower(), replaced), 'wb') as f:
        f.write(content)

      sp.ok(ansi.GREEN + "✓" + ansi.END)

  return True

full = None
lang = None

def str2bool(v):
    if isinstance(v, bool):
       return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')

def getargs():

  global cache, full, lang, subtitles

  parser = argparse.ArgumentParser()

  parser.add_argument("-c", "--cache", type=str2bool,
                      help="whether to use and save local cache (bool)", default=True)
	
  parser.add_argument("-i", "--input", type=str,
                      help="the input to translate (str)", default=None)

  parser.add_argument("-l", "--lang", type=str,
                      help="the sign language to use (str)", default=None, choices=["BSL", "ASL", "DGS"])

  parser.add_argument("-s", "--subtitles", type=str2bool,
                      help="whether to put subtitles in result / finished.mp4 (bool)", default=True)
  
  args = parser.parse_args()
	
  cache = args.cache
  full = args.input
  lang = args.lang
  subtitles = args.subtitles

def checkdir(path):

  with yaspin(text="Checking '{}' exists".format(path)) as sp:
    if not os.path.exists(path):
      sp.text = "'{}' Doesn't exist, creating".format(path)
      os.mkdir(path)
    else:
      sp.text = "'{}' Exists".format(path)

    sp.ok(ansi.GREEN + "✓" + ansi.END)

def checklang(lang):

  checkdir('Data_TxtToSL/cache/{}/'.format(lang))
  checkdir('Data_TxtToSL/cache/{}/words/'.format(lang))

def loadphrases(lang):

  global phrases

  reallang = "english"
  if lang == "dgs":
    reallang = "german"
  
  if not os.path.isfile('Data_TxtToSL/phrases/{}.txt'.format(reallang)):
    with yaspin(text="Downloading 'Data_TxtToSL/phrases/{}.txt'".format(reallang)) as sp1:
      r = requests.get("https://oojmed.com/Data_TxtToSL/phrases/{}.txt".format(reallang))

      if r.status_code == 200:
        with open('Data_TxtToSL/phrases/{}.txt'.format(reallang), 'wb') as f:
          f.write(r.content)

        sp1.ok(ansi.GREEN + "✓" + ansi.END)
      else:
        sp1.fail(ansi.RED + "✗" + ansi.END)

  with yaspin(text="Loading phrases from 'Data_TxtToSL/phrases/{}.txt'".format(reallang)) as sp2:
    phrases = []

    with open('Data_TxtToSL/phrases/{}.txt'.format(reallang), 'r') as f:
      phrases = f.readlines()

    phrases = [phrase.strip() for phrase in phrases]

    sp2.ok(ansi.GREEN + "✓" + ansi.END)
  
  print()

  for phrase in phrases:
    print(phrase)

def loadautoskip(lang):
  '''
  Loads autoskip of lang (param) to autoskip (global)
  Depends on global variables: autoskip

  :param lang: Sign language to get autoskip for.
  :returns: Nothing.
  '''

  global autoskip

  reallang = "english"
  if lang == "dgs":
    reallang = "german"
  
  if not os.path.isfile('Data_TxtToSL/autoskip/{}.txt'.format(reallang)):
    with yaspin(text="Downloading 'Data_TxtToSL/autoskip/{}.txt'".format(reallang)) as sp1:
      r = requests.get("https://oojmed.com/Data_TxtToSL/autoskip/{}.txt".format(reallang))

      if r.status_code == 200:
        with open('Data_TxtToSL/autoskip/{}.txt'.format(reallang), 'wb') as f:
          f.write(r.content)

        sp1.ok(ansi.GREEN + "✓" + ansi.END)
      else:
        sp1.fail(ansi.RED + "✗" + ansi.END)
  
  with yaspin(text="Loading phrases from 'Data_TxtToSL/autoskip/{}.txt'".format(reallang)) as sp2:
    autoskip = []

    with open('Data_TxtToSL/autoskip/{}.txt'.format(reallang), 'r') as f:
      autoskip = f.readlines()

    autoskip = [word.strip() for word in autoskip]

    sp2.ok(ansi.GREEN + "✓" + ansi.END)
  
  print()

  for word in autoskip:
    print(word)

def nl_interpret(full):

  sents = nltk.sent_tokenize(full)

  result = []

  for sent in sents:
    print(sent)
    
    tokens = nltk.word_tokenize(sent)

    print(tokens)

    tagged = nltk.pos_tag(tokens)

    print(tagged)

    exceptions = [ "Are", "am" ]
    length = len(result)

    print(nltk.chunk.ne_chunk(tagged))

    for tag in tagged:
  
      print(tag)

      try:
        if tag[1][0:2] == "NN" and tag[0] not in exceptions: 
          result.insert(length, tag[0])
        
        if tag[1][0:2] == "VB":
          result.append(tag[0])
      
        if tag[1][0:2] == "PR" or tag[1][0:2] == "IN": 
          result.insert(length + 1, tag[0])
      except:
        print("Punctuation")
      
      if tag[0] == "?":
        result.append(result[length])
      
      print(result)

  return result

def interpret(full):

  global phrases, autoskip

  full = full.lower() 
  full = full.replace('.', '').replace(',', '').replace('?', '').replace('!', '')

  print(full)

  for phrase in phrases: 
    replacedPhrase = phrase.replace(" {}", "").replace(" []", "")
    full = full.replace(replacedPhrase, replacedPhrase.replace(' ', '({[SPACE]})'))

  words = full.split(" ")

  words = list(filter(None, words)) 

  print(words)

  words[:] = [word.replace('({[SPACE]})', ' ') for word in words] 

  print(words)

  for word in words:
    if word in autoskip:
      words.remove(word)

  print(words)

  index = 0
  for word in words:
    for phrase in phrases:
      if " {}" in phrase:
        if word == phrase.replace(" {}", ""):
          print(word)
          
          try: # Try incase there is no next word
            words[index + 1] = "{" + words[index + 1] + "}"
          except:
            print("Fail")
      elif " []" in phrase:
        if word == phrase.replace(" []", ""):
          print(word)

          try: # Try incase there is no next word
            words[index + 1] = "[" + words[index + 1] + "]"
          except:
            print("Fail")
    
    index += 1

  print(words)

  final = []

  for word in words: # Seperate letters in a word if it is surrounded by {}
    if word[0] == "{":
      if word[len(word) - 1] == "}":
        word = word.replace('{', '').replace('}', '')
        final.extend(list(word))
    else:
      final.append(word)
  
  print(final)

  return final

def main():

  global lang, full, cache, subtitles

  getargs()

  checkdir('Data_TxtToSL/')
  
  checkdir('Data_TxtToSL/phrases/')
  checkdir('Data_TxtToSL/autoskip/')

  checkdir('Data_TxtToSL/cache/')

  print()

  if lang == None:
    while True:
      print("Select Sign Language:\n1) BSL (British Sign Language)\n ")
      innum = input("Number: ")

      if innum == "1":
        lang = "BSL"
        break
      else:
          print("ERROR")

  print()

  checklang(lang.lower())

  print()

  loadautoskip(lang.lower())

  print()

  loadphrases(lang.lower())

  print()

  if full == None:
    full = input("\nInput: ")

  words = interpret(full)

  print(words)

  for word in copy.deepcopy(words):
    if lang == "BSL":
      content = signorg_getvid(word)
    
    if content != "cache" and content is not False and not isinstance(content, list):
      savevid(content, word)
    elif isinstance(content, list):
      index = words.index(word)

      words.remove(word)

      words[index:index] = content
    elif content is False: # Skip word
      words.remove(word)

    print()     

  print(words)
  print()

  clips = []

  for word in words:
    replaced = word.replace('[', '').replace(']', '')

    if not os.path.isfile("Data_TxtToSL/cache/{}/words/{}.mp4".format(lang.lower(), replaced.replace(' ', '-'))):
      continue

    originalClip = VideoFileClip("Data_TxtToSL/cache/{}/words/{}.mp4".format(lang.lower(), replaced.replace(' ', '-')))

    if subtitles:
      with yaspin(text="Generating subtitles for '{}'".format(word)) as sp:
        txt = TextClip(replaced, font='Arial',
	        color='white',fontsize=24)

        txt_col = txt.on_color(size=(originalClip.w, txt.h + 30),
          color=(0,0,0), pos=('center' ,'center'), col_opacity=0.2)

        txt_mov = txt_col.set_pos(('center', 0.7), relative=True)

        composite = CompositeVideoClip([originalClip, txt_mov])
        composite.duration = originalClip.duration

        clips.append(composite)

        sp.ok(ansi.GREEN + "✓" + ansi.END)
    else:
      clips.append(originalClip)

  print()
  print(clips)
  print()

  final = concatenate_videoclips(clips, method="compose")

  final.write_videofile("finished.mp4", fps=60, audio=False, threads=4)

  class Video(object):
    def __init__(self,path):
        self.path = path

    def play(self):
        from os import startfile
        startfile(self.path)

  class Movie_MP4(Video):
    type = "MP4"

  movie = Movie_MP4(r"C:\Users\Ankita\Desktop\pbl 4\TxtToSL-master\finished.mp4")

  movie.play()

  if not cache:
    with yaspin(text="Deleting video files (because caching is disabled)") as sp2: # Use pymovie to combine video files
      for word in words:
        os.remove("cache/{}/words/{}.mp4".format(lang.lower(), word.replace(' ', '-')))

      sp2.ok(ansi.GREEN + "✓" + ansi.END)

if __name__ == "__main__":
  main()