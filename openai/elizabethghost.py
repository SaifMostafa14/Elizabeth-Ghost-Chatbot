from openai import OpenAI
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import csv

client = OpenAI()

def webscraping(keyword):
    # Set up the Selenium webdriver (you'll need to download and install the appropriate webdriver for your browser)

    chrome_path = '/usr/local/bin/chromedriver'
    service = Service(executable_path=chrome_path)
    service.start()

    driver = webdriver.Chrome(service=service)

    # Navigate to the URL
    url = "https://stetson.on.worldcat.org/search?queryPrefix=kw%3A&queryString=kw%3A"+ keyword+ "&scope=wz%3A4369&expandSearch=off&translateSearch=off"
    driver.get(url)

    wait = WebDriverWait(driver, 60)  # Maximum wait time in seconds

    book_list_Xpath = '//*[@id="dui-main-content-area"]/div/div/div/div/div[2]/div/div[1]/ul'
    book_list_element = wait.until(EC.presence_of_element_located((By.XPATH, book_list_Xpath)))

    # Extract information from the web page
    books = book_list_element.find_elements(By.TAG_NAME, "li")
    
    # Write data to a CSV file
    with open('search.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Title", "Author", "Summary", "Location"])

        for i in range(1,6):
            for book in books:
                title_element = book.find_element(By.XPATH, '//*[@id="dui-main-content-area"]/div/div/div/div/div[2]/div/div[1]/ul/li['+str(i)+']/div/div/div[1]/div[2]/div/div[3]/div/h1/div/div/span/a')
                title = title_element.text.strip()

                author_element = book.find_element(By.XPATH, '//*[@id="dui-main-content-area"]/div/div/div/div/div[2]/div/div[1]/ul/li['+str(i)+']/div/div/div[1]/div[2]/div/div[3]/div/div[1]/div/div')
                author = author_element.text.strip()

                summary_element = book.find_element(By.XPATH, '//*[@id="dui-main-content-area"]/div/div/div/div/div[2]/div/div[1]/ul/li['+str(i)+']/div/div/div[1]/div[2]/div/div[3]/div/div[3]')
                summary = summary_element.text.strip()

                available_element = book.find_element(By.XPATH, '//*[@id="dui-main-content-area"]/div/div/div/div/div[2]/div/div[1]/ul/li['+str(i)+']/div/div/div[1]/div[2]/div/div[3]/div/div[7]')
                available = available_element.text.strip()


            writer.writerow([title, author, summary, available])

    driver.quit()




#openai.api_key = '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'

prompt = """

Greet the user and ask them how you can help them today

"""

response = client.completions.create(model="gpt-3.5-turbo-instruct", prompt=prompt , temperature=0, max_tokens=200)
#print(response)

# Extract the classification from the API response
completion_text = response.choices[0].text.strip().lower()
print(completion_text)

query = ""
while query != "stop":
    query = input("Q: ")
    if query == "stop":
        break

    prompt = """

	Extract the intent of the user input based on the following classifications: 

	- Book search: The user wants to find or is looking for a specific book or books on a particular topic. Example query: "Do you have any books on machine learning?", or "I am looking for books or articles on philosophy"
	- Reserve a study space: The user wants to reserve a space in the library to study or work or just inquiring about a study spaces. Example query: "Can I reserve a study room for tomorrow?"
	- Library hours: The user is asking about the library's hours of operation. Example query: "What time does the library close today?"
	- Checkout inquiry: The user has a question about checking out a book or other library material. Example query: "How long can I keep this book checked out?"
    - Books classification: The user is asking about the location of a collection of books. Example query: "Where can I find books about American History" 

	If you can't classify it into any of the categories, use "fallback" as the classification.
    query = %s
    """

    response = client.completions.create(model="gpt-3.5-turbo-instruct", prompt=prompt % query, temperature=0, max_tokens=200)
    #print(response)

    # Extract the classification from the API response
    completion_text = response.choices[0].text.strip().lower()
    classification = completion_text.split(':')[-1].strip()

    # Handle each classification with if and else statements
    if classification == "book search":
        print("Handling 'book search' classification...")
        # Add your code here to handle this classification
        prompt = """
        Reply to the user saying that your understanding is that they are searching for a book or whatever they want and ask them to give you just a keyword about what they want to search for so that you can help them find it. Helpful keywords can be either the title, the author, or subject.

        query = %s
        """
        response = client.completions.create(model="gpt-3.5-turbo-instruct", prompt=prompt % query, temperature=0, max_tokens=200)
        #print(response)
    
        completion_text = response.choices[0].text.strip().lower()
        respo = completion_text.split(':')[-1].strip()
        print(respo)
        #if respo == "null":

        #prompt = """
        #Ask the user to enter the title or the author or any keyword for what they are looking for. 

        #query = %s
        #"""
        #response = openai.Completion.create(model="text-davinci-003", prompt=prompt % query, temperature=0, max_tokens=200)
        #print(response.choices[0].text.strip().lower())

        query = input(": ")
        prompt = """
        Extract the user response. Your extraction should be exactly what the user writes.

        query = %s
        """
        response = client.completions.create(model="gpt-3.5-turbo-instruct", prompt=prompt % query, temperature=0, max_tokens=200)
        #print(response)

        completion_text = response.choices[0].text.strip().lower()
        respo = completion_text.split(':')[-1].strip()
        respo = respo.replace('"', '')
        print(respo)

        #try:
        webscraping(respo)
        #except:
        #   print("I apologize but I couldn't perform that search")
        #    break
        file_address = "search.csv"
        with open(file_address, newline='') as csvfile: 
            reader = csv.reader(csvfile, delimiter=',')
            content = ""
            for row in reader: 
                content = content + ', '.join(row)


        prompt = f"""
        tell the user these are the results we found based on the library database search. Extract the Titles and Authors that are in:{content}

        provide the response in the following format and iterate the number:
        1- Title + "by" + Author

        query = %s
        """
        response = client.completions.create(model="gpt-3.5-turbo-instruct", prompt=prompt % query, temperature=0, max_tokens=200)
        #print(response)

        completion_text = response.choices[0].text.strip().lower()
        print(completion_text)
    
    #while query != "stop":
        #prompt = """
	    #Use the following file contents to provide a list of titles from the file:\n{file_content}. Only use the contents in this file.

	    #query= %s
	    #"""	
        #response = openai.Completion.create(model="text-davinci-003", prompt=prompt % query, temperature=0, max_tokens=200)
        #print(response)
     
        #completion_text = response.choices[0].text.strip().lower()
        #respo = completion_text.split(':')[-1].strip()
        #query = input(": ")

        prompt = """
        ask the user if they found what they are looking for or if they need more information about a certain book from the list 

        query = %s
        """
        response = client.completions.create(model="gpt-3.5-turbo-instruct", prompt=prompt % query, temperature=0, max_tokens=200)
        #print(response)

        completion_text = response.choices[0].text.strip().lower()
        print(completion_text)

        query = input(": ")
        prompt = """
        If the user answer yes or something similar say awesome I am glad I could help. 

        If they said something else, extract the book title and search on it in: {content} and answer the question based on the information you find

        If you can't find what the user said say "I don't know how to further help you"

        query = %s
        """

        response = client.completions.create(model="gpt-3.5-turbo-instruct", prompt=prompt % query, temperature=0, max_tokens=200)
        # Extract the classification from the API response
        completion_text = response.choices[0].text.strip().lower()
        respo = completion_text.split(':')[-1].strip()
        print(respo) 

    elif classification == "reserve a study space":
        print("Handling 'reserve a study space' classification...")
    # Add your code here to handle this classification
        prompt = """
        Answer the question using the following information. Rephrase your answer to be direct to the question and If you don't know the answer tell them that you don't know 


Study Rooms
Taylor Study Room with Large Monitor and WhiteboardThe Alpha, Beta, and Gamma rooms are the three small study rooms with a whiteboard and seating for four.

The Taylor Room is the large study room with collaboration station, white board, and seating for six.

We strongly recommend that you reserve Study Rooms 24 hours in advance. Study room reservations are limited to current Stetson students, staff, and faculty.

To reserve a study room go to this link: https://stetson.libcal.com/reserve/StudyRooms

	query = %s
	"""
     
        response = client.completions.create(model="gpt-3.5-turbo-instruct", prompt=prompt % query, temperature=0, max_tokens=1000)
        #print(respons)
     
        completion_text = response.choices[0].text.strip().lower()
        print(completion_text)
     

    elif classification == "library hours":
        print("Handling 'library hours' classification...")
        # Add your code here to handle this classification
        prompt = """
        Answer the question as truthfully as possible using the provided text, and if the answer is not contained within the text below, say "I don't know". Rephrase the answer so that it is a direct response to the question.

	Hours of Operation,
	DAYS,HOURS
	Monday to Thursday,8 AM – 12 AM (midnight)
	Friday,8 AM – 6 PM
	Saturday,10 AM – 6 PM
	Sunday,11 AM – 12 AM (midnight)
	"Research assistance hours differ from the building operating hours. For research assistance business hours, see Ask A Librarian. ",
	,
	Special Openings & Closings,
	DATE,SPECIAL HOURS,
	"Sunday, 11 December to Tuesday, 20 December", Intersession Hours
	,Mon – Fri: 8 AM to 5 PM
	,Sat – Sun: CLOSED
	"Monday, 12 December",Library Staff Retreat
	,CLOSED 12 PM to 1:30 PM
	"Wednesday, 21 December to Monday, 2 January",University Holiday
	,CLOSED
	"Tuesday, 3 January to Saturday, 7 January",Intersession Hours
	,Mon – Fri: 8 AM to 5 PM
	,Sat – Sun: CLOSED
	"Sunday, 8 January",Spring Hours Begin
	,Mon – Thur: 8 AM to 12 AM
	,Fri: 8 AM to 6 PM
	,Sat: 10 AM to 6 PM
	,Sun: 11 AM to 12 AM
	"Monday, 16 January",Martin Luther King Day
	,5 PM to 12 AM
	"Saturday, 25 February to Saturday, 4 March",Spring Break – Intersession Hours
	,Mon – Fri: 8 AM to 5 PM
	,Sat – Sun: CLOSED
	"Friday, 7 April",University Holiday
	,CLOSED
	"Thursday, 27 April to Tuesday, 2 May",Extended Hours for Finals
	,Mon – Fri: 8 AM to 12 AM
	,Sat – Sun: 10 AM to 12 AM
	"Wednesday, 3 May to Saturday, 13 May",Intersession Hours
	,Mon – Fri: 8 AM to 5 PM
	,Sat – Sun: CLOSED
	"Sunday, 14 May",Summer Hours Begin
	,Mon – Fri: 8 AM to 8 PM
	,Sat: 10 AM to 6 PM
	,Sun: 11 AM to 8 PM        


    The Writing Center hours are as follows: 
	Monday - Thursday: Noon - 10 p.m.
	Friday: Noon - 3 p.m.
	Sunday: 3 - 6 p.m.

		query = %s
		"""
		
        response = client.completions.create(model="gpt-3.5-turbo-instruct", prompt=prompt % query, temperature=0, max_tokens=1000)
        #print(response)

        completion_text = response.choices[0].text.strip().lower()
        print(completion_text) 

###########################################################################
    elif classification == "checkout inquiry":
        print("Handling 'checkout inquiry' classification...")
    # Add your code here to handle this classification 
       #prompt = """
       # tell the user that you understand they are inquiring about a library checkout and Ask the user what         kind of item they want to checkout from the following items: 
       # BOOKS AND GOVERNMENT DOCS
       # DVDS
       # RESERVE MATERIALS
       # SCORES
       # RECITAL CDS
       # HEADPHONES
       # LAPTOPS
       # TABLETS
       # CDS AND RECORDS

       # query = %s
       # """

       # response = openai.Completion.create(model="text-davinci-003", prompt=prompt % query, temperature=0, max_tokens=1000)
       # print(response)
       # completion_text = response.choices[0].text.strip().lower()
       # print(completion_text) 
       # query = input(": ")

       # prompt = """
       # Extract the item from the user response. Only have the item as your response.
        
       # query = %s
       # """
       # response = openai.Completion.create(model="text-davinci-003", prompt=prompt % query, temperature=0, max_tokens=1000)
       # print(response)
       # completion_text = response.choices[0].text.strip().lower()
       # print(completion_text) 
       # item_requested = completion_text

        #TODO try and extract the relation and the item from the user message first
        relation = "not valid"
        while relation == "not valid":
            prompt = """
            tell the user that you understand that they are trying to inquire about a checkout and tell them to choose on of the following relations: student, faculty, staff, or associate in order to help them

            query = %s
            """
        
            response = client.completions.create(model="gpt-3.5-turbo-instruct", prompt=prompt % query, temperature=0, max_tokens=1000)
            #print(response)
            completion_text = response.choices[0].text.strip().lower()
            print(completion_text) 
            query = input(": ")
    

            prompt = """
            Check the user response and extract just their relation to the library and sort it into one of the following: student, faculty, staff, associate, or not valid. Overlook typos and only have the relation as your response

            query: %s
            """
            response = client.completions.create(model="gpt-3.5-turbo-instruct", prompt=prompt % query, temperature=0, max_tokens=1000)
            #print(response)
            completion_text = response.choices[0].text.strip().lower()
            respo = completion_text.split(':')[-1].strip()
            print(respo)
            relation = respo


        prompt = """
        Tell the user that you get that they are {relation}. and ask the user what kind of item they want to checkout and give them the following options numbered starting from 1:
        BOOKS AND GOVERNMENT DOCS
        DVDS
        RESERVE MATERIALS
        SCORES
        RECITAL CDS
        HEADPHONES
        LAPTOPS
        TABLETS
        CDS AND RECORDS

        query = %s
        """

        response = client.completions.create(model="gpt-3.5-turbo-instruct", prompt=prompt % query, temperature=0, max_tokens=1000)
        #print(response)
        completion_text = response.choices[0].text.strip().lower()
        print(completion_text) 
        query = input(": ")

        prompt = """
        Extract the item from the user response. Only have the item as your response. and sort it into one of the following: BOOKS AND GOVERNMENT DOCS, DVDS, RESERVE MATERIALS, SCORES, RECITAL CDS, HEADPHONES, LAPTOPS, TABLETS, CDS AND RECORDS, or others
        
        query = %s
        """
        response = client.completions.create(model="gpt-3.5-turbo-instruct", prompt=prompt % query, temperature=0, max_tokens=1000)
        #print(response)
        completion_text = response.choices[0].text.strip().lower()
        print(completion_text) 
        item_requested = completion_text

        if relation == "student":

            prompt = """
            Use the extraced item and provide a response with the information associated with the item using the following information. Provide a response only on the extracted item.

        MEDIA,CHECKOUT,NUMBER OF RENEWALS
		BOOKS AND GOVERNMENT DOCS,28 DAYS,2 renewals
		DVDS,7 DAYS,2 renewals
		RESERVE MATERIALS,2  HRS IN LIBRARY OR 24 HRS,1 renewal
		SCORES,28 DAYS,2 renewals
		RECITAL CDS,"2 HRS, IN LIBRARY",1 renewal 
		HEADPHONES,2 HRS,1 renewal
		LAPTOPS,1 DAY OR 4 HRS,1 renewal 
		TABLETS,7 DAYS,1 renewal 
		CDS AND RECORDS,7 DAYS,2 renewals
        
		If the item is anything else say we either don't have that item or that we don't offer that item for checkout 

		    query = %s
            """

            response = client.completions.create(model="gpt-3.5-turbo-instruct", prompt=prompt % query, temperature=0, max_tokens=1000)
            #print(response)
            completion_text = response.choices[0].text.strip().lower()
            print(completion_text)

        if relation == "faculty":

            prompt = """
            Use the extraced item and provide a response with the information associated with the item using the following information. Provide a response only on the extracted item.  

       		MEDIA,CHECKOUT,NUMBER OF RENEWALS
			BOOKS AND GOVERNMENT DOCS,SEMESTER LONG,2 renewals
			DVDS,7 DAYS,2 renewals
			RESERVE MATERIALS,2  HRS IN LIBRARY OR 24 HRS,1 renewal
			SCORES,SEMESTER,2 renewals
			CDS AND RECORDS,28 DAYS,2 renewals
			RECITAL CDS,"2 HRS, IN LIBRARY",1 renewal
			HEADPHONES,2 HRS,1 renewal 
			LAPTOPS,1 DAY OR 4 HRS,1 renewal
			TABLETS,7 DAYS,1 renewals

		If the item is anything else say we either don't have that item or that we don't offer that item for checkout 

		    query = %s
            """

            response = client.completions.create(model="gpt-3.5-turbo-instruct", prompt=prompt % query, temperature=0, max_tokens=1000)
            #print(response)
            completion_text = response.choices[0].text.strip().lower()
            print(completion_text)

        if relation == "staff":

            prompt = """
            Use the extraced item and provide a response with the information associated with the item using the following information. Provide a response only on the extracted item.

       		MEDIA,CHECKOUT,NUMBER OF RENEWALS
			BOOKS AND GOVERNMENT DOCS,28 DAYS,2
			DVDS,7 DAYS,2
			CDS AND RECORDS,7 DAYS,2
			RECITAL CDS,"2 HRS, IN LIBRARY",1
			SCORES,28 DAYS,2
			RESERVE MATERIALS,2  HRS IN LIBRARY OR 24 HRS,1
			HEADPHONES,2 HRS,1
			LAPTOPS,1 DAY OR 4 HRS,1
			TABLETS,7 DAYS,1 
			
			If the item is anything else say we either don't have that item or that we don't offer that item for checkout 

		    query = %s
            """

            response = client.completions.create(model="gpt-3.5-turbo-instruct", prompt=prompt % query, temperature=0, max_tokens=1000)
            #print(response)
            completion_text = response.choices[0].text.strip().lower()
            print(completion_text)


        if relation == "associate":

            prompt = """
            Use the extraced item and provide a response with the information associated with the item using the following information. Provide a response only on the extracted item.

       		MEDIA,CHECKOUT,NUMBER OF RENEWALS
			BOOKS AND GOVERNMENT DOCS,28 DAYS,2
			DVDS,7 DAYS,2
			SCORES,28 DAYS,2
			RECITAL CDS,CHECKOUT NOT AVAILABLE,
			HEADPHONES,2 HRS,1
			CDS AND RECORDS,7 DAYS,2 
		
			If the item is anything else say we either don't have that item or that we don't offer that item for checkout 

		    query = %s
            """

            response = client.completions.create(model="gpt-3.5-turbo-instruct", prompt=prompt % query, temperature=0, max_tokens=1000)
            #print(response)
            completion_text = response.choices[0].text.strip().lower()
            print(completion_text)


    elif classification == "books classification":
        print("Handling 'books classification' classification...")
        prompt = """
        Answer the user question as truthfully as possible making use of the information below. If needed, you can use your knowledge to figure out if what the user is asking may be associated with a subject below. If the answer is not contained within the text below say I don't know. Rephrase your answer so that it is logical and naturally sounding

Call numbers and locations,,
Letter,Subject Area,Floor*
A,"General reference works and periodicals. Museums. History of scholarship and learning. The humanities",2nd
B,Philosophy. Psychology. Religion,2nd
C,History of civilization. Archaeology. Heraldry. Genealogy. Biography,2nd
D,History: General (non-Americas) and Old World,2nd
E,History: United States (by time period),2nd
F,"Local U.S. History (states and cities). History of Canada, Mexico & South America",2nd 
G,"Geography, Anthropology, Recreation",2nd
H,Social Sciences,2nd
H - HJ, Business (Statistics. Economics. Industries. Commerce. Finance),2nd
HM-HX, Sociology. Social history & conditions.Communities. Socialism),2nd
J,Political Science,2nd
K,Law,2nd
L,Education,2nd
M,Music,Main
N,Fine Arts,Main
P,Language and Literature, 2nd
PF,German Literature,2nd
PG ,Slavic Literature,2nd
PN,General . Drama,2nd
PQ,French. Italian. Spanish. Portuguese,2nd
PR,English ,2nd
PS,American,2nd
PZ ,Juvenile,2nd
Q,Science,2nd
R,Medicine,2nd
S,Agriculture (Forestry. Aquaculture. Fishing. Hunting),2nd
T,"Technology (Engineering. Vehicles. Mining. Photography. Manufactures. Handicrafts)",2nd
U,Military Science (Army. Air Force),2nd
V,Naval Science (Navy. Marines. Navigation. Shipbuilding),2nd
Z,"Bibliography, Library Science. Information resources (general)",2nd
,,

		query = %s
		"""

        response = client.completions.create(model="gpt-3.5-turbo-instruct", prompt=prompt % query, temperature=0, max_tokens=1000)
        #print(response)
        completion_text = response.choices[0].text.strip().lower()
        print(completion_text)

    elif classification == "fallback":
        prompt = """
        Tell the user that you are not trained to answer such question. And let them know you can only answer questions about the following: Book Search, Library Hours, Study Spaces, Checkout Inquiries, and Books Location.

        Provide the response as a numbered list of what you can answer questions about

        query = %s
        """
        response = client.completions.create(model="gpt-3.5-turbo-instruct", prompt=prompt % query, temperature=0, max_tokens=1000)
        completion_text = response.choices[0].text.strip().lower()
        print(completion_text)

    else:
        print("I am sorry I have no clue what to do")

