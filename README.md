###### WARNING! README.md modifications.

I collect here non systemized in description modifications to project. If you see notes after this text, 
please consider noted done in code, but still not described in README.md properly. Check commits if needed.

- credentials became encrypted, and data is not kept anywhere except it. Data is inputted on new project 
started. Please note, it does not perform confidentiality of personal and app data, if published by mistake. But it
could be achieved, if minor changes in `loader.py` are made.
- to initiate auto update code on server the sequence is:
  * `git init --bare`
  * `nano hooks/post-receive`
  * in post-receive: `git --work-tree=/home/PyrogramTemplateBot \
--git-dir=/home/PyrogramTemplateBot/.git checkout -f` 
  * `chmod +x post-receive`
  

# Template for Telegram bot.


Mostly for personal use. New plugins and utils may be added in the future. When I use
it, I simply replace redundant ones.

Current issue can be always checked at http://t.me/PyrogramTemplateBot, if my server is fine 😄
Not sure, that everything is well-structured and easy to get, I am working on it.


## I. What can this bot do.

- adds new user to sqlite key-value database;
- checks user in database for certain attributes, like language;
- interviews user for personal data, for registration or contract;
- sends all data collected to google sheets;
- contains admin panel for mailing, restarting, etc.


## II. Used libs.

- Pyrogram    https://github.com/pyrogram/pyrogram            , as main library;
- Plate       https://github.com/delivrance/plate             , for language switch;
- Pyromod     https://github.com/usernein/pyromod             , for dialogue mastering;
- Sqlitedict  https://github.com/RaRe-Technologies/sqlitedict , for sqlite managing;

and others, of course, including dependencies, so my gratefulness to all authors,
developers, for their will to make the world a better place to live.


## III. Bot folders and files.

- `/entities`    - classes are kept, User and Interview;
- `/locales`     - .jsons with bot answer texts, according to [Plate](https://github.com/delivrance/plate) library;
- `/maillogs`    - logs after messaging bot subscribers;
- `/maindata`    - config, session files, database;
- `/plugins`     - handlers, according to Pyrogram's 
[Smart Plugins](https://docs.pyrogram.org/topics/smart-plugins#smart-plugins);
- `/utils`       - workers for database, validation, google sheets, etc.;
- `activator.py` - session maker, can be removed after session is creates;
- `main.py`      - main start file;
- `requirements.txt`
- `MANIFEST.in`
- `README.md`
- `LICENCE`

All imports are made to main.py, and imported to plugins with `from main impot *`, it
may not be a good decision, but works fine for me.


## IV.  How to set up.

That's what I do, actually.

1. Clone repository.
2. `git remote remove origin`.
3. Install requirements.
4. If needed, create google sheet and configure api:  
   - service account with drive and sheet apis;
   - sheet, with access permission to service account;
   - credentials, rename, place to `/maindata`.
5. Fill `/maindata/config.py`, so `<PASTE_YOUR_DATA_HERE>` is replaced.
6. Fill `api_id`, `api_hash` according to [pyrogram docs](https://docs.pyrogram.org/start/auth) in `activator.py`, 
run it, it will do its job and stop.
7. Run `main.py`

From now session file in `/maindata/` is created, and `activator.py` can be removed.
After running `main.py` (with venv enabled, of course) app will create `main.db` - database
file. `main.csv` file - is last one, that was sent to admin by bot, is overwritten
all the time. `.log` file with project name will appear in main project folder.


## V. About admin panel.

To get access to admin panel - admin id is to be specified in admins list, so it can not
be checked in http://t.me/PyrogramTemplateBot.

Simply run `/admin` to get menu and `/commands` to get commands list.
Commands `/kill`, `/restart`, `/reboot` are tested in UBUNTU 18.04 only.


## VI. Notes.

##### About sqlite and sqlitedict.

I use key-value database, so sqlitedict can  be changed to redis by changing
database.py to some redis worker with minor work done.

##### Input data validation.

All methods for data being input by user are in `/utils/validation.py`. 
[email_validator](https://github.com/JoshData/python-email-validator) and 
[phonenumbers](https://github.com/daviddrysdale/python-phonenumbers) are used.

##### About memory.

Dictionary in `class User`, `/entities/userdata.py` in is not being emptied, only when bot is restarted. So be aware
of it, it is not suitable for huge auditory. I will update it someday. Last user's action timestamp is saved to database,
so if implement this feature - it should be based on excluding most long time ago users, I guess.

##### For [@usernain](https://github.com/usernein).

Cezar, implementation you were interested - in `plugins/registration.py`. In works with class Interview,
so any other question or data request is simply defined as class attribute, without
messing up with code. Your new listener is in line 92. Code is not final, I keep
playing with it.

### Best regards to all you people, thanks for any useful hint, advice and healthy criticism.

License
MIT © 2023 [yeralexey](https://github.com/yeralexey)
