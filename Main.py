import time
import os.path
from tkinter import *
from tkinter import filedialog
from tkinter.scrolledtext import ScrolledText
from tkinter.ttk import Combobox
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import *
from selenium.webdriver.common.action_chains import ActionChains
import SoilPrediction
from SoilPrediction import make_prediction
from PIL import ImageTk, Image  

plantSymbolsPath = './PlantSymbols.txt'
checkPlantSymbolsFile = os.path.isfile(plantSymbolsPath)

plantDataPath = './PlantData.csv'
checkPlantDataFile = os.path.isfile(plantDataPath)

global imageFilePath

#Webscrape the symbol for each plant from the USDA plant database and store it in the 'PlantSymbols.txt' file.
def getPlantSymbols():

    driver = webdriver.Chrome()
    driver.get("https://plants.usda.gov/home")

    delay = 10 # seconds
    try:
        WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.CLASS_NAME, 'navSpanLink')))
    except TimeoutException:
        print ("Loading took too much time!")

    characteristicsSearchButton = driver.find_element(By.CLASS_NAME,"navSpanLink")
    characteristicsSearchButton.click()
    
    #Wait at least 30 seconds for the output table to load
    WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CLASS_NAME, 'table')))
    
    #compile the symbols for each plant in the table

    plantSymbolsFile = open("PlantSymbols.txt", "w")

    tableRows = driver.find_elements(By.TAG_NAME,"tr")
    tableRows.pop(0)
    for row in tableRows:
        rowElements = row.find_elements(By.XPATH,".//*")
        plantSymbolsFile.write(rowElements[0].text+"\n")
        print(rowElements[0].text)

    for i in range(1,88):
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, "//a[@aria-label='Next']")))
        #time.sleep(2)
        nextPageButton = driver.find_element(By.XPATH, "//a[@aria-label='Next']")
        nextPageButton.click()
        #WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, "table")))
        time.sleep(7)

        tableRows = driver.find_elements(By.TAG_NAME,"tr")
        tableRows.pop(0)
        for row in tableRows:
            rowElements = row.find_elements(By.XPATH,".//*")
            plantSymbolsFile.write(rowElements[0].text+"\n")
            print(rowElements[0].text)
        

    plantSymbolsFile.close()
    #time.sleep(10)

    driver.close()

