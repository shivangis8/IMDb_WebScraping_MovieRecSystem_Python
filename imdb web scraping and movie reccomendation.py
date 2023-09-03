#!/usr/bin/env python
# coding: utf-8

# In[ ]:


# Install required modules
#!pip install requests
#!pip install bs4


# In[1]:


# Import libraries
from bs4 import BeautifulSoup
import requests
import pandas as pd
import re
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler


# In[2]:


# Define source and extract data through web scraping (page 1: 1-100 titles)

try:
    source = requests.get('https://www.imdb.com/search/title/?count=100&groups=top_1000&sort=user_rating')
    source.raise_for_status
    
    soup = BeautifulSoup(source.text, 'html.parser')
    
    movies = soup.find('div', class_ = "lister-list").find_all('div', class_ = "lister-item-content")
    
    #print(len(movies))
    
    data = [] # Initialize an empty list to store data
    
    for movie in movies:
        rank = int(movie.find('h3', class_ = "lister-item-header").find('span', class_ = "lister-item-index unbold text-primary").text.strip('.'))
        name = movie.find('h3', class_ = "lister-item-header").a.text
        
        rating_element = movie.find('p', class_ = "text-muted").find('span', class_ = "certificate")
        if rating_element:
            rating = rating_element.text 
        else:
            rating = ""
            
        genre_element = movie.find('p', class_ = "text-muted").find('span', class_ = "genre")
        if genre_element:
            genre = genre_element.text.strip()
        else:
            genre = ""
            
        year_element = movie.find('h3', class_ = "lister-item-header").find('span', class_ = "lister-item-year text-muted unbold")
        if year_element:
            year = int(re.search(r'\d{4}', year_element.text).group()) if re.search(r'\d{4}', year_element.text) else ""
        else:
            year = ""
            
        score_element = movie.find('div', class_ = "ratings-bar")
        if score_element:
            score = float(score_element.strong.text)
        else:
            score = ""
        
        votes_element = movie.find('p', class_ = "sort-num_votes-visible").find('span', {'name': 'nv'})
        if votes_element:
            votes = int(votes_element['data-value'])
        else:
            votes = ""
            
        gross_element = movie.find('p', class_ = "sort-num_votes-visible").find('span', text='Gross:')
        if gross_element:
            gross = float(gross_element.find_next('span', {'name': 'nv'}).text.strip('$M'))
        else:
            gross = ""
        
        runtime_element = movie.find('p', class_ = "text-muted").find('span', class_ = "runtime")
        if runtime_element:
            runtime = int(runtime_element.text.strip(' min'))
        else:
            runtime = ""
        
        #print(rank, name, rating, genre, year, score, votes, gross, runtime)
        #break
        
        # Append data to the list
        data.append({
            "Rank": rank,
            "Name": name,
            "Rating": rating,
            "Genre": genre,
            "Year": year,
            "Score": score,
            "Votes": votes,
            "Gross": gross,
            "Runtime": runtime
        })

# Export data to excel file
    df100 = pd.DataFrame(data)

    excel_path = 'C:/Project/movies_data.xlsx'
    df100.to_excel(excel_path, index=False)

    print(f'Data saved to Excel.')
        
except Exception as e:
    print(e)


# In[3]:


# Define source and extract data through web scraping (page 2-5: 101-500 titles)

existing_df = pd.read_excel('C:/Project/movies_data.xlsx')

