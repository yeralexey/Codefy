# Template for Telegram bot.

Mostly for personal use. New plugins and utils may be added in the future. When I use
it, I simply replace redundant ones.

Current issue can be always checked at http://t.me/PyrogramTemplateBot, if my server is fine 🤭.
Not sure, that everything is well-structured and easy to get, I am working on it.


## I. What can this bot do.

- adds new user and all his data to sqlite key-value database;
- checks user in database for certain attributes, like language, fsm step, etc.;
- interviews user for personal data, for registration or contract;
- sends all data collected to google sheets;
- contains admin panel for mailing, restarting, etc.


## II. Used libs.

- Pyrogram     https://github.com/pyrogram/pyrogram            , as main library;
- Plate        https://github.com/delivrance/plate             , for language switch;
- Pyromod      https://github.com/usernein/pyromod             , for dialogue mastering;
- Sqlitedict   https://github.com/RaRe-Technologies/sqlitedict , for sqlite managing;
- Cryptography https://github.com/pyca/cryptography            , encrypt secrets;

and others, of course, including dependencies, so my gratefulness to all authors,
developers, for their will to make the world a better place to live.


## III. Bot folders and files.

- `/entities`    - "communication-related" classes are kept, User and Interview for now;
- `/locales`     - .jsons with bot answer texts, according to [Plate](https://github.com/delivrance/plate) library;
- `/maillogs`    - logs after messaging bot subscribers;
- `/maindata`    - config, session files, database;
- `/plugins`     - handlers, according to Pyrogram's 
[Smart Plugins](https://docs.pyrogram.org/topics/smart-plugins#smart-plugins), Interview instances;
- `/utils`       - workers for database, validation, google sheets, etc.;
- `main.py`      - main start file;
- `requirements.txt`
- `MANIFEST.in`
- `README.md`
- `LICENCE`

Imports are made to main.py, and imported to plugins with `from main impot *`, it
may not be a good decision, but works fine for me.


## IV.  How to set up.

That's what I do, actually.

1. Clone repository.
2. `git remote remove origin`.
3. Install requirements.
4. If needed, create google sheet and configure api:  
   - service account with drive and sheet apis;
   - sheet, with access permission to service account;
   - credentials, rename, replace template in `/maindata`.
5. Run `main.py`, __input__ `owner telegram id`(to configure admin), `api_id`, `api_hash` according to
[pyrogram docs](https://docs.pyrogram.org/start/auth), `bot token` and `googlesheet id`. All session files are created.
6. Rollback `googlecredentials.json` to template one, so **absolutely no secret data is kept in code**.
7. Remove all unnecessary utils and plugins. Add them back by need.

Credentials stored encrypted with cryptography module.  Please note, provided code does not perform confidentiality of 
personal and app data, if published by mistake. But it could be achieved, if minor changes in `loader.py` were made.

## V. About admin panel.

To get access to admin panel - admin id is to be specified in admins list, so it can not
be checked in http://t.me/PyrogramTemplateBot.

Simply run `/admin` to get menu and `/commands` to get commands list.
Commands `/kill`, `/restart`, `/reboot` are tested in UBUNTU 20.04 only, correct path with `which` Linux command".


## VI. Bot menu.

I am pretty sure that you can see it in [bot itself](http://t.me/PyrogramTemplateBot) by yourself, but it is so cool to
copypaste it from here to Botfather, if changes needed 🤓.

  * `start - main menu`
  * `help - how to use`
  * `mydata - check your data`
  * `language - choose language`
  * `cancel - stop current process`

## VII. Set up on server.

I do love to push projects with git, using Pycharm, without doing any extra-movements, like "filezilling", "sshing",
so here comes recipe for those, who didn't know how to, and a crib for myself. 

- to initiate auto update code on server the sequence is (Ubuntu 20.04 tested):
  * `mkdir <YOUR_PROJECT_NAME>`
  * `cd <YOUR_PROJECT_NAME>`
  * `mkdir .git`
  * `cd .git`
  * `git init --bare`
  * `nano hooks/post-receive`
  * in post-receive: 
    ```commandline
    git --work-tree=/home/<YOUR_PROJECT_NAME> \
      --git-dir=/home/<YOUR_PROJECT_NAME>.git checkout -f

  * `chmod +x post-receive`
- sequence to create systemd daemon (Ubuntu 20.04 tested):
  * `nano /etc/systemd/system/<YOUR_PROJECT_NAME>.service`
  * in <YOUR_PROJECT_NAME>.service: 
    ```commandline
    [Unit]
    Description=<YOUR_PROJECT_NAME>
    After=network.target
    
    [Service]
    Type=simple
    User=root
    WorkingDirectory=/home/<YOUR_PROJECT_NAME>
    VIRTUAL_ENV=/home/<YOUR_PROJECT_NAME>/venv
    Environment=PATH=$VIRTUAL_ENV/bin:$PATH
    ExecStart=/home/<YOUR_PROJECT_NAME>/venv/bin/python /home/<YOUR_PROJECT_NAME>/main.py
    Restart=on-failure
    
    [Install]
    WantedBy=multi-user.target
  * `systemctl enable <YOUR_PROJECT_NAME>`
  * `systemctl start <YOUR_PROJECT_NAME>`

  
## Notes.

##### About sqlite and sqlitedict.

I use key-value database, so sqlitedict can  be changed to redis by changing database.py to some redis worker with 
minor work done.

##### Input data validation.

All methods for inputed by user data validation are in `/utils/validation.py`. 
[email_validator](https://github.com/JoshData/python-email-validator) and 
[phonenumbers](https://github.com/daviddrysdale/python-phonenumbers) are used.

##### About memory.

Dictionary in `class User`, `/entities/userdata.py` in is not being emptied, only when bot is restarted. So be aware
of it, it is not suitable for huge auditory. I will update it someday. Last user's action timestamp is saved to database,
so if implement this feature - it should be based on excluding most long time ago users, I guess.


### Best regards to all you people, thanks for any useful hint, advice and healthy criticism.

License
MIT © 2023 [yeralexey](https://github.com/yeralexey)