#Webscrape the data for each plant from the USDA plant database and store it in the 'PlantData.csv' file.
def getPlantData():
    #Use each plant symbol to go to the plant profile page
    plantSymbols = open("PlantSymbols.txt", "r")
    plantData = open("PlantData.csv","w")
    headerString = "plant symbol,plant scientific name,plant common name,native states (separated by '*'),duration,growth habit,growth period,growth rate,moisture use,adapted to coarse soil,adapted to fine soil,adapted to medium soil,drought tolerance,shade tolerance,temp min (°F),foliage color,flower conspicuous,flower color,bloom period\n"
    plantData.write(headerString)

    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")

    #driver = webdriver.Chrome(options=options)
    driver = webdriver.Chrome()

    fileCount = 0
    for line in plantSymbols.readlines():
        plantSymbol = line.strip()
        print("Checking data for: "+plantSymbol)
        driver.get("https://plants.usda.gov/home/plantProfile?symbol="+plantSymbol)
        
        
        try:
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'table')))
            time.sleep(2)

        except TimeoutException:
            print("took too long")

        
        #Only download plants that have both distribution data and the characteristics data available
    
        #Look for the Characteristics tab
        try:
          driver.find_element(By.ID, 'CharacteristicsTab')
        except NoSuchElementException:
           print("No characteristics data for: "+plantSymbol)
           continue

        #Look for the distribution data
        try:
            buttons = driver.find_elements(By.TAG_NAME, 'button')
            linkButton = buttons[2]
            actions = ActionChains(driver)
            actions.move_to_element_with_offset(linkButton,0,6)
            actions.click()
            actions.perform()
            time.sleep(1)
            downloadButton = driver.find_element(By.XPATH, "//a[@download='DistributionData.csv']")
            downloadButton.click()
            time.sleep(1.5)
        except NoSuchElementException:
           print("No distribution data for: "+plantSymbol)
           continue
        except MoveTargetOutOfBoundsException:
            print("Download was inaccesible for: "+plantSymbol)
            continue

        #time.sleep(2)


        #Open the downloaded distribution data file and puts its native states in the plant data csv
        fileNum = ""
        if(fileCount!=0):
            fileNum = " ("+str(fileCount)+")"
        #distributionDataFile = open("C:\\Users\\fireb\\Downloads\\DistributionData"+fileNum+".csv", "r")
        distributionDataFile = open("C:\\Users\\fireb\\Downloads\\DistributionData.csv", "r")
        distributionRows = distributionDataFile.readlines()
        distributionDataFile.close()
        os.remove("C:\\Users\\fireb\\Downloads\\DistributionData.csv")
        distributionRows.pop(0)
        distributionRows.pop(0)

        nativeStatesDuplicates = []
        for row in distributionRows:
            rowInfo = row.split(',')
            state = rowInfo[2]
            nativeStatesDuplicates.append(state)
            
        nativeStates = list(set(nativeStatesDuplicates))

        stateList = ""
        for state in nativeStates:
            stateList+=state+"*"
        
        closeButton = driver.find_element(By.CLASS_NAME,"close")
        closeButton.click()
        time.sleep(0.5)

        plantProfileHeader = driver.find_element(By.TAG_NAME,"plant-profile-header")
        h1 = plantProfileHeader.find_elements(By.XPATH,".//*")
        span = h1[0].find_elements(By.XPATH,".//*")
        spanChildren = span[0].find_elements(By.XPATH,".//*")
        plantScientificName = spanChildren[0].text

        durationRef = driver.find_element(By.XPATH,'//h6[text()="Duration:"]')
        durationRefParent = durationRef.find_element(By.XPATH,'..')
        durationRowRef = durationRefParent.find_element(By.XPATH,'..')
        durationRowChildren = durationRowRef.find_elements(By.XPATH,".//*")
        durationText = durationRowChildren[2].text
        durationList = durationText.split("\n")
        duration = ""
        for d in durationList:
            duration+=d.strip()+"*"

        growthHabitRef = driver.find_element(By.XPATH,'//h6[text()="Growth Habit:"]')
        growthHabitRefParent = growthHabitRef.find_element(By.XPATH,'..')
        growthHabitRowRef = growthHabitRefParent.find_element(By.XPATH,'..')
        growthHabitRowChildren = growthHabitRowRef.find_elements(By.XPATH,".//*")
        growthHabitText = growthHabitRowChildren[2].text
        habits = growthHabitText.split("\n")
        growthHabit = ""
        for habit in habits:
            growthHabit+= habit.strip() + "*"
        
        
        plantCommonName = ""
        try:
            plantCommonName = driver.find_element(By.CLASS_NAME,"text-muted").text
        except NoSuchElementException:
            #no common name
            print("No common name")

        

        #Go to the characteristics tab
        characteristicsTabButton = driver.find_element(By.ID, 'CharacteristicsTab')
        characteristicsTabButton.click()
        time.sleep(0.5)

        #Parse the characteristics data into the plant data csv
        try:
            tableBody1DataReference = driver.find_element(By.XPATH,'//td[text()="Active Growth Period"]')
            tableBody1RowReference = tableBody1DataReference.find_element(By.XPATH,"..")
            tableBody1Reference  = tableBody1RowReference.find_element(By.XPATH,"..")
            #Get rid of headers from table
            table1Rows = tableBody1Reference.find_elements(By.XPATH,".//*")
            table1Rows.pop(0)
            table1Rows.pop(0)
            #get table 1 data
            j = 0
            for row in table1Rows:
                #print(j)
                if (len(row.find_elements(By.XPATH,".//*"))>0):
                    rowChildren = row.find_elements(By.XPATH,".//*")
                    # print(rowChildren[0].text)
                    # print(rowChildren[1].text)
                    if(rowChildren[0].text == "Active Growth Period"):
                        cleaningString = rowChildren[1].text
                        cleanlist = cleaningString.split(",")
                        output=""
                        for i in cleanlist:
                            parts = i.split("and")
                            for part in parts:
                                output += part.strip() + "*"
                        growthPeriod = output
                        #growthPeriod = rowChildren[1].text
                    if(rowChildren[0].text == "Growth Rate"):
                        growthRate = rowChildren[1].text
                    if(rowChildren[0].text == "Flower Color"):
                        flowerColor = rowChildren[1].text
                    if(rowChildren[0].text == "Foliage Color"):
                        foliageColor = rowChildren[1].text
                    if(rowChildren[0].text == "Flower Conspicuous"):
                        flowerConspicuous = rowChildren[1].text
            j+=1
        except NoSuchElementException:
            print("Missing data from table 1")
            growthPeriod = "NA"
            growthRate = "NA"
            flowerColor = "NA"
            foliageColor = "NA"
            flowerConspicuous = "NA"
        
        try:
            tableBody2DataReference = driver.find_element(By.XPATH,'//td[text()="Adapted to Coarse Textured Soils"]')
            tableBody2RowReference = tableBody2DataReference.find_element(By.XPATH,"..")
            tableBody2Reference  = tableBody2RowReference.find_element(By.XPATH,"..")
            #Get rid of headers from table
            table2Rows = tableBody2Reference.find_elements(By.XPATH,".//*")
            table2Rows.pop(0)
            table2Rows.pop(0)
            #get table 2 data
            i = 0
            for row in table2Rows:
                #print(i)
                if (len(row.find_elements(By.XPATH,".//*"))>0):
                    rowChildren = row.find_elements(By.XPATH,".//*")
                    #print(rowChildren[0].text)
                    #print(rowChildren[1].text)
                    if(rowChildren[0].text == "Adapted to Coarse Textured Soils"):
                        coarseSoil = rowChildren[1].text
                    if(rowChildren[0].text == "Adapted to Fine Textured Soils"):
                        fineSoil = rowChildren[1].text
                    if(rowChildren[0].text == "Adapted to Medium Textured Soils"):
                        medSoil = rowChildren[1].text
                    if(rowChildren[0].text == "Drought Tolerance"):
                        droughtTolerance = rowChildren[1].text
                    if(rowChildren[0].text == "Shade Tolerance"):
                        shadeTolerance = rowChildren[1].text
                    if(rowChildren[0].text == "Moisture Use"):
                        moistureUse = rowChildren[1].text
                    if(rowChildren[0].text == "Temperature, Minimum (°F)"):
                        tempMin = rowChildren[1].text
            i+=1

        except NoSuchElementException:
            print("Missing data from table 2")
            coarseSoil = "NA"
            fineSoil = "NA"
            medSoil = "NA"
            droughtTolerance = "NA"
            shadeTolerance = "NA"
            moistureUse = "NA"
            tempMin = "NA"

        try: 
            tableBody3DataReference = driver.find_element(By.XPATH,'//td[text()="Bloom Period"]')
            tableBody3RowReference = tableBody3DataReference.find_element(By.XPATH,"..")
            tableBody3Reference  = tableBody3RowReference.find_element(By.XPATH,"..")
             #Get rid of headers from tables
            table3Rows = tableBody3Reference.find_elements(By.XPATH,".//*")
            table3Rows.pop(0)
            table3Rows.pop(0)
            #get table 3 data
            z = 0
            for row in table3Rows:
                #print(j)
                if (len(row.find_elements(By.XPATH,".//*"))>0):
                    rowChildren = row.find_elements(By.XPATH,".//*")
                    # print(rowChildren[0].text)
                    # print(rowChildren[1].text)
                    if(rowChildren[0].text == "Bloom Period"):
                        bloomPeriod = rowChildren[1].text
            z+=1
        except NoSuchElementException:
            print("Missing data from table 3")
            bloomPeriod = "NA"
       
        # CSV FORMAT: plant symbol, plant scientific name, plant common name, native states (separated by '*'), duration, growth habit, growth period, growth rate, moisture use, adapted to coarse soil, adapted to fine soil, adapted to medium soil, drought tolerance, shade tolerance, temp min (°F), foliage color, flower conspicuous, flower color, bloom period
        outputString = plantSymbol+","+plantScientificName+","+plantCommonName+","+stateList+","+duration+","+growthHabit+","+growthPeriod+","+growthRate+","+moistureUse+","+coarseSoil+","+fineSoil+","+medSoil+","+droughtTolerance+","+shadeTolerance+","+tempMin+","+foliageColor+","+flowerConspicuous+","+flowerColor+","+bloomPeriod+"\n"
        print(outputString)
        plantData.write(outputString)
        #print("Data retrieved for: " + plantScientificName + " / " + plantCommonName)
        print("Data retrieved for: "+plantSymbol+". "+str(fileCount+1)+" out of 2268 downloaded")
        fileCount+=1

    plantData.close()

#Get the plant symbols if they are not already present
if(checkPlantSymbolsFile==False):
    getPlantSymbols()

#Get the plant data if it is not already present
if(checkPlantDataFile==False):
    getPlantData()

#Read the 'PlantData.csv' file into 2 maps: State Search Map (key->State, value->List of Plant Names) and Plant Search Map (key->Plant Name, value->Plant Data) 
def readInPlantData():
    #print("Reading 'PlantData.csv'...")
    plantDataFile = open("PlantData.csv","r")
    plantDataRows = plantDataFile.readlines()
    plantDataRows.pop(0)
    dictList = []

    stateSearch = dict(State = [])
    plantSearch = dict(Symbol = [])

    dictList.append(stateSearch)
    dictList.append(plantSearch)

    for row in plantDataRows:
        dataList = row.strip().split(",")
        plantSymbol = dataList[0]
        plantScientificName = dataList[1]
        plantCommonName = dataList[2]
        nativeStatesList = dataList[3].split("*")
        nativeStatesList.pop(-1)
        nslString = ", ".join(nativeStatesList)
        durationList = dataList[4].split("*")
        durationList.pop(-1)
        dlString = ", ".join(durationList)
        growthHabitList = dataList[5].split("*")
        growthHabitList.pop(-1)
        ghlString = ", ".join(growthHabitList)
        growthPeriodList = dataList[6].split("*")
        growthPeriodList.pop(-1)
        gplString = ", ".join(growthPeriodList)
        growthRate = dataList[7]
        moistureUse = dataList[8]
        coarseSoil = dataList[9]
        fineSoil = dataList[10]
        medSoil = dataList[11]
        droughtTolerance = dataList[12]
        shadeTolerance = dataList[13]
        minTemp = dataList[14]
        foliageColor = dataList[15]
        flowerConspicuous = dataList[16]
        flowerColor = dataList[17]
        bloomPeriod = dataList[18]

        # print("_______"+plantCommonName+"_______")
        # print("Native States: "+nslString)
        # print("Duration: "+dlString)
        # print("Growth Habit: "+ghlString)
        # print("Growth Period: "+gplString) 
        # print("Growth Rate: "+growthRate)
        # print("Moisture Use: "+moistureUse)
        # print("Coarse Soil: "+coarseSoil)
        # print("Fine Soil: "+fineSoil)
        # print("Medium Soil: "+medSoil)
        # print("Drought Tolerance: "+droughtTolerance)
        # print("Shade Tolerance: "+shadeTolerance)
        # print("Min Temp (F): "+minTemp)
        # print("Foliage Color: "+foliageColor)
        # print("Flower Conspicuous: "+flowerConspicuous)
        # print("Flower Color: "+flowerColor)
        # print("Bloom Period: "+bloomPeriod)
        
        #Put the plant in the state dictionary
        for state in nativeStatesList:
            if state in stateSearch.keys():
                stateSearch[state].append(plantSymbol)
            else:
                stateSearch[state] = [plantSymbol]

        #Put the plant in the plant dictionary
        plantSearch[plantSymbol] = dataList

    return dictList