try:
    num_pages = 9
    movies = []
    
    for page in range(2, num_pages+2):
        base_url = f'https://www.imdb.com/search/title/?groups=top_1000&sort=user_rating,desc&count=100&start={(page - 1) * 100 + 1}&ref_=adv_nxt'
    
        source = requests.get(base_url)
        source.raise_for_status
    
        soup = BeautifulSoup(source.text, 'html.parser')
    
        movies = soup.find('div', class_ = "lister-list").find_all('div', class_ = "lister-item-content")
    
        #print(len(movies))
        
        page_data = []
        
        for movie in movies:
            rank = int(movie.find('h3', class_ = "lister-item-header").find('span', class_ = "lister-item-index unbold text-primary").text.strip('.,').replace(',', ''))
            name = movie.find('h3', class_ = "lister-item-header").a.text
        
            rating_element = movie.find('p', class_ = "text-muted").find('span', class_ = "certificate")
            if rating_element:
                rating = rating_element.text 
            else:
                rating = ""
            
            genre_element = movie.find('p', class_ = "text-muted").find('span', class_ = "genre")
            if genre_element:
                genre = genre_element.text.strip()
            else:
                genre = ""
            
            year_element = movie.find('h3', class_ = "lister-item-header").find('span', class_ = "lister-item-year text-muted unbold")
            if year_element:
                year = int(re.search(r'\d{4}', year_element.text).group()) if re.search(r'\d{4}', year_element.text) else ""
            else:
                year = ""
            
            score_element = movie.find('div', class_ = "ratings-bar")
            if score_element:
                score = float(score_element.strong.text)
            else:
                score = ""
            
            votes_element = movie.find('p', class_ = "sort-num_votes-visible").find('span', {'name': 'nv'})
            if votes_element:
                votes = int(votes_element['data-value'])
            else:
                votes = ""
            
            gross_element = movie.find('p', class_ = "sort-num_votes-visible").find('span', text='Gross:')
            if gross_element:
                gross = float(gross_element.find_next('span', {'name': 'nv'}).text.strip('$M'))
            else:
                gross = ""
        
            runtime_element = movie.find('p', class_ = "text-muted").find('span', class_ = "runtime")
            if runtime_element:
                runtime = int(runtime_element.text.strip(' min'))
            else:
                runtime = ""
        
            #print(rank, name, rating, genre, year, score, votes, gross, runtime)
            #break
            
            page_data.append({
                "Rank": rank,
                "Name": name,
                "Rating": rating,
                "Genre": genre,
                "Year": year,
                "Score": score,
                "Votes": votes,
                "Gross": gross,
                "Runtime": runtime
            })
            
# Export data to excel file
        page_df = pd.DataFrame(page_data)
        existing_df = pd.concat([existing_df, page_df], ignore_index=True)

except Exception as e:
    print(e)
    
# Save the updated dataframe to the same Excel file
existing_df.to_excel('C:/Project/movies_data.xlsx', index=False)

print(f'Data saved to Excel.')


# In[5]:


# Create a dataframe 'df'
df = existing_df
print(len(df))
df.head()


# In[6]:


# Check data types
df.info()


# In[8]:


# Correct data types
df['Gross'] = pd.to_numeric(df['Gross'], errors = 'coerce')
df.info()


# In[9]:


# Create a copy of the dataset
df_og = df.copy()


# ### Create a movie recommendation system based on Genre

# In[10]:


genres = df['Genre'].str.get_dummies(',')

# Standardize numerical columns
scaler = StandardScaler()
numerical_cols = ['Year', 'Score', 'Votes', 'Gross', 'Runtime']
df[numerical_cols] = scaler.fit_transform(df[numerical_cols])

# Combine features
features = pd.concat([genres, df[numerical_cols]], axis=1)
features = np.nan_to_num(features, nan=0)

# Display %match in different color
GREEN = '\033[92m'
END_COLOR = '\033[0m'

# Calculate cosine similarity between movies
movie_similarity = cosine_similarity(features)

# Recommendation function
def get_movie_recommendations():
    movie_title = input("Recommend movies similar to: ")  # Input for the movie title
    movie_idx = df[df['Name'] == movie_title].index[0]
    similar_scores = list(enumerate(movie_similarity[movie_idx]))
    similar_scores.sort(key=lambda x: x[1], reverse=True)
    similar_movies = similar_scores[1:11]  # Get top 10 recommendations excluding input movie
    
    recommendations = []
    
    for i in similar_movies:
        title = df.iloc[i[0]]['Name']
        score = df_og.iloc[i[0]]['Score']
        similarity_percent = f"{i[1] * 100:.2f}% match"
        recommendation_text = f"{title} (imdB {score}): {GREEN}{similarity_percent}{END_COLOR}"
        recommendations.append(recommendation_text)

    return recommendations, movie_title


# In[11]:


# Testing the recommendation system

recommendations, movie_title = get_movie_recommendations()
for recommendation in recommendations:
    print(recommendation) 


# In[ ]:




