import urllib.parse
from datetime import datetime

import requests
import spotipy
from flask import Flask, redirect, request, jsonify


class TokenManager():
    def __init__(self, client_id="", client_secret=""):

        self.secret_key = "secret_key"
        self.scope = "user-read-currently-playing user-read-playback-state"

        self.CLIENT_ID = client_id
        self.CLIENT_SECRET = client_secret
        self.REDIRECT_URI = "http://127.0.0.1:8888/callback"

        self.AUTH_URL = "https://accounts.spotify.com/authorize"
        self.TOKEN_URL = "https://accounts.spotify.com/api/token"
        self.API_BASE_URL = "https://accounts.spotify.com/v1"

        self.session = {}



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


    def callback(self):
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
                return jsonify({"success": "Token obtained successfully"})
            else:
                return jsonify({"error": "Failed to obtain token"})

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

        else:
            raise Exception("No valid token available")


    def create_spotify_client(self):
        token = self.get_token()
        if not token:
            raise Exception("No valid token available")

        return spotipy.Spotify(auth=token)








