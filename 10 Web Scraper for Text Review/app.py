# doing necessary imports
from flask import Flask, render_template, request
# from flask_cors import CORS,cross_origin
import requests
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as uReq

# initialising the flask app with the name 'app'
app = Flask(__name__)


# base url + '/', i.e. 'http://localhost:8000' + '/'
@app.route('/', methods=['GET', 'POST'])  # route with allowed methods as POST and GET
def index():
    if request.method == 'GET':
        return render_template('index.html')
    elif request.method == 'POST':
        # obtaining the search string entered in the form
        searchString = request.form['content'].replace(' ', '%20')
        try:
            # preparing the URL to search the product on flipkart
            flipkart_url = 'https://www.flipkart.com/search?q=' + searchString
            # requesting the webpage from the internet
            uClient = uReq(flipkart_url)
            # reading the webpage
            flipkartPage = uClient.read()
            # closing the connection to the web server
            uClient.close()
            # parsing the webpage as HTML
            flipkart_html = bs(flipkartPage, 'html.parser')
            # searching for appropriate tag to redirect to the product link
            bigboxes = flipkart_html.find_all('div', {'class': '_1AtVbE col-12-12'})
            # the first 3 members of the list do not contain relevant information, hence deleting them
            del bigboxes[0:3]
            # taking the first iteration (for demo)
            box = bigboxes[0]
            # extracting the actual product link
            productLink = 'https://www.flipkart.com' + box.div.div.div.a['href']
            # getting the product page from server
            productPage = requests.get(productLink)
            # parsing the product page as HTML
            product_html = bs(productPage.text, 'html.parser')
            # extracting the name of the product
            productName = product_html.find('span', {'class': 'B_NuCI'}).text
            # finding the HTML section containing the customer comments
            commentSection = product_html.find_all('div', {'class': '_16PBlm'})
            # initializing an empty list for reviews
            reviews = []
            # iterating over the comment section to get the details of customer and their comments
            for commentbox in commentSection[:-1]:
                try:
                    name = commentbox.div.div.find_all('p', {'class': '_2sc7ZR _2V5EHH'})[0].text
                except:
                    name = 'No Name'
                try:
                    rating = commentbox.div.div.div.div.text
                except:
                    rating = 'No Rating'
                try:
                    commentHead = commentbox.div.div.div.p.text
                except:
                    commentHead = 'No Comment Heading'
                try:
                    customerComment = commentbox.div.div.find_all('div', {'class': ''})[0].div.text
                except:
                    customerComment = 'No Customer Comment'
                # saving that detail to a dictionary
                mydict = {'Product': productName, 'Name': name, 'Rating': rating,
                          'CommentHead': commentHead, 'Comment': customerComment}
                # appending the comments to the review list
                reviews.append(mydict)
            # showing the review to the user
            return render_template('results.html', reviews=reviews)
        except Exception as e:
            return 'something is wrong: ' + str(e)


if __name__ == '__main__':
    # running the app on the local machine on port 8000
    app.run(port=8000, debug=True)