dictList = readInPlantData()
stateDict = dictList[0]
plantDict = dictList[1]

def recommendPlants(state):
    plantCodeList = list(set(stateDict[state]))
    
    plants = []
    for plant in plantCodeList:
        plantData = plantDict[plant]
        #if plantData[17] == "Purple":
        plants.append(plantData[0]+" - "+plantData[1] +" / "+plantData[2])
    return plants

def displaySearch(listArea,input,durationVal,growthHabitVal,flowerColorVal,flowerConspicuousVal):
    plantList = recommendPlants(input)
    listArea.delete(0,"end")
    print("Found "+str(len(plantList))+" results")
    i = 1
    for plant in plantList:
        plantCode = plant.split(" - ")[0]
        plantInfo = plantDict[plantCode]
        #check the "duration", "growth habit", "flower color", and "flower conspicuous" values to see if they match the filter values
        if(durationVal!=""):
           durationList = plantInfo[4].split("*")
           if(not durationVal in durationList):
               continue
        if(growthHabitVal!=""):
           growthHabitList = plantInfo[5].split("*")
           if(not growthHabitVal in growthHabitList):
               continue
        if(flowerColorVal!=""):
            if(flowerColorVal!=plantInfo[17]):
                continue
        if(flowerConspicuousVal!=""):
            if(flowerConspicuousVal!=plantInfo[16]):
                continue
        listArea.insert(i,plant)
        i+=1
    # print(input)
    # print(durationVal)
    # print(growthHabitVal)
    # print(flowerColorVal)
    # print(flowerConspicuousVal)

