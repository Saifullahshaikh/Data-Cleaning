import requests, re
from bs4 import BeautifulSoup
import pandas as pd

# Define the URLs of the e-commerce websites you want to scrape
url1 = 'https://priceoye.pk/mobiles/infinix'
url2 = 'https://www.olx.com.pk/infinix-mobile-phones_c1453?filter=make_eq_infinix'

# Function to scrape product SKUs from a website
def scrape_product_skus(url):
    product_data ={}
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        # Find and extract product
        if url == url1:
            product_list = [sku.text for sku in soup.find_all('div', class_='detail-box')]
            # return product_skus
            pattern = r'(\w+\s+\w+\s+\d+)\s+Rs.\s+(\d+,\d+)'

            # Find all matches in the scraped data
            matches = re.findall(pattern, ''.join(product_list))
            # Extracted data will be a list of tuples, where each tuple contains (product name, price)
            product_list = matches
            product_data['Site1'] = {}
            product_data['Site1']['Title'] = [product_list[title][0] for title in range(len(product_list)-1)]
            product_data['Site1']['Price'] = [product_list[price][1] for price in range(len(product_list)-1)]
            return product_data
        else:
            product_title = [sku.text for sku in soup.find_all('div', class_="_5fdf4379")]
            modified_titles = [' '.join(title.split()[:3]) for title in product_title]
            product_price = [sku.text for sku in soup.find_all('span', class_="_95eae7db")]
            product_data['Site2'] = {}
            product_data['Site2']['Title'] = [modified_titles[title] for title in range(len(modified_titles)-1)]
            product_data['Site2']['Price'] = [product_price[price].replace('Rs', '') for price in range(len(product_price)-1)]
            return product_data
    else:
        print(f"Failed to fetch data from {url}")
        return []

# Scrape products from both websites
product_list1 = scrape_product_skus(url1)
product_list2 = scrape_product_skus(url2)
# print(product_list1,product_list2)

# data clean for both sites data
data1 = product_list1['Site1']
data2 = product_list2['Site2']

df1 = pd.DataFrame(data1)
df2 = pd.DataFrame(data2)

# Check for duplicates
df1 = df1.drop_duplicates(subset='Title', keep='first')
df2 = df2.drop_duplicates(subset='Title', keep='first')

# Check for missing values
df1 = df1.dropna()
df2 = df2.dropna()
# Both site cleaned df
print("Site 1 data: ", df1,sep="\n")
print("Site 2 data: ", df2,sep="\n")

# merging dataframes base on common title
merged_df = df1.merge(df2, on='Title', how='inner',suffixes=('_site1', '_site2'))

#Recomendation based on price
merged_df['Recommendation'] = ['Site 1' if int(price_site1.replace(',', '')) < int(price_site2.replace(',', '')) else 'Site 2' for price_site1, price_site2 in zip(merged_df['Price_site1'], merged_df['Price_site2'])]
print("Common Products ",merged_df, sep="\n")

# write data in xls
with pd.ExcelWriter('output.xlsx', engine='xlsxwriter') as writer:
    # Write dataframe to a excel sheet
    merged_df.to_excel(writer, sheet_name='common_data', index=False)
    


