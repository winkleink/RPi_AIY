# Copyright 2017 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Carry out voice commands by recognising keywords."""

import datetime
import logging
import subprocess

import RPi.GPIO as gpio
import time

import urllib.request
import feedparser

import actionbase

gpio.setmode(gpio.BCM)
gpio.setup(23, gpio.IN)


# =============================================================================
#
# Hey, Makers!
#
# This file contains some examples of voice commands that are handled locally,
# right on your Raspberry Pi.
#
# Do you want to add a new voice command? Check out the instructions at:
# https://aiyprojects.withgoogle.com/voice/#makers-guide-3-3--create-a-new-voice-command-or-action
# (MagPi readers - watch out! You should switch to the instructions in the link
#  above, since there's a mistake in the MagPi instructions.)
#
# In order to make a new voice command, you need to do two things. First, make a
# new action where it says:
#   "Implement your own actions here"
# Secondly, add your new voice command to the actor near the bottom of the file,
# where it says:
#   "Add your own voice commands here"
#
# =============================================================================

# Actions might not use the user's command. pylint: disable=unused-argument


# Example: Say a simple response
# ================================
#
# This example will respond to the user by saying something. You choose what it
# says when you add the command below - look for SpeakAction at the bottom of
# the file.
#
# There are two functions:
# __init__ is called when the voice commands are configured, and stores
# information about how the action should work:
#   - self.say is a function that says some text aloud.
#   - self.words are the words to use as the response.
# run is called when the voice command is used. It gets the user's exact voice
# command as a parameter.

class SpeakAction(object):

    """Says the given text via TTS."""

    def __init__(self, say, words):
        self.say = say
        self.words = words

    def run(self, voice_command):
        self.say(self.words)


# Example: Tell the current time
# ==============================
#
# This example will tell the time aloud. The to_str function will turn the time
# into helpful text (for example, "It is twenty past four."). The run function
# uses to_str say it aloud.

class SpeakTime(object):

    """Says the current local time with TTS."""

    def __init__(self, say):
        self.say = say

    def run(self, voice_command):
        time_str = self.to_str(datetime.datetime.now())
        self.say(time_str)

    def to_str(self, dt):
        """Convert a datetime to a human-readable string."""
        HRS_TEXT = ['midnight', 'one', 'two', 'three', 'four', 'five', 'six',
                    'seven', 'eight', 'nine', 'ten', 'eleven', 'twelve']
        MINS_TEXT = ["five", "ten", "quarter", "twenty", "twenty-five", "half"]
        hour = dt.hour
        minute = dt.minute

        # convert to units of five minutes to the nearest hour
        minute_rounded = (minute + 2) // 5
        minute_is_inverted = minute_rounded > 6
        if minute_is_inverted:
            minute_rounded = 12 - minute_rounded
            hour = (hour + 1) % 24

        # convert time from 24-hour to 12-hour
        if hour > 12:
            hour -= 12

        if minute_rounded == 0:
            if hour == 0:
                return 'It is midnight.'
            return "It is %s o'clock." % HRS_TEXT[hour]

        if minute_is_inverted:
            return 'It is %s to %s.' % (MINS_TEXT[minute_rounded - 1], HRS_TEXT[hour])
        return 'It is %s past %s.' % (MINS_TEXT[minute_rounded - 1], HRS_TEXT[hour])


# Example: Run a shell command and say its output
# ===============================================
#
# This example will use a shell command to work out what to say. You choose the
# shell command when you add the voice command below - look for the example
# below where it says the IP address of the Raspberry Pi.

class SpeakShellCommandOutput(object):

    """Speaks out the output of a shell command."""

    def __init__(self, say, shell_command, failure_text):
        self.say = say
        self.shell_command = shell_command
        self.failure_text = failure_text

    def run(self, voice_command):
        output = subprocess.check_output(self.shell_command, shell=True).strip()
        if output:
            self.say(output)
        elif self.failure_text:
            self.say(self.failure_text)


# Example: Change the volume
# ==========================
#
# This example will can change the speaker volume of the Raspberry Pi. It uses
# the shell command SET_VOLUME to change the volume, and then GET_VOLUME gets
# the new volume. The example says the new volume aloud after changing the
# volume.

class VolumeControl(object):

    """Changes the volume and says the new level."""

    GET_VOLUME = r'amixer get Master | grep "Front Left:" | sed "s/.*\[\([0-9]\+\)%\].*/\1/"'
    SET_VOLUME = 'amixer -q set Master %d%%'

    def __init__(self, say, change):
        self.say = say
        self.change = change

    def run(self, voice_command):
        res = subprocess.check_output(VolumeControl.GET_VOLUME, shell=True).strip()
        try:
            logging.info("volume: %s", res)
            vol = int(res) + self.change
            vol = max(0, min(100, vol))
            subprocess.call(VolumeControl.SET_VOLUME % vol, shell=True)
            self.say(_('Volume at %d %%.') % vol)
        except (ValueError, subprocess.CalledProcessError):
            logging.exception("Error using amixer to adjust volume.")


