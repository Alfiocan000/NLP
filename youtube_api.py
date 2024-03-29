# -*- coding: utf-8 -*-
filename = ''

import pandas as pd
df = pd.read_excel(filename)

df['captions']

import pandas as pd
df = pd.read_csv('NewDiscourses_2024_01_28-20_15_31.csv')
df.head()

#!pip install youtube_transcript_api
from youtube_transcript_api import YouTubeTranscriptApi
# srt = YouTubeTranscriptApi.get_transcript("n0fpeiFNWMY")

def extract_srt(videoId):
  try:
    srt = YouTubeTranscriptApi.get_transcript(videoId)
    text = " ".join([line for line in pd.DataFrame(srt)['text'].tolist() if line[0]!='['])
    print('text')
    return(text)
  except:
    print('99')
    return('99')

captions = df['videoId'].apply(lambda x: extract_srt(x))
captions

import pandas as pd
from tqdm import tqdm
from youtube_transcript_api import YouTubeTranscriptApi

# Funzione con barra di progresso
def extract_srt_with_progress(video_id):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        text = " ".join([line for line in pd.DataFrame(srt)['text'].tolist() if line[0]!='['])
        return text
    except Exception as e:
        print(f"An error occurred: {e}")
        return ""

# Applica la funzione con barra di progresso alla colonna 'videoId'
df['captions'] = list(tqdm(df['videoId'].apply(extract_srt_with_progress), desc="Processing videos", unit="video"))

# Visualizza il DataFrame risultante
print(df)

df.to_excel('NewDiscourses_2024_01_28-20_15_31_captions.xlsx')

# NLP

import pandas as pd

# df = pd.read_excel('NewDiscourses_2024_01_28-20_15_31_captions.xlsx')
df.columns

df['date'] = pd.to_datetime(df['publishedAtSQL'])

!pip install stop_words
!pip install xlsxwriter

import xlsxwriter
from stop_words import get_stop_words

stoplist = get_stop_words('en')
toremove = ['music','applause']

def find_Topics(df,feature_text,n_topics,toremove):

    from sklearn.feature_extraction.text import TfidfVectorizer
    vett = TfidfVectorizer(ngram_range=(1,3),                    # chiediamo segmenti ripetuti fino a lunghezza 3
                           max_features = 1000,                  # n. massimo di parole da considerare
                           stop_words = stoplist+toremove,
                           min_df = 2,                           # frequenza minima di una forma grafica per essere considerata
                           max_df = 0.9,
                          #  tokenizer = mytokenizer
                           )


    # Per chiarezza, chiamiamo "V" la matrice Tf-idf
    V = vett.fit_transform(df[feature_text].astype(str))
    words = vett.get_feature_names_out()
    print(V.shape)

    from sklearn.decomposition import NMF
    model = NMF(n_components=n_topics,beta_loss='kullback-leibler', solver='mu', max_iter=1000, alpha_H=.1, l1_ratio=.5)

    # Model fit
    W = model.fit_transform(V)
    H = model.components_
    import pandas as pd
    word_topic_df = pd.DataFrame(H.T,index=words)
    document_topic_df = pd.DataFrame(W)
    document_topic_df["Topic"] = document_topic_df.idxmax(axis=1)

    sheet_1 = pd.concat([df,document_topic_df],axis=1)
    sheet_2 = word_topic_df

    # Create a Pandas Excel writer using XlsxWriter as the engine.
    writer = pd.ExcelWriter('NMF()_Results.xlsx', engine='xlsxwriter')

    # Write each dataframe to a different worksheet.
    sheet_1.to_excel(writer, sheet_name='documents')
    sheet_2.to_excel(writer, sheet_name='words')

    # Close the Pandas Excel writer and output the Excel file.
    writer.save()
    # return(word_topic_df,document_topic_df)

find_Topics(df,'captions',20,toremove)

Docs = df['captions'].astype(str)

#%%
import pandas as pd
import networkx as nx
from sklearn.feature_extraction.text import CountVectorizer


# CountVectorizer
cv = CountVectorizer(ngram_range=(2,2),                    # chiediamo segmenti ripetuti fino a lunghezza 3
                           max_features = 1000,                  # n. massimo di parole da considerare
                           stop_words = stoplist+toremove,
                           min_df = 10,                           # frequenza minima di una forma grafica per essere considerata
                           max_df = 0.5)

# Docs = df[feature_text].astype(str)  # Text
X = cv.fit_transform(Docs)
words = cv.get_feature_names_out()

# Network from Adjacency matrix
Adj = pd.DataFrame((X.T*X).toarray(),columns=words,index=words)

# Here is my graph object
G = nx.from_pandas_adjacency(Adj)

# Graph info
print("Nodes:")
print(len(G.nodes()))
print("Edges:")
print(len(G.edges()))

# Run degree centrality
degree_dict = dict(G.degree(G.nodes()))
# Degree = list(degree_dict.values())

# Run eigenvector centrality
eigenvector_dict = nx.eigenvector_centrality(G)

# Run closeness centrality
closeness_dict = nx.closeness_centrality(G)

# Run betweenness centrality
betweenness_dict = nx.betweenness_centrality(G)

# Assign each to an attribute in your network
nx.set_node_attributes(G, degree_dict, 'degree')
nx.set_node_attributes(G, betweenness_dict, 'betweenness')
nx.set_node_attributes(G, eigenvector_dict, 'eigenvector')
nx.set_node_attributes(G, closeness_dict, 'closeness')

# Gephi
nx.write_gexf(G,"Gephi()_Results.gexf")
