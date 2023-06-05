Before anything, go read the README.md files in each of the folders 'audio', 'footage' and 'videos', they're not a long read but they are important

To run this program:

get access to the reddit API by adding your credentials, it is very easy but reddit apps might be down due to recent events: [how to get credentials for the reddit API](https://www.jcchouinard.com/reddit-api/)

replace the 'XXX' with your credentials on line 179 and 182 inside the create_data function in main.py to get access

INSIDE main.py
- Modify subreddit_names on line 240 to change the subreddits you want to pull data from
- modify number_of_posts_per_subreddit to change the amount of posts from each subreddit
- Run main.js and you generated videos should appear in videos' subfolder's with today's date

sorry for the program not being very user friendly but I never planned on sharing this project and so I never made an interface

### About other things:
- it grabs the posts by popularity and it will not generate videos with very long text because you do not want 10min long videos and some reddit posts are very very long
- clear.py clears a directory of all its contents, inside main.py, it will not clear anything other than 'audio', you can check main.py if you don't trust me
- history.txt contains all the post ids from all the posts already generated so you don't create duplicates
- profanity_filter.txt is used to make the videos more family friendly, though it is very incomplete
- this was a dumb personal project, do not take it very seriously
