#-------------------------------------------------------------------------------
# Name:        Word Frequency
# Purpose:     Analyse word frequency in a series of timestamped Tweets.
#
# Author:      Andrew Mellor
#
# Created:     04/06/2014
# Copyright:   (c) Andrew Mellor 2014
# Licence:     The MIT License (MIT)
#-------------------------------------------------------------------------------

"""
word_frequency.py {csv-file-path} {output-path} [{time-window-length}]

Calculates the frequency of words in Tweets in a given time window (default 60s).
"""

def getData(input_csv):
    """
    Reads in a csv file and returns a pandas dataframe consisting
    of the columns [timestamps] and [tweet] only
    """

    # Reads in .CSV file.
    df = pd.read_csv(input_csv,
                        sep=",",
                        header = 0,
                        date_parser = dateutil.parser.parse,
                        parse_dates=["utc"],
                        usecols = ["body","utc","actor.languages"]
                        )

    df.rename(columns={"body":"tweet","utc":"timestamp","actor.languages":"language"} , inplace=True)
    df.set_index(["timestamp"], inplace=True, drop=False)

    print "\n"
    print "Data Import Successful ({} tweets)".format(len(df))
    print "Columns: {}".format(df.columns.values)
    print "First tweet timestamp (UTC):", df['timestamp'][0]
    print "Last tweet timestamp (UTC): ", df['timestamp'][len(df)-1]
    return df

def group_by_T_min_intervals(x, T, start_timestamp):
    return int((x.day - start_timestamp.day)*24*(60.0/T)) + int((x.hour - start_timestamp.hour)*(60.0/T)) + int((x.minute - start_timestamp.minute)/T)

def calculateFrequencies(df, include_bigrams = True):
    """
    Takes a pandas dataframe of tweets and timestamps and calculates the
    frequency of each word within the given timestep.
    """
    frequencies = {}
    grouped = df.groupby(lambda x: group_by_T_min_intervals(x,timestep,df['timestamp'][0]))

    for hour,group in grouped:

        en_tweets = group[group['language'] == 'en'].pop('tweet') # Takes tweets marked as English only.
        tokens = []
        for txt in en_tweets.values:
            try:
                tokens.extend([t.lower().strip('",:,.,#,?,;,!),(') for t in txt.split()]) # Removes punctuation and hashtags.
            except BaseException, e:
                print "Something has gone wrong {}".format(str(e))
                print "======================="
                print txt
                print "======================="

        # Removes empty strings (comment/uncomment as you please).
        tokens = [c for c in tokens if c]

        # Remove user @mentions (comment/uncomment as you please).
        tokens = [c for c in tokens if c[0]!='@']

        # Remove #hashtags (comment/uncomment as you please).
        #tokens = [c for c in tokens if c[0]!='#']

        # Remove URLs (comment/uncomment as you please).
        tokens = [c for c in tokens if c[:4]!='http']

        # Remove single letter words (comment/uncomment as you please).
        #tokens = [c for c in tokens if len(c) > 1]

        # Remove keywords (RT for retweet, e.t.c) (comment/uncomment as you please).
        omitted_words = ['rt','de','&amp','-']
        tokens = [c for c in tokens if c not in omitted_words]

        # Use a Counter to construct frequency tuples
        tokens_counter = Counter(tokens)

        # Remove Stopwords (the, and, e.t.c) (comment/uncomment as you please).
        for t in nltk.corpus.stopwords.words('english'):
            try:
                tokens_counter.pop(t)
            except KeyError,e:
                pass

        if include_bigrams:
            bgs = nltk.bigrams(tokens)
            # Compute frequency distribution for all the bigrams in the text
            fdist = nltk.FreqDist(bgs)
            bigrams = {' '.join(k): v for k, v in fdist.items() if v>1}

            # Add bigrams to words
            tokens_counter = tokens_counter + Counter(bigrams)

        # Collect words and frequencies.
        frequencies[hour] = tokens_counter

    # Add words and frequencies to a dataframe.
    frequency_table = pd.DataFrame(frequencies)
    frequency_table.fillna(0, inplace=True)
    frequency_table = frequency_table.astype('int')

    return frequency_table

def outputData(frequencies, output_csv):
    """
    Saves the frequency of each word within each timestep to the given
    output .csv file.
    """
    frequencies.to_csv(output_csv)
    print "\n"
    print "Data Exported Successfully"
    return None

def printSummary(frequencies):
    """
    Provides a brief summary of the top trends after processing.
    """
    frequencies['total'] = frequencies.sum(axis=1)
    frequencies.sort(columns=['total'], axis=0, ascending=False, inplace=True)
    print "\n"
    print "Top Words Over Time (grouped {} minute intervals)".format(timestep)
    print "=================================================="
    print frequencies.head(20)

if __name__ == '__main__':
    import sys
    import pandas as pd
    import dateutil
    from collections import Counter
    import nltk

    if len(sys.argv[1:]) == 2:
        input_csv = sys.argv[1]
        output_csv = sys.argv[2]
        timestep = 60
    elif len(sys.argv[1:]) == 3:
        input_csv = sys.argv[1]
        output_csv = sys.argv[2]
        timestep = int(sys.argv[3])
    else:
        print("""word_frequency.py {csv-file-path} {output-path} [{time-window-length}]

Script requires at least two arguments.
""")
        sys.exit(1)

    print "\n"
    nltk.download('stopwords')
    data = getData(input_csv)
    frequencies = calculateFrequencies(data, include_bigrams=True)
    outputData(frequencies, output_csv)
    printSummary(frequencies)
