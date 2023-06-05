import os
import shutil
from time import time as t

def clear(directory, ask=True, log=True):
   if ask:
      inp = input('Please confirm you want to clear the data (y/n): ').lower()
      while inp not in {'y', 'n'}:
         inp = input('Please confirm you want to clear the data (y/n): ').lower()
      if inp == 'y':
         delete_everything(directory, log)
      else:
         if log:
            print('Keeping all the data. Continuing...')
   else:
      delete_everything(directory, log)

def delete_everything(directory, log):
   st = t()
   if log:
      print('\nClearing...')

   total_files_deleted = 0
   total_dirs_deleted = 0

   try:
      for root, dirs, files in os.walk(directory, topdown=False):
         for name in files:
            file_path = os.path.join(root, name)
            os.remove(file_path)
            total_files_deleted += 1
         for name in dirs:
            dir_path = os.path.join(root, name)
            os.rmdir(dir_path)
            total_dirs_deleted += 1

      shutil.rmtree('posts')
      if log:
         print('Success')

         print(f'{total_files_deleted} files and {total_dirs_deleted} directories have been deleted')

   except:
      if log:
         print('\nUnsuccessful')

   finally:
      et = t()
      if log:
         print(f'Time taken: {round(et-st, 2)} seconds\n')

if __name__ == '__main__':
   clear()