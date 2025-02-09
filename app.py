# importing all the neccessary libraries
import os
import json
import googleapiclient.discovery
from flask import request, Flask, render_template, jsonify
import requests
import numpy as np
import pandas as pd
from textblob import TextBlob

app = Flask(__name__)
@app.route('/',methods=['GET'])
def Home():
    return render_template('home.html')

@app.route("/predict", methods=['POST'])
def predict():
    if request.method == 'POST':
        try:

            link = request.form['url_name']
            if 'youtu.be' in link:
                v_id = link.split('youtu.be/')[-1]
            
            elif 'shorts' in link:
                v_id = link.split('shorts/')[-1].split('?')[0]
                
            else:
                v_id = link.split('?v=')[-1].split('&')[0]
            os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
            api_service_name = "youtube"
            api_version = "v3"
            DEVELOPER_KEY = "AIzaSyAQutJZfdFEGh1W_WuQexIpByqs310SY6M"
            youtube = googleapiclient.discovery.build(api_service_name, api_version, developerKey = DEVELOPER_KEY)
            link_request = youtube.commentThreads().list(part="snippet", maxResults=200,  order="relevance",videoId= v_id)
            link_response = link_request.execute()
            result = link_response.copy()
            comments = []
            for i in range(len(result['items'])):
                comments.append(result['items'][i]['snippet']['topLevelComment']['snippet']['textOriginal'])
            
            
            # Calculate sentiment for each comment and classify into categories
            sentiments_dict = {}
            for comment in comments:
                blob = TextBlob(comment)
                sentiment_value = blob.sentiment.polarity
                
                # Classify sentiment value into positive, negative, or neutral labels
                if sentiment_value > 0:
                    sentiment_label = 'Positive'
                elif sentiment_value < 0:
                    sentiment_label = 'Negative'
                else:
                    sentiment_label = 'Neutral'
                
                # Store sentiment label in the dictionary
                sentiments_dict[comment] = sentiment_label

            lst=[]
            lst.append(sentiments_dict) # append dictionary into list
            # print(lst)

            # Initialize counters for positive and negative sentiments
            positive_count = negative_count = neutral_count = length_of_dict = 0

            # Iterate through the list
            for item in lst:
                length_of_dict = len(item)

                # Iterate through the dictionary inside the list
                for sentiment_label in item.values():
                    if sentiment_label == 'Positive':
                        positive_count += 1
                    elif sentiment_label == 'Negative':
                        negative_count += 1
                    elif sentiment_label == 'Neutral':
                        neutral_count  += 1
                        
                           
            # return render_template('home.html',prediction_text=f"For top 100 relevant comments, the final average sentiment is: {final_sentiment} and the average Sentiment Score is {med_score}")
            return render_template('home.html', sentiments_dict=lst, length_of_dict=length_of_dict, positive_count=positive_count, negative_count=negative_count, neutral_count=neutral_count)

        except:
            return render_template('home.html',prediction_text=f"Comments are Disabled.")
    else:
        print('NO ENTRY')
        return render_template('home.html')

if __name__=="__main__":
    app.run()
