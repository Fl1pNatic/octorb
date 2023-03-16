# How to host Octorb
Whether you're hosting Octorb to test contributions or simply use, most of the steps are the same.

## Basic Setup
First, you'll need to download the code. If you're wanting to contribute, you should do this by cloning a fork of the repository. If you just want to host octorb, you should clone the base repository so that updates can be done through Octorb's internal update command.

Next, you should make sure you have python3.10 or higher installed, along with pip (or another python package manager). Lower versions may work but are not officially supported.

If you're using pip you can install all of Octorb's python dependencies with `pip install -r requirements.txt`, run in the base directory. If not, please check this file to see what versions are required and install them.

Next, you'll probably want to give yourself full permissions on your Octorb instance. To do this, simply replace the contents of the developer_ids array in `PermissionsChecks.py` with your user id, and any others who are working/running the bot with you.

In `commands/dynamic.py`, you should change the gallery_id variable for devmode or not devmode to the id of the channel you want Octorb to store the gallery media in.

Finally, you need to create a file named `.env` in the base folder. This file should contain your discord bot token, in the format of `TOKEN="TOKEN HERE"`. If you're doing development, you may want to add `DEVMODE=1` on another line.

## Running
Once you have your bot setup, all you need to do is run `python main.py`. For production instances you may want to use something external like pm2 for remote log viewing and automatic restarts in case of crashes.
