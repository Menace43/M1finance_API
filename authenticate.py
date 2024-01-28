#Author: Adeyemo Joel
#File: authenticate.py
#Date:1/7/2024


# Dependencies
import os,getpass
import pandas as pd
import requests
from icecream import ic  # used for printing

class Authentication():
    def __init__(self):
        self.available=False
        self.available=self.isAccountavailable()
    #---------------------------------------------------------
    def isAccountavailable(self):
        if os.getenv('M1_USER') and os.getenv('M1_PASS'):
            return True
        else:
            return False
    #---------------------------------------------------------
    def get_credentials(self):
        '''
            Get credentials to obtain an M1 auth token.
        
            @details
            This function checks whether a session is interactive. If it is, it prompts the
            user to enter their username and password. Otherwise, it checks .Renviron for the
            credentials.
        '''
        
        if os.isatty(0):  #if running an interactive session 
            try:
                username=input("Enter M1 Finane Username: ")
                password=getpass.getpass("M1 Finance password: ")
                os.environ['M1_USER'] = username
                os.environ['M1_PASS'] = password
                self.available=True
            except Exception as e:
                ic(e)
        else:
            print("Checking environment variables for username and password...")
            username = os.getenv("M1_USER")
            password = os.getenv("M1_PASS")
    
        
        if not username or not password:
            raise ValueError("Could not find username and password. "
                         "Please set up the following environment variables for non-interactive sessions: M1_USER, M1_PASS")
        return {
            "username":username,
            "password":password,
        }
    #---------------------------------------------------------
    def checksystemstatus(self):
        '''
            Checks if the system is still running
            
            @details
            This function checks the website is working and if anything is blocking the website to not work
        '''
        try:
            url = 'https://lens.m1.com/graphql'
            
            payload={
                "operationName": "CheckSystemStatus",
                "variables": {},
                "query": "query CheckSystemStatus{\n system{\n version\n status\n statusMessage\n isStatusBlocking\n blockedFunctionality\n __typename\n }\n }"
            }
            
            header= {
                "authority": "lens.m1.com",
                "accept": "*/*",
                "origin": "https://dashboard.m1.com",
                "referer": "https://dashboard.m1.com/",
            }
            response = requests.post(url, json=payload, headers=header)
            
            if response.status_code != 200:
                raise Exception(
                    f"ERROR: Response returned status code {response.status_code}. Check your credentials and try again."
                )
            
            ic(response.json())
            ic(response.cookies)
            ic(response.content)
            print(response.cookies.get("__cf_bm"))
            
            return response.cookies
        except Exception as e:
            ic(e)
            ic("Please Check Connection")
    #---------------------------------------------------------
    def get_auth_token(self):
        '''
            Uses the credentials to get authentication token that is important to the M1 functionality
        
            @details
            This function gets the users credentials, get the authentication token, 
            get the userid and checks if it worked
            
        '''
        credentials= self.get_credentials()     #get the users credentials
        if not credentials:
            return
        
        url = 'https://lens.m1.com/graphql'
        
        payload={
            "operationName": "Authenticate",
            "variables": {"input":{
                "password": credentials['password'],
                "username": credentials['username']
            }},
            "query": "mutation Authenticate($input: AuthenticateInput!) {\n  authenticate(input: $input) {\n    result {\n      didSucceed\n      inputError\n      __typename\n    }\n    accessToken\n    refreshToken\n    viewer {\n      user {\n        id\n        correlationKey\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}"
        }
        
        header= {
            "authority": "lens.m1.com",
            "accept": "*/*",
            "origin": "https://dashboard.m1.com",
            "referer": "https://dashboard.m1.com/",
            "content-type": "application/json; charset=utf-8"
        }
        
        response = requests.request("POST",url, json=payload, headers=header)
        
        if response.status_code != 200:
            raise Exception(
                f"ERROR: Response returned status code {response.status_code}. Check your credentials and try again."
            )
        
        ic(response.json())
        df = pd.DataFrame(response.json())
        new_df=self.parse_auth_data(df)
        
        # Add the authentication token to os
        if new_df['AccessToken']:
            os.environ["M1_token"]= new_df['AccessToken']
        else:
            raise Exception("Token not found in response cookies.")
    #---------------------------------------------------------
    def parse_auth_data(self,df:pd.DataFrame):
        ic(df.keys())
        new_df=df['data']['authenticate']
        ic(new_df.keys())  # result,accessToken,refreshToken,viewwer
        
        res_df=new_df['result']
        AccToken_df =new_df['accessToken']
        refToken_df = new_df['refreshToken']
        view_df =new_df['viewer']
        
        
        ic(res_df['didSucceed'])  #Check for success
        ic(AccToken_df) # Get the access Token
        ic(refToken_df) # Get the refresh Token
        ic(view_df['user']['id']) # Get the user ID 
        
        return {
            "user_id": view_df['user']['id'],
            "didSucceed": res_df['didSucceed'],
            "AccessToken": AccToken_df,
            "RefreshToken": refToken_df
        }
    #---------------------------------------------------------    
    def get_auth_token2(self):
        credentials= self.get_credentials()     #get the users credentials
          
        url = 'https://lens.m1.com/graphql'
        api_url = 'https://api.refract.m1finance.com/v1/i'
        
        session = requests.Session()
        initial_response= session.post(url)
        
        ic(initial_response)
        
        login_data ={
            "username": credentials['username'],
            "password": credentials['password'],
        }
        
        response = session.post(api_url, data=login_data)
        
        if response.status_code != 200:
            raise Exception(
                f"ERROR: Response returned status code {response.status_code}. Check your credentials and try again."
            )
        
        ic(response.json())
        ic(response.request)
    #--------------------------------------------------------- 
    def get_chat_context(self):
        '''
            A Layer of verification 
        
            @details
            This function verifies the authentication token
            
            @return Add the user correletion key to the environment
        '''
        url = 'https://lens.m1.com/graphql'
        
        M1_token = os.getenv("M1_token")
        if not M1_token:
            return
        
        payload={
            "operationName": "ChatContext",
            "variables": {},
            "query":"query ChatContext {\n  viewer {\n    user {\n      id\n      username\n      isPrimaryEmailVerified\n      correlationKey\n      intercomIdentityHash\n      __typename\n    }\n    profile {\n      primary {\n        firstName\n        __typename\n      }\n      __typename\n    }\n    plus {\n      hasPlus\n      __typename\n    }\n    __typename\n  }\n}"
        }
        
        header= {
            "authority": "lens.m1.com",
            "accept": "*/*",
            "origin": "https://dashboard.m1.com",
            "referer": "https://dashboard.m1.com/",
            "content-type": "application/json",
            "Authorization": "Bearer " + str(M1_token)
        }
        response = requests.post(url, json=payload, headers=header)
        
        if response.status_code != 200:
            raise Exception(
                f"ERROR: Response returned status code {response.status_code}. Check your credentials and try again."
            )
        
        # Parse the response data and get the correltion key
        ic(response.json()) 
        df = pd.DataFrame(response.json())
        new_df=self.parse_chat_context(df) 
        
        # Add the user correlation key to the environment
        if new_df:
            os.environ['correlationKey']=new_df
    #--------------------------------------------------------- 
    def parse_chat_context(self,df:pd.DataFrame):
        '''
           parse the bootstrap authetication response
           Add the user correletion key to the environment
        '''
        new_df=df['data']['viewer']['user']
        ic(new_df.keys())   #ID, Username, Correlaationkey,isPrimaryEmaailVerified
        return new_df['correlationKey']
    #---------------------------------------------------------    
    def get_bootstrap_auth(self):
        '''
            Another Layer of verification 
        
            @details
            This function verifies the authentication token
            
            @return Get the User ID that is important for getting account activities
                - Also returns the Other types of acccount like saving,Borrowing account etc
        '''
        url = 'https://lens.m1.com/graphql'
        
        M1_token = os.getenv("M1_token")
        
        if not M1_token :
            return
        
        payload={
            "operationName": "BootstrapAuthedUser",
            "variables": {},
            "query":"query BootstrapAuthedUser {\n  viewer {\n    accounts(first: 20, filterStatus: [NEW, OPENED, REJECTED, CLOSED]) {\n      edges {\n        node {\n          id\n          isActive\n          registration\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    borrow {\n      borrowAccounts {\n        edges {\n          node {\n            id\n            hasBorrowedBefore\n            __typename\n          }\n          __typename\n        }\n        __typename\n      }\n      personalLoans {\n        loans {\n          edges {\n            node {\n              id\n              status\n              __typename\n            }\n            __typename\n          }\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    spend {\n      currentSpendAccounts {\n        id\n        __typename\n      }\n      __typename\n    }\n    credit {\n      activeAccount {\n        id\n        __typename\n      }\n      __typename\n    }\n    id\n    user {\n      correlationKey\n      data(keys: [\"watchlist\"]) {\n        key\n        value\n        __typename\n      }\n      username\n      __typename\n    }\n    save {\n      savings {\n        hasSavingsAccounts\n        savingsAccounts {\n          edges {\n            node {\n              id\n              __typename\n            }\n            __typename\n          }\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    featureFlags {\n      hasFeature(keys: [\"M1_EMPLOYEE\"])\n      __typename\n    }\n    __typename\n  }\n}"
        }
        
        header= {
            "authority": "lens.m1.com",
            "accept": "*/*",
            "origin": "https://dashboard.m1.com",
            "referer": "https://dashboard.m1.com/",
            "content-type": "application/json",
            "Authorization": "Bearer " + str(M1_token)
        }
        response = requests.post(url, json=payload, headers=header)
        
        if response.status_code != 200:
            raise Exception(
                f"ERROR: Response returned status code {response.status_code}. Check your credentials and try again."
            )
        
        #Parse the accountID and add it the os environment 
        ic(response.json())
        df = pd.DataFrame(response.json())
        new_df=self.parse_bootstrap_auth(df) 
        
        if new_df:
            os.environ['accountID']= new_df
    #--------------------------------------------------------- 
    def parse_bootstrap_auth(self,df:pd.DataFrame):
        '''
           parse the bootstrap authetication response
           Add the AccountID from
        '''
        new_df=df['data']['viewer']['accounts']['edges']
        accountID=new_df[0]['node']['id']
        ic(accountID)
        return accountID
    #--------------------------------------------------------- 
    def run(self):
        self.checksystemstatus()
        self.get_auth_token()
        self.get_chat_context()
        self.get_bootstrap_auth()


class Reauthentication():
    def __init__(self):
        pass
        
        


if __name__ =="__main__":
    auth =Authentication()
    cookies=auth.checksystemstatus()
    auth.get_auth_token()
    auth.get_chat_context()
    auth.get_bootstrap_auth()


