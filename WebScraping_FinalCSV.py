from selenium import webdriver
from selenium.webdriver.common.by import By
#from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait
#from selenium.webdriver.support import expected_conditions as EC
import time
import timeit
import datetime
import pandas as pd

url = ''
columnNames=[]
csv_suffix = ''
blockcounterTotal = 0

while True:
    inp = input('Choose from Tobalaba (t) or Ethereum Main Chain (e):')
    if inp == 't':
        url = "http://netstats.energyweb.org/"
        columnNames = ['TimeStamp','BlockNumber','MinedBy','TimePerBlockInMS','EliaGroup', 'SlockitTobalabaNode0Genesis','Centrica','Shell','TWL','ParityTechnologiesAuthorityNode0','GridSingularity','SPGroup','ENGIEAuthorityNode','Eneco']
        csv_suffix = 'TobalabaData.csv'  
        break
    elif inp == 'e':
        url = "https://ethstats.net"
        columnNames = ['TimeStamp','BlockNumber','MinedBy','TimePerBlockInMS']
        csv_suffix = 'EthereumData.csv' 
        break

while(True):
    try:
        driver=webdriver.Firefox()
        wait = WebDriverWait(driver, 10)
        time.sleep(2)
        driver.get(url)
        time.sleep(5)
        
        df = pd.DataFrame(columns=columnNames)
        
        table = driver.find_element_by_css_selector(".table") #find the table
        rows = table.find_elements(By.TAG_NAME, "tr") # get all of the rows in the table ## verschieben nach unten in die erste for!
        
        lastBlock = 0
        blockcounter = 0
        start = timeit.default_timer()
        blockzeit = 0
        
        #create new csv file only with column headers
        csv_name = datetime.datetime.now().isoformat().replace(":","_")[:19] + "_" + csv_suffix
        df.to_csv(csv_name, sep='\t', encoding='utf-8')
        
        f = open(csv_name, 'a') # Open csv file in append mode
        
        #loop over time
        while (blockcounter < 2000) and (blockzeit < 120000): # restarts driver after 2000 blocks or when time between blocks exceeds 2 minutes
            currentBlock = int(driver.find_element_by_css_selector( ".bestblock > div:nth-child(2) > span:nth-child(2)").text.replace('#', '').replace(",",""))
            if (lastBlock == 0) or (lastBlock<currentBlock):  
                blockzeit = int((timeit.default_timer()- start)*1000) #measuring time difference in milliseconds
                start = timeit.default_timer()
                print("Current Block: " + str(currentBlock) + " Total Blocks counted so far: " + str(blockcounterTotal) + " Blocks counted in this csv File: " + str(blockcounter) + " Last Blocktime: " + str(blockzeit))
                time.sleep(0.5) # wait for stuff to be refreshed after new block
    
                #loop over table to make sure that all nodes are in columnNames
                for row in rows:
                    #Node Names - if name isn't in the dataframe yet -> add a column with the name to the dataframe
                    col = row.find_elements_by_css_selector("td:nth-child(2)")
                    if len(col)>0:
                        NodeName = col[0].text.translate ({ord(c): "" for c in "!@#$%^&*()[]{};:,./<>?\|`'~-=_+ "}) #getting rid of special characters
                        if not NodeName in df.columns:
                            #close the old csv file
                            f.close()
    
                            #add new column
                            columnNames.append(NodeName)
                            df = pd.DataFrame(columns=columnNames)
    
                            #open a new csv file with more columns
                            csv_name = datetime.datetime.now().isoformat().replace(":","_")[:19] + "_" + csv_suffix
                            df.to_csv(csv_name, sep='\t', encoding='utf-8')
                            f = open(csv_name, 'a') # Open csv file in append mode
    
                df = pd.DataFrame(columns=columnNames,index=range(1)) #create dataframe which will be filled
                
                df["TimeStamp"] = datetime.datetime.now().strftime('%x %X')
                df["BlockNumber"] = currentBlock #Block Number
                df["TimePerBlockInMS"] = blockzeit #Time passed since last block
    
                #MinedBy    
                df["MinedBy"] = driver.find_element_by_css_selector("div.blocks-holder:nth-child(2) > div:nth-child(2)").text    
    
                #loop over table for the propagation time
                for row in rows:
                    #nodename
                    col = row.find_elements_by_css_selector("td:nth-child(2)")
                    if len(col)>0:
                        NodeName = col[0].text.translate ({ord(c): "" for c in "!@#$%^&*()[]{};:,./<>?\|`'~-=_+ "}) #getting rid of special characters
    
                        #Propagation times
                        col = row.find_elements_by_css_selector("td:nth-child(14)")
                        propagation = col[0].text
                        if " s" in propagation:
                            df[NodeName] = int(propagation.replace("+","").replace(" s","").replace(".",""))*1000
                        elif " min" in propagation:
                            df[NodeName] = int(propagation.replace("+","").replace(" min","").replace(".",""))*1000*60
                        elif " h" in propagation:
                            df[NodeName] = int(propagation.replace("+","").replace(" h","").replace(".",""))*1000*60*60
                        else:
                            df[NodeName] = int(propagation.replace("+","").replace(" ms",""))
    
                lastBlock = currentBlock
                blockcounter +=1
                blockcounterTotal +=1
            
                #append dataframe to csv file
                df.to_csv(f, header = False, encoding='utf-8')

            #wait for new block
            time.sleep(0.2)
          
        #close browser and csv file and start loop over again
        driver.quit()
        f.close()
        
    except KeyboardInterrupt:
        print("you succesfully ended the program")
        driver.quit()
        f.close()
        break
    
    except Exception as e:
        print(e)
        #close browser and csv file and start loop over again
        f.close()
        driver.quit()

    
    


