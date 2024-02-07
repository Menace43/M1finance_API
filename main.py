
# Author: Adeyemo Joel
# Date: 2/5/2024


# Dependencies



#User Defined Depnendencies
from authenticate import Authentication
from accountactivity import AccountActivity


if __name__ == '__main__':
    auth_normal=Authentication()
    auth_normal.run()
    
    Activities=AccountActivity()
    #Activities.get_investment_activity()
    Activities.get_investmentpage()