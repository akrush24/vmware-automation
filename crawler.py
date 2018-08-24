import requests
from bs4 import BeautifulSoup
import csv
from datetime import datetime
from multiprocessing import Pool

def get_htm(url):
    r = requests.get(url)
    return r.text

def get_all_links(html):
    soup = BeautifulSoup(html, 'lxml')
    tds = soup.find('table', id='currencies-all').find_all('td', class_='currency-name')
    links= []
    for td in tds:
        a = td.find('a').get('href')
        link = 'https://coinmarketcap.com' + a
        links.append(link)
    return links

def get_page_data(html):
    soup = BeautifulSoup(html, 'lxml')
    try:
        name = soup.find('span', class_='text-gray').text.strip()
        print (name)
    except:
        name = ''
    try:
        price = soup.find('span', id='quote_price').text.strip()
    except:
        price = ''
    data = {'name': name,
            'price': price}
    return data

def write_csv(data):
    with open('coinmarketcap.csv', 'a') as f:
        writer = csv.writer(f)
        writer.writerow((data['name'],
                         data['price']))
        print(data['name'], 'parsed')
#url = 'https://coinmarketcap.com/all/views/all/'

def make_all(url):
    html = get_htm(url)
    data = get_page_data(html)
    write_csv(data)



def main ():
    #start = datetime.now()
    url = 'https://coinmarketcap.com/all/views/all/'
    all_links = get_all_links(get_htm(url))

    with Pool(5) as p:
        print(p.map(make_all, all_links))

    #for url in all_links:
      #  html = get_htm(url)
     #   data = get_page_data(html)
        #write_csv(data)



    #with pool(40) as p:
    #    p.map(make_all, all_links)



if __name__ == '__main__':
    main()