def displayPlantInfo(selection,plantProfileSection,plantList):
    plantProfileSection.configure(state=NORMAL)
    plantProfileSection.delete(0,"end")
    for i in selection:
        selectedPlantRow = plantList.get(i)
        selectedPlant = selectedPlantRow.split(" - ")[0]
    
    plantInfo = plantDict[selectedPlant]

    plantProfileSection.insert(1,"Scientific Name: "+plantInfo[1])
    plantProfileSection.insert(2,"Common Name: "+plantInfo[2])
    plantProfileSection.insert(3,"")

    durationList = plantInfo[4].split("*")
    durationList.pop(-1)
    dlString = ", ".join(durationList)
    plantProfileSection.insert(4,"Duration: "+dlString)
    growthHabitList = plantInfo[5].split("*")
    growthHabitList.pop(-1)
    ghlString = ", ".join(growthHabitList)
    plantProfileSection.insert(5,"Growth Habit: "+ghlString)
    growthPeriodList = plantInfo[6].split("*")
    growthPeriodList.pop(-1)
    gplString = ", ".join(growthPeriodList)
    plantProfileSection.insert(6,"Growth Period: "+gplString)
    plantProfileSection.insert(7,"Growth Rate: "+plantInfo[7])
    plantProfileSection.insert(8,"")

    plantProfileSection.insert(9,"Moisture Usage: "+plantInfo[8])
    plantProfileSection.insert(10,"Adapted to Coarse Soil: "+plantInfo[9])
    plantProfileSection.insert(11,"Adapted to Fine Soil: "+plantInfo[10])
    plantProfileSection.insert(12,"Adapted to Medium Soil: "+plantInfo[11])
    plantProfileSection.insert(13,"Drought Tolerance: "+plantInfo[12])
    plantProfileSection.insert(14,"Shade Tolerance: "+plantInfo[13])
    plantProfileSection.insert(15,"Min Temp(F): "+plantInfo[14])
    plantProfileSection.insert(16,"")
    plantProfileSection.insert(17,"Foliage Color: "+plantInfo[15])
    plantProfileSection.insert(18,"Flower Conspicuous: "+plantInfo[16])
    plantProfileSection.insert(19,"Flower Color: "+plantInfo[17])
    plantProfileSection.insert(20,"Bloom Period: "+plantInfo[18])

