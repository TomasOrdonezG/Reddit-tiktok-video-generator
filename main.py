import praw, re, json, os, random, datetime
from clear import clear
from time import time as t
from gtts import gTTS
from pyperclip import copy
from moviepy.editor import *
from moviepy.audio.fx.all import audio_fadeout, audio_fadein
from pydub import AudioSegment
from pydub.effects import speedup

# ! DATE
current_date = datetime.date.today()
date = current_date.strftime('%Y_%m_%d')

class Post:
   # ! CONSTANTS
   AUDIO_FOLDER = 'audio'
   VIDEO_OUTPUT_FOLDER = 'videos/' + date
   HISTORY = 'history.txt'

   def __init__(self, title: str, text: str, post_id: str) -> None:
      # ! Create the date folder if it doesn't exist
      if not os.path.exists(Post.VIDEO_OUTPUT_FOLDER):
         os.makedirs(Post.VIDEO_OUTPUT_FOLDER)
      
      text = re.split(r'\.|\n', text)
      text = [title]+[sentence for sentence in text if sentence.strip() != '']
      self.title = title
      self.id = post_id
      self.text_original = self.cut_text(text)
      self.text_clean = self.profanity_filter(text)
      self.audio_exists = False
      self.__audio_paths = []
   
   def cut_text(self, text: list) -> list:
      result = []
      for sentence in text:
         words = sentence.split()
         lines = []
         line = ""
         for word in words:
            if len(line) + len(word) < 30:
               line += word + " "
            else:
               lines.append(line.strip())
               line = word + " "
         lines.append(line.strip())
         result.append("\n".join(lines))
      return result
   
   def create(self):
      self.create_audio()
      self.create_video()
      
      # Cache to the history
      with open(Post.HISTORY, 'a') as f:
         f.write(str(self.id) + '\n')
   
   def profanity_filter(self, text: list) -> str:
      '''Filters bad words so the algorithm doesn't get mad at me'''
      output_text = []
      for sentence in text:
         word_list = sentence.split(' ')
         for word_i in range(len(word_list)):
            # Read from file
            with open('profanity_filter.txt', 'r', encoding='utf-8') as f:
               lol = f.readlines()
               for i in range(len(lol)):
                  lol[i] = lol[i].strip().split(';')
            
            # Filter
            for word_pair in lol:
               if word_list[word_i].lower() == word_pair[0]:
                  word_list[word_i] = word_pair[1]
               elif word_list[word_i][:-1].lower() == word_pair[0]:
                  word_list[word_i] = word_pair[1] + word_list[word_i][-1]
         output_sentence = ' '.join(word_list)
         output_text.append(output_sentence)
      return output_text
   
   def get_audio_paths(self) -> list:
      '''returns mp3 file paths for the post'''
      assert self.audio_exists, 'Error: Audio does not exist'
      return self.__audio_paths
   
   def add_audio_path(self, path) -> None:
      self.__audio_paths.append(path)

   def speed_up_audio(self, filename):
      '''Speeds up the audio'''
      audio = AudioSegment.from_mp3(filename)
      new_file = speedup(audio,1.5,50)
      new_file.export(filename, format="mp3")

   def create_audio(self):
      assert not self.audio_exists, 'Error creating audio: Audio already exists'
      
      print('\n    Creating audio...')
      
      for i in range(len(self.text_clean)):
         speech = gTTS(text=self.text_clean[i], lang='en', slow=False, tld='com')
         output = Post.AUDIO_FOLDER + '/' + f'{i}.mp3'
         speech.save(output)
         self.add_audio_path(output)
         
         # Speed up the audio
         self.speed_up_audio(output)
      self.audio_exists = True
      print('\n    Audio created\n')
      
   def create_video(self):
      speed = 1.5
      speedup = False
      
      # Get video
      folder = 'footage'
      file_paths = [os.path.join(folder, f) for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))]
      video_path = random.choice(file_paths)
      video = VideoFileClip(video_path)
      
      # speed up ss gameplay
      if 'ss' in video_path:
         video = video.speedx(1.5)

      # Audio files list
      audio_clips = []
      for audio_path in self.get_audio_paths():
         audio_clip = AudioFileClip(audio_path)
         if speedup:
            audio_clip = audio_clip.fx(vfx.speedx, factor=speed)
         audio_clips.append(audio_clip)
      final_audio_clip = concatenate_audioclips(audio_clips)
            
      # Create text
      text_clips = []
      start_time = 0
      for i, text in enumerate(self.text_original):
         text_clip = TextClip(text, fontsize=70, color='white')
         text_clip = text_clip.set_position('center').set_duration(audio_clips[i].duration)
         text_clip = text_clip.set_start(start_time)
         text_clip = text_clip.resize(width=video.w * 0.8) # Scale text to fit within 80% of video width
         text_clips.append(text_clip)
         start_time += audio_clips[i].duration

      video_with_text = CompositeVideoClip([video, *text_clips])

      final_duration = final_audio_clip.duration
      video_duration = video_with_text.duration
      if video_duration > final_duration:
         video_with_text = video_with_text.subclip(0, final_duration)
      else:
         final_audio_clip = final_audio_clip.subclip(0, video_duration)

      video_with_text = video_with_text.set_audio(final_audio_clip)
      video_with_text.write_videofile(f"{Post.VIDEO_OUTPUT_FOLDER}/{self.title}.mp4")
      
      # Clear audio after use
      clear(Post.AUDIO_FOLDER, ask=False, log=False)

