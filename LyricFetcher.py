import spotipy
from lrclib import LrcLibAPI
import time



class LyricFetcher:
    def __init__(self, callback_function):

        self.lrc_api = LrcLibAPI(user_agent="SpotifyLyrics/1.0")
        self.callback = callback_function
        self.running = True

        # Current track data
        self.last_id = None
        self.artist_name = ""
        self.track_name = ""
        self.album_name = ""
        self.duration = 0
        self.timestamps = []
        self.lyrics = []
        self.current_lyrics = []
        self.display_lyrics = ["", "", "", ""]
        self.ind = 0
        self.wait_time = 0

        self.sp = None

    def ExtractTimestamps(self, temp_lyrics):
        self.ind = 0
        self.timestamps.clear()
        self.lyrics.clear()
        self.display_lyrics = ["", "", "", ""]

        if temp_lyrics is None:
            self.ind = -1
            return

        for raw in temp_lyrics:
            if ']' not in raw or '[' not in raw:
                continue
            try:
                raw_time, raw_lyrics = raw[1:].split("]", 1)
                minutes, seconds = raw_time.split(":")
                minutes = int(minutes)
                seconds = float(seconds)
                total_time = minutes * 60 + seconds

                if raw_lyrics.strip() == "":
                    raw_lyrics = "(...)"

                self.timestamps.append(total_time)
                self.lyrics.append(raw_lyrics[1:] if raw_lyrics.startswith(' ') else raw_lyrics)
            except (ValueError, IndexError):
                continue

        for i in range(3):
            self.timestamps.append(self.timestamps[-1] + 5)
            self.lyrics.append("")

    def FindLocation(self, progress):
        # Find where we are in the song
        if self.ind == -1:
            return False

        old_ind = self.ind
        track_length = len(self.timestamps)

        while self.ind < track_length - 1 and progress > self.timestamps[self.ind+1]-0.1:
            self.ind += 1

        while self.ind > 0 and progress < self.timestamps[self.ind-1]-0.1:
            self.ind -= 1

        if self.ind < track_length - 1:
            self.wait_time = self.timestamps[self.ind] - progress - 0.1
        else:
            self.wait_time = 0

        # The lyrics changed
        if old_ind != self.ind:
            self.PrepareLyrics(self.ind)
            return True
        return False

    def PrepareLyrics(self, ind):
        # Update lyrics to new ones
        self.display_lyrics = ["", "", "", ""]

        if ind >= 2:
            self.display_lyrics[0] = self.lyrics[ind - 2]
        if ind >= 1:
            self.display_lyrics[1] = self.lyrics[ind - 1]
        if ind < len(self.lyrics):
            self.display_lyrics[2] = self.lyrics[ind]
        if ind < len(self.lyrics) - 1:
            self.display_lyrics[3] = self.lyrics[ind + 1]

    def Run(self):

        while self.running:
            if(self.sp):
                try:
                    # Get the current track
                    current_track = self.sp.current_user_playing_track()

                    # If the track is available and still playing
                    if current_track and current_track["is_playing"]:
                        # Get the current id
                        track_id = current_track["item"]["id"]

                        # Check if the track changed to update data
                        if track_id != self.last_id:
                            self.artist_name = current_track["item"]["artists"][0]["name"]
                            self.track_name = current_track["item"]["name"]
                            self.album_name = current_track["item"]["album"]["name"]
                            self.duration = current_track["item"]["duration_ms"] // 1000
                            self.last_id = track_id

                            print(f"Playing {self.track_name} by {self.artist_name}")

                            try:
                                lyric_result = self.lrc_api.get_lyrics(
                                    track_name=self.track_name,
                                    artist_name=self.artist_name,
                                    album_name=self.album_name,
                                    duration=self.duration
                                )
                                if lyric_result and lyric_result.synced_lyrics:
                                    self.current_lyrics = lyric_result.synced_lyrics
                                    self.ExtractTimestamps(self.current_lyrics.splitlines())
                                else:
                                    self.ind = -1
                                    print("No synced lyrics found")
                                    self.display_lyrics = ["", "", "No lyrics for this track :(", ""]
                                    self.callback(self.display_lyrics)

                            # If no lyrics found
                            except Exception as e:
                                print(f"Error fetching lyrics: {e}")
                                self.ind = -1
                                self.display_lyrics = ["", "", "No lyrics for this track :(", ""]
                                self.callback(self.display_lyrics)

                        # Get the current progress in seconds
                        progress = current_track["progress_ms"] / 1000
                        lyrics_changed = self.FindLocation(progress)

                        # If lyrics changed, notify the callback
                        if lyrics_changed and self.callback:
                            self.callback(self.display_lyrics)

                        time.sleep(0.5)

                except Exception as e:
                    print(f"Error in lyric fetcher: {e}")

    def Stop(self):
        self.running = False


