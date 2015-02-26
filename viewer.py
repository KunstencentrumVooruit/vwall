#!/usr/bin/env python
# -*- coding: utf8 -*-

__author__ = "Viktor Petersson"
__copyright__ = "Copyright 2012-2014, WireLoad Inc"
__license__ = "Dual License: GPLv2 and Commercial License"

from datetime import datetime, timedelta
from os import path, getenv, utime
from platform import machine
from random import shuffle
from requests import get as req_get
from requests import head as req_head
from time import sleep, time
from json import load as json_load
from signal import signal, SIGUSR1, SIGUSR2
import subprocess
import logging
import sh

from settings import settings
import html_templates
from utils import url_fails
import db
import assets_helper


SPLASH_DELAY = 60  # secs
EMPTY_PL_DELAY = 5  # secs


WATCHDOG_PATH = '/tmp/screenly.watchdog'
SCREENLY_HTML = '/tmp/screenly_html/'


current_browser_url = None
browser = None

VIDEO_TIMEOUT = 20  # secs



def sigusr1(signum, frame):
    """
    The signal interrupts sleep() calls, so the currently playing web or image asset is skipped.
    omxplayer is killed to skip any currently playing video assets.
    """
    logging.info('USR1 received, skipping.')
    sh.killall('avconv', _ok_code=[1])


def sigusr2(signum, frame):
    """Reload settings"""
    logging.info("USR2 received, reloading settings.")
    load_settings()


class Scheduler(object):
    def __init__(self, *args, **kwargs):
        logging.debug('Scheduler init')
        self.update_playlist()

    def get_next_asset(self):
        logging.debug('get_next_asset')
        self.refresh_playlist()
        logging.debug('get_next_asset after refresh')
        if self.nassets == 0:
            return None
        idx = self.index
        self.index = (self.index + 1) % self.nassets
        logging.debug('get_next_asset counter %s returning asset %s of %s', self.counter, idx + 1, self.nassets)
        if settings['shuffle_playlist'] and self.index == 0:
            self.counter += 1
        return self.assets[idx]

    def refresh_playlist(self):
        logging.debug('refresh_playlist')
        time_cur = datetime.utcnow()
        logging.debug('refresh: counter: (%s) deadline (%s) timecur (%s)', self.counter, self.deadline, time_cur)
        if self.get_db_mtime() > self.last_update_db_mtime:
            logging.debug('updating playlist due to database modification')
            self.update_playlist()
        elif settings['shuffle_playlist'] and self.counter >= 5:
            self.update_playlist()
        elif self.deadline and self.deadline <= time_cur:
            self.update_playlist()

    def update_playlist(self):
        logging.debug('update_playlist')
        self.last_update_db_mtime = self.get_db_mtime()
        (self.assets, self.deadline) = generate_asset_list()
        self.nassets = len(self.assets)
        self.counter = 0
        self.index = 0
        logging.debug('update_playlist done, count %s, counter %s, index %s, deadline %s', self.nassets, self.counter, self.index, self.deadline)

    def get_db_mtime(self):
        # get database file last modification time
        try:
            return path.getmtime(settings['database'])
        except:
            return 0


def generate_asset_list():
    logging.info('Generating asset-list...')

    now = datetime.utcnow()
    enabled_assets = [a for a in assets_helper.read(db_conn) if a['is_enabled']]
    future_dates = [a[k] for a in enabled_assets for k in ['start_date', 'end_date'] if a[k] > now]
    deadline = sorted(future_dates)[0] if future_dates else None
    logging.debug('generate_asset_list deadline: %s', deadline)

    playlist = assets_helper.get_playlist(db_conn)
    if settings['shuffle_playlist']:
        shuffle(playlist)
    return (playlist, deadline)


def watchdog():
    """Notify the watchdog file to be used with the watchdog-device."""
    if not path.isfile(WATCHDOG_PATH):
        open(WATCHDOG_PATH, 'w').close()
    else:
        utime(WATCHDOG_PATH, None)


def view_video(uri, duration):
    logging.debug('Displaying video %s for %s ', uri, duration)
    subprocess.call(['sudo', 'pkill', '-USR1', '-f', 'python /home/pi/vwall/gpio_master.py']) # call gpio.py to set pin HIGH
    sleep(2) # geef slaves de kans om pwomx te starten
    p = subprocess.Popen(['avconv', '-re', '-i', uri, '-vcodec', 'copy', '-f', 'avi', '-an', 'udp://239.0.1.23:1234'])
    #p  = subprocess.Popen(['/home/pi/udpserver3.sh'])
    p.wait() # wacht tot subprocess gestopt is
    logging.debug ("----> PWOMXPLAYER DONE!")
    subprocess.call(['sudo', 'pkill', '-USR2', '-f', 'python /home/pi/vwall/gpio_master.py']) # call gpio.py to set pin LOW
    logging.debug ("Sleeping for %s seconds", duration)
    sleep(int(duration))
    

def check_update():
    """
    Check if there is a later version of Screenly-OSE
    available. Only do this update once per day.

    Return True if up to date was written to disk,
    False if no update needed and None if unable to check.
    """

    sha_file = path.join(settings.get_configdir(), 'latest_screenly_sha')

    if path.isfile(sha_file):
        sha_file_mtime = path.getmtime(sha_file)
        last_update = datetime.fromtimestamp(sha_file_mtime)
    else:
        last_update = None

    logging.debug('Last update: %s' % str(last_update))

    if last_update is None or last_update < (datetime.now() - timedelta(days=1)):

        if not url_fails('http://stats.screenlyapp.com'):
            latest_sha = req_get('http://stats.screenlyapp.com/latest')

            if latest_sha.status_code == 200:
                with open(sha_file, 'w') as f:
                    f.write(latest_sha.content.strip())
                return True
            else:
                logging.debug('Received non 200-status')
                return
        else:
            logging.debug('Unable to retreive latest SHA')
            return
    else:
        return False


def load_settings():
    """Load settings and set the log level."""
    settings.load()
    logging.getLogger().setLevel(logging.DEBUG if settings['debug_logging'] else logging.DEBUG)


def asset_loop(scheduler):
    check_update()
    asset = scheduler.get_next_asset()

    if asset is None:
        logging.info('Playlist is empty. Sleeping for %s seconds', EMPTY_PL_DELAY)
        
        sleep(EMPTY_PL_DELAY)

    elif path.isfile(asset['uri']) or not url_fails(asset['uri']):
        name, mime, uri = asset['name'], asset['mimetype'], asset['uri']
        logging.info('Showing asset %s (%s)', name, mime)
        logging.debug('Asset URI %s', uri)
        watchdog()

        if 'video' in mime:
            view_video(uri, asset['duration'])
        else:
            logging.error('Unknown MimeType %s', mime)

        
    else:
        logging.info('Asset %s at %s is not available, skipping.', asset['name'], asset['uri'])
        sleep(0.5)


def setup():
    global arch, db_conn
    arch = machine()

    signal(SIGUSR1, sigusr1)
    signal(SIGUSR2, sigusr2)

    load_settings()
    db_conn = db.conn(settings['database'])

def main():
    setup()
      
    scheduler = Scheduler()
    logging.debug('Entering infinite loop.')
    while True:
        asset_loop(scheduler)

if __name__ == "__main__":
    main()






		
		
