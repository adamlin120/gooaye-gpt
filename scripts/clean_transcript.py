import pandas as pd


df = pd.read_csv("transcript.csv")

# to int
df['start'] = df['start'].astype(int)

# merge two cols: episode, start, as episode_start
df['id'] = df['episode'].astype(str) + "_" + df['start'].astype(str)

# sort by episode, start
df = df.sort_values(by=['episode', 'start'])

# set id as index
df = df.set_index('id')

# remove episode, start
df = df.drop(columns=['episode', 'start'])

df.to_csv("transcript_clean.csv")

# split a small part of the data for testing
df = df.sample(frac=0.1, random_state=42)
df.to_csv("transcript_clean_test.csv")