import threading
import time
import urllib.parse
import webbrowser
from datetime import datetime

import requests
import spotipy
from flask import Flask, redirect, request, jsonify, json

import os
import sys


class TokenManager():
    def __init__(self, client_id="", client_secret="", on_token_refresh=None):

        self.scope = "user-read-currently-playing user-read-playback-state"

        self.on_token_refresh = on_token_refresh

        self.CLIENT_ID = client_id
        self.CLIENT_SECRET = client_secret
        self.REDIRECT_URI = "http://127.0.0.1:8888/callback"

        self.AUTH_URL = "https://accounts.spotify.com/authorize"
        self.TOKEN_URL = "https://accounts.spotify.com/api/token"
        self.API_BASE_URL = "https://accounts.spotify.com/v1"

        self.session = {}

        self.CACHE_FILE = ".cache"
        self.session = self.load_session()

        if self.session and "access_token" in self.session:
            if self.is_expired():
                print("Token expired, refreshing...")
                self.refresh_token()
            else:
                print("Token loaded from .cache and still valid.")
        else:
            print("No valid session found. Login required.")

        self.start_auto_refresh()

        self.app = Flask(__name__)
        self.setup_routes()

    def setup_routes(self):
        @self.app.route("/login")
        def login():
            params = {
                "client_id": self.CLIENT_ID,
                "response_type": "code",
                "scope": self.scope,
                "redirect_uri": self.REDIRECT_URI
            }
            auth_url = f"{self.AUTH_URL}?{urllib.parse.urlencode(params)}"
            return redirect(auth_url)

        @self.app.route("/callback")
        def callback():
            if "error" in request.args:
                return jsonify({"error": request.args["error"]})

            elif "code" in request.args:
                req_body = {
                    "code": request.args["code"],
                    "grant_type": "authorization_code",
                    "redirect_uri": self.REDIRECT_URI,
                    "client_id": self.CLIENT_ID,
                    "client_secret": self.CLIENT_SECRET
                }

                response = requests.post(self.TOKEN_URL, data=req_body)
                token_info = response.json()

                if "access_token" in token_info:
                    self.session["access_token"] = token_info["access_token"]
                    self.session["refresh_token"] = token_info["refresh_token"]
                    self.session["expires_at"] = datetime.now().timestamp() + token_info["expires_in"]
                    self.save_session()
                    return "Spotify login successful. You can close this tab."
                else:
                    return "Failed to obtain token."

    def start_server(self):
        # Run Flask in a separate thread
        threading.Thread(target=lambda: self.app.run(port=8888, debug=False, use_reloader=False), daemon=True).start()
        webbrowser.open("http://127.0.0.1:8888/login")

        self.login()



    def save_session(self):
        try:
            with open(self.CACHE_FILE, "w") as f:
                json.dump(self.session, f)
        except Exception as e:
            print(f"Failed to save session: {e}")

    def load_session(self):
        if os.path.exists(self.CACHE_FILE):
            try:
                with open(self.CACHE_FILE, "r") as f:
                    return json.load(f)
            except Exception as e:
                print(f"Failed to load session: {e}")
        return {}




    def login(self):

        if self.CLIENT_ID == "" or self.CLIENT_SECRET == "":
            raise Exception("Client credentials not set")

        params = {
            "client_id": self.CLIENT_ID,
            "response_type": "code",
            "scope": self.scope,
            "redirect_uri": self.REDIRECT_URI,
            "show_dialog": True
        }

        auth_url = f"{self.AUTH_URL}?{urllib.parse.urlencode(params)}"

        return redirect(auth_url)


    def is_expired(self):
        if "expires_at" not in self.session:
            return True

        return datetime.now().timestamp() > self.session["expires_at"]

    def is_session_valid(self):
        return "access_token" in self.session and "refresh_token" in self.session and not self.is_expired()


    def get_token(self):
        if "access_token" not in self.session:
            raise Exception("No access token available, authenticate please")

        if datetime.now().timestamp() > self.session["expires_at"]:
            try:
                self.refresh_token()
            except Exception as e:
                raise Exception(f"Failed refreshing token: {e}")

        return self.session.get("access_token")



    def refresh_token(self):

        if "refresh_token" not in self.session:
            raise Exception("No refresh token available, authenticate please")

        if self.CLIENT_ID == "" or self.CLIENT_SECRET == "":
            raise Exception("Client credentials not set")

        req_body = {
            "grant_type": "refresh_token",
            "refresh_token": self.session["refresh_token"],
            "client_id": self.CLIENT_ID,
            "client_secret": self.CLIENT_SECRET
        }

        response = requests.post(self.TOKEN_URL, data=req_body)
        new_token_info = response.json()

        if "access_token" in new_token_info:
            self.session["access_token"] = new_token_info["access_token"]
            self.session["expires_at"] = datetime.now().timestamp() + new_token_info["expires_in"]

            if "refresh_token" in new_token_info:
                self.session["refresh_token"] = new_token_info["refresh_token"]

            self.save_session()

            if self.on_token_refresh:
                self.on_token_refresh()

        else:
            raise Exception("No valid token available")

    def start_auto_refresh(self):
        def refresh_loop():
            while True:
                time.sleep(300)
                if not self.session or "expires_at" not in self.session:
                    continue

                time_left = self.session["expires_at"] - datetime.now().timestamp()
                if time_left <= 600:
                    print(f"[TokenManager] Access token expiring in {int(time_left)}s, refreshing...")
                    self.refresh_token()



        t = threading.Thread(target=refresh_loop, daemon=True)
        t.start()


    def create_spotify_client(self):
        token = self.get_token()
        if not token:
            raise Exception("No valid token available")

        return spotipy.Spotify(auth=token, requests_timeout=10)








