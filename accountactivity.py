#Author: Adeyemo Joel
#File: authenticate.py
#Date:1/9/2024



#Dependencies
import os,getpass
import pandas as pd
import requests
from icecream import ic  # used for printing


class AccountActivity():
    def __init__(self):
        pass
    #---------------------------------------------------------
    def check_apirefract(self):
        ''' Checks if the api refract for M1 finance isn't working
            @return : successful
        '''
        
        url =  'https://api.refract.m1finance.com/v1/p'
        
        header = {
            
        }
        
    def get_investment_activity(self):
        '''
            The function kind of the first 10 pages of the Investment Activities for only one account
        '''
        url = 'https://lens.m1.com/graphql'
        
        payload ={
            
            "operationName": "GetInvestActivity",
            "variables": {
                "id": os.getenv('accountID'),
                "first": 20,
                "sort": {
                    "direction": "DESC",
                    "type": "DATE"
                },
                "filter": {
                    "includeCategoryCash": True,
                    "includeCategoryDividend": True,
                    "includeCategoryTrading": True,
                    "includeCategoryPosition": True,
                    "includeCategoryTransfer": True,
                    "symbols": [],
                    "toDate": None,
                    "fromDate": None
                }
            },
            "query": "query GetInvestActivity($id: ID!, $first: Int, $after: String, $filter: InvestActivityEntryFilterInput, $sort: [InvestActivityEntrySortInput!]) {\n  node(id: $id) {\n    ...InvestActivity\n    __typename\n  }\n}\n\nfragment InvestActivity on Account {\n  investActivity {\n    activity(first: $first, after: $after, filter: $filter, sort: $sort) {\n      pageInfo {\n        ...PageInfo\n        __typename\n      }\n      edges {\n        node {\n          ...InvestActivityNode\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment PageInfo on PageInfo {\n  hasNextPage\n  hasPreviousPage\n  startCursor\n  endCursor\n  __typename\n}\n\nfragment InvestActivityNode on InvestActivityEntry {\n  __typename\n  id\n  title\n  date(local: true)\n  description\n  ... on InvestActivityTradeSummaryEntry {\n    countOfBuys\n    countOfSells\n    amountOfBuys\n    amountOfSells\n    __typename\n  }\n  ... on InvestActivityTradeEntry {\n    amount\n    tradeSecurity {\n      descriptor\n      security {\n        symbol\n        name\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n  ... on InvestActivityCashEntry {\n    amount\n    isRelatedToSecurity\n    cashSecurity {\n      descriptor\n      security {\n        symbol\n        name\n        __typename\n      }\n      __typename\n    }\n    transferDetails {\n      transferSummary\n      transferId\n      totalAmount\n      __typename\n    }\n    __typename\n  }\n  ... on InvestActivityPositionEntry {\n    quantity\n    positionSecurity {\n      descriptor\n      security {\n        symbol\n        name\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}"
        }
        
        M1_token = os.getenv("M1_token")
        header= {
            "authority": "lens.m1.com",
            "accept": "*/*",
            "origin": "https://dashboard.m1.com",
            "referer": "https://dashboard.m1.com/",
            "content-type": "application/json",
            "Authorization": "Bearer " + str(M1_token)
        }
        
        response = requests.request("POST", url, json=payload, headers=header)
        
        if response.status_code != 200:
            raise Exception(
                f"ERROR: Response returned status code {response.status_code}. Check your credentials and try again."
            )
        
        # Parse the response data 
        ic(response.json()) 

    def get_investmentpage(self):
        '''
            Get the nickname, Account number  and Current Total value
        '''
        url = 'https://lens.m1.com/graphql'
        
        
        payload ={
            "operationName": "InvestPage",
            "variables": {'activeAccountId': os.getenv('accountID') },
            "query": "query InvestPage($activeAccountId: ID!) {\n  account: node(id: $activeAccountId) {\n    ...InvestPageAccountNode\n    __typename\n  }\n  viewer {\n    invest {\n      acatWizardEntryLink {\n        ...Linkable\n        __typename\n      }\n      __typename\n    }\n    accounts(first: 50) {\n      edges {\n        node {\n          id\n          nickname\n          number\n          registration\n          balance {\n            totalValue {\n              value\n              __typename\n            }\n            __typename\n          }\n          transferParticipantType\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    transfers {\n      isEligibleForFundingSourceUpdate\n      __typename\n    }\n    __typename\n  }\n}\n\nfragment InvestPageAccountNode on Account {\n  allowsExternalFunding\n  isCryptoAccount\n  isCustodialAccount\n  id\n  nickname\n  number\n  __typename\n}\n\nfragment Linkable on Linkable {\n  __typename\n  title\n  ...AppLink\n  analyticsEvent {\n    ...AnalyticsEvent\n    __typename\n  }\n  ...TransferSuggestion\n}\n\nfragment AppLink on AppLink {\n  articleId\n  internalPath\n  title\n  url\n  analyticsEvent {\n    ...AnalyticsEvent\n    __typename\n  }\n  __typename\n}\n\nfragment AnalyticsEvent on AppAnalyticsEvent {\n  name\n  valueParameter\n  customParameters {\n    name\n    value\n    __typename\n  }\n  customBoolParameters {\n    name\n    value\n    __typename\n  }\n  customNumberParameters {\n    name\n    value\n    __typename\n  }\n  __typename\n}\n\nfragment TransferSuggestion on TransferSuggestionLink {\n  title\n  suggestion {\n    transferType\n    fromParticipant {\n      id\n      __typename\n    }\n    toParticipant {\n      id\n      __typename\n    }\n    amount\n    __typename\n  }\n  __typename\n}"   
        }
        
        M1_token = os.getenv("M1_token")
        header = {
            "authority": "lens.m1.com",
            "accept": "*/*",
            "origin": "https://dashboard.m1.com",
            "referer": "https://dashboard.m1.com/",
            "content-type": "application/json",
            "Authorization": "Bearer " + str(M1_token)
        }
        
        response = requests.request("POST", url, json=payload, headers=header)
        
        if response.status_code != 200:
            raise Exception(
                f"ERROR: Response returned status code {response.status_code}. Check your credentials and try again."
            )
        
        # Parse the response data 
        ic(response.json()) 
        df = pd.DataFrame(response.json())
        new_df =pd.DataFrame()
        new_df = self.parse_data(df)
        
        # Add the values to the user's environment
        if new_df.any().any():
            os.environ['M1_number'] = new_df['number']
            os.environ['M1_nickname'] = new_df['nickname']
            os.environ['M1_totalAccountValue'] = new_df['balance']
            os.environ['registration'] = new_df['registration']
    
    def parse_data(self,df:pd.DataFrame):
        ''' 
            data
                account
                    allowsExternalFunding
                    isCryptoAccount
                    isCustodialAccount
                    id
                    nickname
                    number
                    __typename
                viewer
                    invest
                        __typename
                        acatWizaardEntryLink
                        analyticsEvent
                    accounts
                        edges
                            node
                                balance
                                    totalValue
                                        value
                                        __typename
                                    __typename
                                id
                                nickname
                                number
                                registration
                                transferParticipantType
                                __typename
                            __typename
                        __typename
                    transfer
                        __typename
                        isEligibleForFundingSourceUpdate
                    __typename
        '''
        new_df = df['data']['viewer']['accounts']['edges']
        
        # Just Incase if the person has multiple accounts
        data = []
        for idx, values in enumerate(new_df):
            needed_data={
                'index': idx,
                'number': values['node']['number'],
                'nickname': values['node']['nickname'],
                'registration':values['node']['registration'],
                'balance':values['node']['balance']['totalValue']['value']
            }
            data.append(needed_data)
        
        c_df =pd.DataFrame(data)
        return c_df
        
            
        
    
        
        



if __name__ == '__main__':
    Activities=AccountActivity()
    Activities.get_investmentpage()