# Example: Repeat after me
# ========================
#
# This example will repeat what the user said. It shows how you can access what
# the user said, and change what you do or how you respond.

class RepeatAfterMe(object):

    """Repeats the user's command."""

    def __init__(self, say, keyword):
        self.say = say
        self.keyword = keyword

    def run(self, voice_command):
        # The command still has the 'repeat after me' keyword, so we need to
        # remove it before saying whatever is left.
        to_repeat = voice_command.replace(self.keyword, '', 1)
        self.say(to_repeat)

# =========================================
# Makers! Implement your own actions here.
# =========================================

# play streaming radio stations
# commands are  "radio absolute radio" or "radio bbc radio 2"

# Use the following command on the command line to see what the keyword is that's be interpreted.
# I expected "BBC Radio 2" to have to be "B B C Radio Two", but Google interpreted it correctly.

# sudo journalctl -u voice-recognizer -n 20 -f 

# currently plays
# Absolute Radio
# Absolute 80s
# Absolute 90s
# Absolute 00s

# Eagle Radio

# BBC Radio 1
# BBC Radio 2
# BBC Radio 3
# BBC Radio 4

# Capital FM 

# list of streaming URL for the UK - http://www.listenlive.eu/uk.html

class Radio(object):

    STATIONS = {
        "absolute radio":"http://network.absoluteradio.co.uk/core/audio/mp3/live.pls?service=arbb"
        "absolute 80s":"http://network.absoluteradio.co.uk/core/audio/mp3/live.pls?service=a8bb"
        "absolute 90s":"http://network.absoluteradio.co.uk/core/audio/mp3/live.pls?service=a9bb"
        "absolute noughties":"http://network.absoluteradio.co.uk/core/audio/mp3/live.pls?service=a0bb"
        "eagle radio":"http://str1.sad.ukrd.com/eagle.m3u"
        "bbc radio 1":"http://www.listenlive.eu/bbcradio1.m3u"
        "bbc radio 2":"http://www.listenlive.eu/bbcradio2.m3u"
        "bbc radio 3":"http://www.listenlive.eu/bbcradio3.m3u"
        "bbc radio 4":"http://www.listenlive.eu/bbcradio4.m3u"		
        "capital fm":"http://media-ice.musicradio.com/CapitalMP3.m3u"
    }

    def __init__(self, say, keyword):
        self.say = say
        self.keyword = keyword

    def run(self, voice_command):

        station = ((voice_command.lower()).replace(self.keyword, '', 1)).strip()

        if station == 'list':
            logging.info("Enumerating radio stations")
            self.say("Available stations are")
            for key in Radio.STATIONS.keys():
                self.say(key)
            return

        elif station not in Radio.STATIONS:
            logging.info("Station not found: " + voice_command)
            self.say("radio station " + voice_command + " not found")
            return

        logging.info("streaming " + station)
        self.say("tuning the radio to " + station)

        p = subprocess.Popen(['/usr/bin/cvlc','--no-video','--quiet','--play-and-exit',Radio.STATIONS[station]],stdout=subprocess.PIPE,stderr=subprocess.PIPE)

        gpio.setmode(gpio.BCM)
        gpio.setup(23, gpio.IN)

        while p.poll() == None:
            if gpio.input(23) == 0:
                logging.info("stopping radio by GPIO")
                p.kill()
                break

            time.sleep(0.1)

        logging.info("radio stopped playing")