def openFile(imageLabel):
    filePath = filedialog.askopenfilename()
    global imageFilePath
    imageFilePath=filePath

    #Set the image label widget to the seleted image
    image = Image.open(filePath)
    soilImage = ImageTk.PhotoImage(image)

    imageLabel.configure(image = soilImage)
    imageLabel.image = soilImage\
    
def displayPrediction(outputLabel):    
    outputText = make_prediction(imageFilePath)
    #print(make_prediction(inputImageFilePath))
    outputLabel.configure(text=outputText)

def clear_frame():
   for widgets in root.winfo_children():
      widgets.destroy()

def displayMainMenu():
    clear_frame()
    # mainMenu = Frame(root)
    # mainMenu.pack()
    #root.wm_attributes('-transparentcolor', '#ab23ff')
    topBarFrame = Frame(root,bg="#474A2C")
    topBarFrame.grid(row=0,column=0,sticky=EW,pady=(0,40))
    topBarFrame.grid_columnconfigure(0, weight=1)

    titleText = Label(topBarFrame, text="P.L.A.N.T.S",bg="#474A2C",font=('Aerial 20 bold italic'),fg="#F8FCDA")
    titleText.grid(row=0,column=0)

    subTitleText = Label(topBarFrame, text="Plant Location Analysis and Niche Terrestrial Soil",bg="#474A2C",font=('Aerial 10'),fg="white")
    subTitleText.grid(row=1,column=0,pady=(0,10))

    plantSearchScreenButton = Button(root, text="Plant Search", command = lambda:displayPlantSearchScreen())
    plantSearchScreenButton.grid(row = 2 ,column= 0,pady=(40,20))

    soilPredictionScreenButton = Button(root, text="Soil Prediction", command = lambda:displaySoilPredictionScreen())
    soilPredictionScreenButton.grid(row = 3 ,column= 0 )

