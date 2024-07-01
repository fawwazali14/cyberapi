import json
import tweepy
import pandas as pd
from flask import Flask, request, jsonify
from sklearn.naive_bayes import MultinomialNB
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics import accuracy_score
import datetime
from flask_cors import CORS
from nltk.corpus import stopwords
from googleapiclient.discovery import build
import pickle

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "https://cyber-censor.vercel.app"}})

@app.route('/ml', methods=['POST'])
def ml():
    with open('model.pkl', 'rb') as model_file:
        nb = pickle.load(model_file)
    with open('vectorizer.pkl', 'rb') as vectorizer_file:
        vect = pickle.load(vectorizer_file)
    data = request.data.decode()
    print(data)
    xox = json.loads(data)
    platform = xox['platform']

    if platform == "Twitter":
        text = xox['text']
        sample_test = [text]
        sample_test_dtm = vect.transform(sample_test)
        a = nb.predict(sample_test_dtm)
        final = str(a[0])
        return jsonify({'result': final})

    elif platform == "Youtube":
        desp = xox['Desp']
        com = xox['Coms']
        st = [desp]
        sample_test_dtm = vect.transform(st)
        a = nb.predict(sample_test_dtm)
        finaldesp = str(a[0])

        com = eval(com)
        sample_test_dtm = vect.transform(com)
        a = nb.predict(sample_test_dtm)
        countzero = 0
        countone = 0
        for i in range(len(a)):
            if a[i] == 0:
                countzero += 1
            elif a[i] == 1:
                countone += 1

        return jsonify({"desp": finaldesp, "czero": countzero, "cone": countone})

@app.route('/dataa', methods=['POST'])
def data_social():
    try:
        data = request.data.decode()
        json_data = json.loads(data)
        platform = json_data['platform']
        id = json_data['id']

        if platform == "Twitter":
            consumer_key = "KAi8jFN93D96CAUwpwtJsDl5W"
            consumer_secret = "FH45qTtGgj8bvL9a4JlHZtKvZNh0FXqSd4yT7WjqjelQbKcDzG"
            access_token = "1484587292677181441-WtLbTzL5lCyklZlcVRK27kPFXYeCyZ"
            access_token_secret = "iI3almvnTMqvi8LyoVIZHqKEk6MTeXBq1kVWufUmehArx"

            auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
            auth.set_access_token(access_token, access_token_secret)
            api = tweepy.API(auth)

            status = api.get_status(id, tweet_mode='extended')
            full_text = status.full_text
            return jsonify({"text": full_text})

        elif platform == "YouTube":
            DEVELOPER_KEY = 'AIzaSyAxo0H1RshuKNpnA8Hpex0DPkII9O6z9sY'
            YOUTUBE_API_SERVICE_NAME = 'youtube'
            YOUTUBE_API_VERSION = 'v3'
            video_id = id
            youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=DEVELOPER_KEY)
            comments = []
            nextPageToken = ''
            while True:
                results = youtube.commentThreads().list(
                    part='snippet',
                    videoId=video_id,
                    pageToken=nextPageToken
                ).execute()

                nextPageToken = results.get('nextPageToken')

                for item in results['items']:
                    comment = item['snippet']['topLevelComment']['snippet']['textDisplay']
                    comments.append(comment)

                if not nextPageToken:
                    break

            request1 = youtube.videos().list(
                part="snippet,contentDetails,statistics",
                id=video_id
            )
            response = request1.execute()
            description = response['items'][0]['snippet']['description']
            cleaned_string = description.replace("\n", "")
            no = len(comments)

            return jsonify({"Comments": comments, "Description": cleaned_string, "Com_count": no})

        else:
            return jsonify({"error": f"Unsupported platform: {platform}"})

    except KeyError as e:
        return jsonify({"error": f"Missing key in request data: {str(e)}"})

    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