class Podcast(object):

    PODCASTS = {
        'no such thing as a fish':'https://audioboom.com/channels/2399216.rss'
        'good job brain':'https://audioboom.com/channels/2795364.rss',
        'freakonomics':'http://feeds.feedburner.com/freakonomicsradio?format=xml',
        'ted talks':'https://www.ted.com/feeds/talks.rss'
    }

    def __init__(self, say, keyword):
        self.say = say
        self.keyword = keyword
        self.podcast = None
        self.offset = None

    def run(self, voice_command):

        self.offset = 0
        self.podcast = ((voice_command.lower()).replace(self.keyword, '', 1)).strip()

        if self.podcast == 'list':
            logging.info("Enumerating Podcasts")
            self.say("Available podcasts are")
            for key in Podcast.PODCASTS.keys():
                self.say(key)
            return

        elif self.podcast not in Podcast.PODCASTS:
            logging.info("Podcast not found: " + self.podcast)
            self.say("Podcast " + self.podcast + " not found")
            return

        elif self.podcast.startswith('previous '):
            self.offset = 1
            self.podcast = self.podcast[9:]

        podcastInfo = self.getPodcastItem(Podcast.PODCASTS[self.podcast], self.offset)
        if podcastInfo == None:
            logging.info("Podcast failed to load")
            return
        logging.info("Podcast Title: " + podcastInfo['title'])
        logging.info("Podcast URL: " + podcastInfo['url'])
        logging.info("Podcast Date: " + podcastInfo['published'])

        self.say("Playing episode of " + self.podcast + " titled " + podcastInfo['title'])

        p = subprocess.Popen(['/usr/bin/cvlc','--no-video','--quiet','--play-and-exit',podcastInfo['url']],stdout=subprocess.PIPE,stderr=subprocess.PIPE)

        gpio.setmode(gpio.BCM)
        gpio.setup(23, gpio.IN)

        while p.poll() == None:
            if gpio.input(23) == 0:
                logging.info("stopping podcast by GPIO")
                p.kill()
                break

            time.sleep(0.1)

        logging.info("podcast stopped playing")

    def getPodcastItem(self, src, offset):

        result = {
            "url":None,
            "title":None,
            "published_parsed":None,
            "published":None
        }

        logging.info("loading " + src + " podcast feed")
        rss = feedparser.parse(src)

        # get the total number of entries returned
        resCount = len(rss.entries)
        logging.info("feed contains " + str(resCount) + " items")

        # exit out if empty
        if resCount < offset:
            logging.info(self.podcast + " podcast feed is empty")
            self.say("There are no episodes available of " + self.podcast)
            return None

        rssItem = rss.entries[offset]

        # Extract infromation about requested item

        if 'title' in rssItem:
            result['title'] = rssItem.title

        if 'published_parsed' in rssItem:
            result['date_parsed'] = rssItem.published_parsed

        if 'published' in rssItem:
            result['published'] = rssItem.published

        if 'media_content' in rssItem:
            result['url'] = rssItem.media_content[0]['url']

        elif 'enclosures' in rssItem:
            result['url'] = rssItem.enclosures[0]['href']

        else:
            logging.info(self.podcast + " feed format is unknown")
            self.say("The feed for " + self.podcast + " is unknown format")
            return None

        return result

class play(object):

    def __init__(self, say, keyword):
        self.say = say
        self.keyword = keyword

    def run(self, voice_command):

        track = voice_command.replace(self.keyword, '', 1) 

        p = subprocess.Popen(["/usr/local/bin/mpsyt",""],stdin=subprocess.PIPE,stdout=subprocess.PIPE)

        p.stdin.write(bytes('/' + track + '\n1\n', 'utf-8'))
        p.stdin.flush()

        while gpio.input(23):
             time.sleep(1)

        pkill = subprocess.Popen(["/usr/bin/pkill","omxplayer"],stdin=subprocess.PIPE)
        p.kill()


def make_actor(say):
    """Create an actor to carry out the user's commands."""

    actor = actionbase.Actor()

    actor.add_keyword(
        _('ip address'), SpeakShellCommandOutput(
            say, "ip -4 route get 1 | head -1 | cut -d' ' -f8",
            _('I do not have an ip address assigned to me.')))

    actor.add_keyword(_('volume up'), VolumeControl(say, 10))
    actor.add_keyword(_('volume down'), VolumeControl(say, -10))
    actor.add_keyword(_('volume max'), VolumeControl(say, -10))
    actor.add_keyword(_('max volume'), VolumeControl(say, 100))

    actor.add_keyword(_('repeat after me'),
                      RepeatAfterMe(say, _('repeat after me')))

    # =========================================
    # Makers! Add your own voice commands here.
    # =========================================

    # streaming radio station commend
    actor.add_keyword(_('radio'), Radio(say,_('radio')))

    # streaming most recent podcast
    actor.add_keyword(_('podcast'), Podcast(say,_('podcast')))

	
    #play youtube audio - be as specific as possible for the video otherwise you will get some interestng results
    actor.add_keyword(_('play'), play(say,_('play')))
    return actor


def add_commands_just_for_cloud_speech_api(actor, say):
    """Add simple commands that are only used with the Cloud Speech API."""
    def simple_command(keyword, response):
        actor.add_keyword(keyword, SpeakAction(say, response))

    simple_command('alexa', _("We've been friends since we were both starter projects"))
    simple_command(
        'beatbox',
        'pv zk pv pv zk pv zk kz zk pv pv pv zk pv zk zk pzk pzk pvzkpkzvpvzk kkkkkk bsch')
    simple_command(_('clap'), _('clap clap'))
    simple_command('google home', _('She taught me everything I know.'))
    simple_command(_('hello'), _('hello to you too'))
    simple_command(_('tell me a joke'),
                   _('What do you call an alligator in a vest? An investigator.'))
    simple_command(_('three laws of robotics'),
                   _("""The laws of robotics are
0: A robot may not injure a human being or, through inaction, allow a human
being to come to harm.
1: A robot must obey orders given it by human beings except where such orders
would conflict with the First Law.
2: A robot must protect its own existence as long as such protection does not
conflict with the First or Second Law."""))
    simple_command(_('where are you from'), _("A galaxy far, far, just kidding. I'm from Seattle."))
    simple_command(_('your name'), _('A machine has no name'))

    actor.add_keyword(_('time'), SpeakTime(say))