def displayPlantSearchScreen():
    clear_frame()

    #titleSectionFrame = Frame(root,bg="coral",width=100,height=100)
    #COL 0
    
    # titleAreaFrame = Frame(root,bg="coral",width=100,height=100)
    # titleAreaFrame.grid(row = 0, column=0)
    topBarFrame = Frame(root,background='#474A2C')
    topBarFrame.grid(row=0,column=0,sticky=EW)
    topBarFrame.grid_columnconfigure(0, weight=1)


    mainMenuBtn = Button(topBarFrame, text="Main Menu",command = lambda:displayMainMenu())
    mainMenuBtn.grid(row=0,column=0,sticky=W,padx=10,pady=(10,0))
    
    titleText = Label(topBarFrame, text="Plant Search",bg="#474A2C",font=('Aerial 20 bold italic'),fg="#F8FCDA")
    titleText.grid(row=1,column=0)

    explanationText = Label(topBarFrame, text="Enter a state to get a list of recommended plants",bg="#474A2C",font=('Aerial 10'),fg="white")
    explanationText.grid(row = 2, column = 0,pady=(0,5))

    contentFrame = Frame(root,bg="#646F4B")
    contentFrame.grid(row=1,column=0,sticky=N,pady=(30,0))
    
    contentFrame.grid_rowconfigure(0, weight=1)
    contentFrame.grid_columnconfigure(0, weight=1)

    searchFrame = Frame(contentFrame,bg="#646F4B",width=100,height=100)
    searchFrame.grid(row = 2, column=0,pady=(0,30))
    entry = Entry(searchFrame)
    entry.insert(0,"Search")
    entry.grid(row = 0, column = 0,padx=10)

    #when the search button is clicked, add the recommended plants to the output list area
    btn = Button(searchFrame, text="Search",command = lambda:displaySearch(listArea,entry.get(),durationDropdown.get(),growthHabitDropdown.get(),flowerColorDropdown.get(),flowerConspicuousDropdown.get()))
    btn.grid(row = 0, column = 1)

    filterFrame = Frame(contentFrame,bg="#646F4B")
    filterFrame.grid(row = 3, column = 0,pady=(0,50),sticky=EW)

    durationFrame = Frame(filterFrame,bg="#646F4B")
    durationFrame.grid(row=0,column=0)
    durationText = Label(durationFrame, text="Duration:",bg="#646F4B",font="bold",fg="#F8FCDA")
    durationText.grid(row = 0, column= 0)
    durationDropdown = Combobox(durationFrame,state="readonly",values=["Perennial","Biennial","Annual"])
    durationDropdown.grid(row=1, column= 0)

    growthHabitFrame = Frame(filterFrame,bg="#646F4B",padx=20)
    growthHabitFrame.grid(row=0,column=1)
    growthHabitText = Label(growthHabitFrame, text="Growth Habit:",bg="#646F4B",font="bold",fg="#F8FCDA")
    growthHabitText.grid(row = 0, column= 0)
    growthHabitDropdown = Combobox(growthHabitFrame,state="readonly",values=["Forb/herb","Graminoid","Lichenous","Nonvascular","Shrub","Subshrub","Tree","Vine"])
    growthHabitDropdown.grid(row = 1, column= 0)

    flowerColorFrame = Frame(filterFrame,bg="#646F4B",padx=20)
    flowerColorFrame.grid(row=0,column=2)
    flowerColorText = Label(flowerColorFrame, text="Flower Color:",bg="#646F4B",font="bold",fg="#F8FCDA")
    flowerColorText.grid(row = 0, column= 0)
    flowerColorDropdown = Combobox(flowerColorFrame,state="readonly",values=["Blue","Brown","Green","Orange","Purple","Red","White","Yellow"])
    flowerColorDropdown.grid(row = 1, column= 0)

    flowerConFrame = Frame(filterFrame,bg="#646F4B",padx=20)
    flowerConFrame.grid(row=0,column=3)
    flowerConspicuousText = Label(flowerConFrame, text="Flower Conspicuous:",bg="#646F4B",font="bold",fg="#F8FCDA")
    flowerConspicuousText.grid(row = 0, column= 0)
    flowerConspicuousDropdown = Combobox(flowerConFrame,state="readonly",values=["Yes","No"])
    flowerConspicuousDropdown.grid(row = 1, column= 0)

    outputFrame = Frame(contentFrame,bg="#646F4B")
    outputFrame.grid(row=4,column=0)

    listArea = Listbox(outputFrame,height=20,width=60,background="#E3E9C2",selectforeground="black",selectbackground="white")
    listArea.grid(row = 0, column = 0)

    #when the Get Info button is clicked, add the plant data to the plant profile section
    btn2 = Button(outputFrame, text="Get Info",command = lambda:displayPlantInfo(listArea.curselection(),plantInfoSection,listArea))
    btn2.grid(row = 0, column = 1,padx=10)

    # # plantProfileSection = Listbox(root,height=20,width=60,background="coral",borderwidth=0, highlightthickness=0,font=('Aerial 13'),fg="black")
    # # plantProfileSection.configure(state=DISABLED)
    plantInfoSection = Listbox(outputFrame,height=20,width=60,background="#E3E9C2",borderwidth=0, highlightthickness=0,fg="black",activestyle='none',selectforeground="black",selectbackground="#E3E9C2")
    plantInfoSection.grid(row = 0, column = 3)
    
    plantInfoSection.insert(1,"Scientific Name: ")
    plantInfoSection.insert(2,"Common Name: ")

    plantInfoSection.insert(3,"") 

    plantInfoSection.insert(4,"Duration: ")
    plantInfoSection.insert(5,"Growth Habit: ")
    plantInfoSection.insert(6,"Growth Period: ")
    plantInfoSection.insert(7,"Growth Rate: ")
    plantInfoSection.insert(8,"")


    plantInfoSection.insert(9,"Moisture Usage: ")
    plantInfoSection.insert(10,"Adapted to Coarse Soil: ")
    plantInfoSection.insert(11,"Adapted to Fine Soil: ")
    plantInfoSection.insert(12,"Adapted to Medium Soil: ")
    plantInfoSection.insert(13,"Drought Tolerance: ")
    plantInfoSection.insert(14,"Shade Tolerance: ")
    plantInfoSection.insert(15,"Min Temp(F): ")
    plantInfoSection.insert(16,"")


    plantInfoSection.insert(17,"Foliage Color: ")
    plantInfoSection.insert(18,"Flower Conspicuous: ")
    plantInfoSection.insert(19,"Flower Color: ")
    plantInfoSection.insert(20,"Bloom Period: ")

