import cherrypy
import os
import threading
from fitbit.api import FitbitOauth2Client
from urllib.parse import urlparse

class OAuth2Server:
    def __init__(self, client_id, client_secret, redirect_uri='http://127.0.0.1:8080/'):
        self.success_html = "<h1>Success!</h1><p>You can close this window and go back to Python.</p>"
        self.fitbit = FitbitOauth2Client(client_id, client_secret)
        self.redirect_uri = redirect_uri

    def browser_authorize(self):
        url, _ = self.fitbit.authorize_token_url(redirect_uri=self.redirect_uri)
        import webbrowser
        webbrowser.open(url)
        
        # Configure CherryPy to listen on the correct port
        url_parts = urlparse(self.redirect_uri)
        cherrypy.config.update({'server.socket_host': '127.0.0.1', 'server.socket_port': url_parts.port})
        cherrypy.quickstart(self)

    @cherrypy.expose
    def index(self, state, code=None, error=None):
        # This handles the root URL or the /callback URL
        if code:
            self.fitbit.fetch_access_token(code, self.redirect_uri)
            # Shut down the server after 1 second so the script can continue
            threading.Timer(1, cherrypy.engine.exit).start()
            return self.success_html
        return "<h1>Error</h1><p>No code received from Fitbit.</p>"

    @cherrypy.expose
    def callback(self, state, code=None, error=None):
        # This explicitly handles the /callback path
        return self.index(state, code, error)
