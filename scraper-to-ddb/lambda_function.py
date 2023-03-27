import boto3
import requests
from bs4 import BeautifulSoup

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('used_clothing_database')

def lambda_handler(event, context):
    # Setting up base code
    base_url = 'https://poshmark.com/category/'
    categories = [
        'Women',
        # 'Men',
        # 'Kid'
    ]
    
    # Create urls
    urls = [f'{base_url}{category}' for category in categories]
    
    # Loop through different categories
    for current_url in urls:
        page = 1
    
        while True:
            url = f'{current_url}?max_id={page}'
    
            # Send a request to the URL, grab page content, parse the content
            response = requests.get(url)
            html_content = response.content
            soup = BeautifulSoup(html_content, 'html.parser')
            listings = soup.find_all('div', class_='card')
        
            # Break out of the loop once done
            if len(listings) == 0:
                break
            
            # Reset counters
            errors = 0
            items = 0
    
            # Scrape the stuff
            for listing in listings:
                try:
                    items += 1
                    title = listing.find('a', class_='tile__title tc--b').text.strip()
                    price = listing.find('span', class_='p--t--1 fw--bold').text.strip()
                    price = price.split('$')[1]
                    size = listing.find('a', class_='tile__details__pipe__size ellipses').text.strip()
                    size = size.split('Size: ')[1]
                    brand = listing.find('a', class_='tile__details__pipe__brand').text.strip()
                    img_src = listing.find('img', class_='ovf--h d--b')['src']
                    
                    # Put em into the table
                    table.put_item(
                                   Item={
                                   'product_name': title,
                                   'brand': brand,
                                   'image_url': img_src,
                                   'marketplace': "Poshmark",
                                   'price': price,
                                   'size': size,
                                   })
                                   
                    #print(f'Title: {title}\nPrice: {price}\nSize: {size}\nImg: {img_src}\nBrand: {brand}\n')
                except:
                    errors += 1
                    #print(f'Error fetching information, skipping item')
            
            print(f'page: {page}, items: {items}, errors: {errors}')
            
            # For analytics
            page += 1
            errors = 0
            items = 0
            