def displaySoilPredictionScreen():
    clear_frame()
    
    topBarFrame = Frame(root,background='#474A2C')
    topBarFrame.grid(row=0,column=0,sticky=EW)
    topBarFrame.grid_columnconfigure(0, weight=1)

    mainMenuBtn = Button(topBarFrame, text="Main Menu",command = lambda:displayMainMenu())
    mainMenuBtn.grid(row=0,column=0,sticky=W,padx=10,pady=10)

    titleText = Label(topBarFrame, text="Soil Prediction",bg="#474A2C",font=('Aerial 20 bold italic'),fg="#F8FCDA")
    titleText.grid(row=1,column=0)

    subTitleText = Label(topBarFrame, text="Select a photo of soil to predict its content",bg="#474A2C",font=('Aerial 10'),fg="white")
    subTitleText.grid(row=2,column=0)

    contentFrame = Frame(root,bg="#646F4B")
    contentFrame.grid(row=1,column=0,sticky=N)
    contentFrame.grid_rowconfigure(0, weight=1)
    contentFrame.grid_columnconfigure(0, weight=1)


    controlFrame = Frame(contentFrame,bg="#646F4B")
    controlFrame.grid(row=2,column=0)

    btnFrame = Frame(controlFrame,bg="#646F4B")
    btnFrame.grid(row=0,column=0,pady=(30,0))

    fileBtn = Button(btnFrame, text="Open Image File",command = lambda:openFile(imageLabel))
    fileBtn.grid(row=0,column=0,padx=(0,5))

    predictBtn = Button(btnFrame, text="Predict Soil Type",command = lambda:displayPrediction(outputLabel))
    predictBtn.grid(row=0,column=1,padx=(5,0))

    
    outputLabel = Label(controlFrame,text="Predicted Soil Type: ",bg="#646F4B",font='Aerial 12',fg="#F8FCDA")
    outputLabel.grid(row=1,column=0,padx=30)


    imageLabel = Label(contentFrame,bg="#646F4B")
    imageLabel.grid(row=3,column=0)

    

#TODO: Write a function to generate overview text for a given soil type
def generateSoilOverviewText(soilType):
    print("Soil Overview:")

#Main Menu Window
root = Tk()
root.title("P.L.A.N.T.S")
root.configure(bg="#646F4B")
root.minsize(1000, 700)# width, height
root.geometry("1000x700")
root.grid_columnconfigure(0, weight=1)

displayMainMenu()

root.mainloop()


    