class Subreddit:
   def __init__(self, name) -> None:
      self.name = name
      self.posts = []
      self.size = 0
   
   def add_post(self, post: Post) -> None:
      self.posts.append(post)
      self.size += 1
   
   def get_size(self) -> int:
      return self.size

with open(Post.HISTORY, 'r') as f:
   post_id_list = f.readlines()
   for i in range(len(post_id_list)):
      post_id_list[i] = post_id_list[i].strip()

def create_data(subreddit_names: list, number_of_posts_per_subreddit: int, sort='hot') -> list[Subreddit]:
   user_agent = "XXX"

   # Create an instance of reddit class
   reddit = praw.Reddit(client_id="XXX",client_secret="XXX",user_agent=user_agent)
   
   # Initialize a list of subreddit objects
   subreddits = []
   
   # Loop through each subreddit
   for subreddit_name_i in range(len(subreddit_names)):
      subreddit_name = subreddit_names[subreddit_name_i]
      
      # Gets subreddit
      subreddit = reddit.subreddit(subreddit_name)

      subreddits.append(Subreddit(subreddit_name))

      # Extracts data
      max_length = 1200
      min_length = 500
      print('\n    Gathering data from r/%s...' % (subreddit_name))
      
      # ! sort by
      if sort.lower() == 'hot':
         posts = subreddit.hot(limit=None)
      elif sort == 'top':
         posts = subreddit.top(time_filter='month', limit=None)
      
      
      for submission in posts:
         if subreddits[subreddit_name_i].get_size() >= number_of_posts_per_subreddit:
            break
         else:
            if len(submission.selftext) >= min_length and len(submission.selftext) <= max_length and not submission.stickied:
               post_id = submission.id
               # Check if the video has been made before
               if post_id not in post_id_list:
                  title = submission.title
                  text = submission.selftext
                  subreddits[subreddit_name_i].add_post(Post(title, text, post_id))
               else:
                  print('Video ' + str(post_id) + ' already created. Skipping...')

   print('\n    Data collected')
   return subreddits

def create_videos(subreddits):
   # Loop through each post
   for sub in subreddits:
      for post in sub.posts:
         # ! Create
         try:
            post.create()
         except Exception as e:
            print(e.args[0])

def main() -> None:
   # Clear audio
   clear(Post.AUDIO_FOLDER, ask=False, log=False)
   
   # * Modifiable Variables
   subreddit_names = ["TrueOffMyChest", "tifu"]
   number_of_posts_per_subreddit = 1
   
   # ! gets data
   subreddits = create_data(subreddit_names, number_of_posts_per_subreddit)
   create_videos(subreddits)

if __name__ == '__main__':
   main()
