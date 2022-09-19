import base64
import datetime 
import requests
from urllib.parse import urlencode  

client_id = 'client id'
client_secret ='secret id'


class SpotifyAPI(object):
    acess_token = None
    acess_token_expires = datetime.datetime.now() 
    acess_token_did_expire =True 
    client_id = None
    client_secret = None
    token_url = 'https://accounts.spotify.com/api/token'

    
    def __init__(self, client_id, client_secret, *args,**kwargs):
        super().__init__(*args, **kwargs)
        self.client_id = client_id
        self.client_secret= client_secret 

        
    def get_client_credentials(self):
        
        client_id = self.client_id
        client_secret = self.client_secret
        
        if client_id is None or client_secret is None:
            raise Exception("you must set cliend_id  and client_secret")
        client_creds  = f"{client_id}:{client_secret}"
        client_creds_b64 =base64.b64encode(client_creds.encode())
        return client_creds_b64.decode()
        
    def get_token_headers(self):
        client_creds_b64 = self.get_client_credentials()
        return {
    "Authorization":f"Basic {client_creds_b64}"
        }
        
    def get_token_data(self):
        return {
        "grant_type" :"client_credentials"
        }
        
    def perform_auth(self):
        token_url = self.token_url
        token_data = self.get_token_data()
        token_headers =self.get_token_headers()
        r = requests.post(token_url, data =token_data, headers=token_headers)
        if r.status_code not in range (200,299):
            raise Exception("couldn'tAuthenticate client")
        data = r.json()
        now = datetime.datetime.now()
        acess_token = data["access_token"]
        expires_in = data["expires_in"]#seconds
        expires = now+datetime.timedelta(seconds= expires_in)
        self.acess_token = acess_token
        self.acess_token_expires = expires
        self.acess_token_did_expire = expires<now
        return True
    
    
    def get_acess_token(self):
        token=self.acess_token 
        expires=self.acess_token_expires
        now = datetime.datetime.now()
        if expires < now :
            self.perform_auth()
            return self.get_acess_token()
        elif token == None:
            self.perform_auth()
            return self.get_acess_token()
        return token
    
    def get_resource_header(self):
        acess_token = self.get_acess_token()
        headers = {
            "Authorization" : f"Bearer {acess_token}" 
        }
        return headers
        
    
    def get_resources(self, _id, resource_type = 'albums', version = 'v1'):
        endpoint = f"https://api.spotify.com/{version}/{resource_type}/{_id}"
        headers = self.get_resource_header()
        r = requests.get(endpoint, headers = headers)
        if r.status_code not in range(200,299):
            return {}
        return r.json()    
    
    def get_album(self,_id):
        return self.get_resources(_id,resource_type = "albums") 
        
    def get_artist(self,_id):
        return self.get_resources(_id,resource_type = "artists")
    
    
    def base_search(self,query_params):
        headers = self.get_resource_header()
        endpoint = "https://api.spotify.com/v1/search"
        lookup_url = f"{endpoint}?{query_params}"
        r= requests.get(lookup_url, headers = headers)
        if r.status_code not in range(200,299):
            return {}
        return r.json() 
    
    
 
    def search(self, query=None, operator=None, operator_query=None, search_type='artist'):

        if query == None:
            raise Exception(" A query is required")

        if isinstance(query, dict):
             query = " ".join([f"{k}:{v}" for k,v in query.items()])

        if operator != None and operator_query !=None:
            if operator.lower() == "or" or operator.lower() == "not":
                operator= operator.upper()
                if isinstance(operator_query,str): 
                    query= f"{query} {operator} {operator_query}"

        query_params = urlencode({"q": query,"type":search_type.lower()})
        print(query_params)
        return self.base_search(query_params)

spotify = SpotifyAPI(client_id, client_secret)

spotify.search(query = "Danger", operator = "NOT", operator_query = "Zone",search_type="track")


spotify.search(query = "Danger", operator_query = "Zone",search_type="track")

