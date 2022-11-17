def main():
    pass

if __name__ == '__main__':
    main()
import pandas as pd
import numpy as np
import ftfy
import re
import nltk
nltk.download('stopwords')
nltk.download('punkt')
from string import punctuation
from nltk.tokenize import sent_tokenize
from nltk import word_tokenize
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
main_df = pd.read_excel("C:\\Users\\ommde\\OneDrive\\Desktop\\int project\\Input.xlsx")
def data_crawl(URL):
    path = "C:\\Program Files (x86)\\chromedriver.exe"
    driver = webdriver.Chrome(path)
    try:
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36"
        options = webdriver.ChromeOptions()
        options.headless = True
        options.add_argument(f'user-agent={user_agent}')
        options.add_argument("--window-size=1920,1080")
        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--allow-running-insecure-content')
        options.add_argument("--disable-extensions")
        options.add_argument("--proxy-server='direct://'")
        options.add_argument("--proxy-bypass-list=*")
        options.add_argument("--start-maximized")
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--no-sandbox')
        driver = webdriver.Chrome(executable_path="chromedriver.exe", options=options)
        driver.get(URL)
        if driver.title != "Page not found - Blackcoffer Insights":
            Web_Content = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "td-post-content"))
            )
            Content = Web_Content.text
        else : Content = " "
    except:
        driver.quit()
    print(URL)
    return (driver.title +" "+ Content)
main_df['Content'] = main_df.URL.apply(data_crawl)
def count_sentance(Content) :
    return len(sent_tokenize(Content))
main_df['sent_count'] = main_df.Content.apply(count_sentance)
# Punctuation removal
def clean(Content):
    return (re.sub('[^A-Za-z]+', ' ', Content))
main_df['Clean_Content'] = main_df.Content.apply(clean)
#Count total words
def count_words(Content):
    return (len(word_tokenize(Content)))
main_df['total_word'] = main_df.Clean_Content.apply(count_words)
# Count of total leters
def count_leters(Content):
    return (sum(not chr.isspace() for chr in Content))
main_df['total_leters'] = main_df.Clean_Content.apply(count_leters)
# Cleanning of stop words
# Loading all the stop words
files = ['StopWords_Auditor.txt','StopWords_Currencies.txt','StopWords_DatesandNumbers.txt','StopWords_Generic.txt',
'StopWords_GenericLong.txt','StopWords_Geographic.txt','StopWords_Names.txt']
all_stop_words = []
for i in files:
    with open(f"C:\\Users\\ommde\\OneDrive\\Desktop\\int project\\StopWords\\{i}") as f:
        lines = f.readlines()
    for elm in lines :
        split = elm.split()
        all_stop_words.append(split[0].upper())
def filter(Content):
    Cont = word_tokenize(Content)
    res = []
    for word in Cont:
        if word.upper() not in all_stop_words:
            res.append(word)
    return res
main_df['filtered_words'] = main_df.Clean_Content.apply(filter)
main_df['WORD COUNT'] = main_df.filtered_words.apply(len)
# Positive and negative Score
# Loading Positive words 
positive = np.loadtxt("C:\\Users\\ommde\\OneDrive\\Desktop\\int project\\MasterDictionary\\positive-words.txt", dtype='str')
positive_words = np.char.upper(positive)
def positive_score(f_words):
    res = 0
    for word in f_words:
        if word.upper() in positive_words:
            res += 1
    return res
main_df['POSITIVE SCORE'] = main_df.filtered_words.apply(positive_score)
# Loading Negative words 
negative = np.loadtxt("C:\\Users\\ommde\\OneDrive\\Desktop\\int project\\MasterDictionary\\negative-words.txt", dtype='str')
negative_words = np.char.upper(negative)
def negative_score(f_words):
    res = 0
    for word in f_words:
        if word.upper() in negative_words:
            res += 1
    return res
main_df['NEGATIVE SCORE'] = main_df.filtered_words.apply(negative_score)
# Polarity Score
main_df["POLARITY SCORE"] = (main_df['POSITIVE SCORE']-main_df['NEGATIVE SCORE'])/(main_df['POSITIVE SCORE']+main_df['NEGATIVE SCORE']+0.000001)
# Subjectivity Score
main_df["SUBJECTIVITY SCORE"] = (main_df['POSITIVE SCORE']+main_df['NEGATIVE SCORE'])/(main_df['WORD COUNT']+0.000001)
# Average Sentence Length
main_df["AVG SENTENCE LENGTH"] = main_df['total_word']/main_df['sent_count']
# Count Complex Words
def count_complex(Clean_Content):
    word_list = word_tokenize(Clean_Content)
    complex_count = 0
    for Word in word_list:
        word = Word.lower()
        res = len(re.findall('(?!e$)[aeiouy]+', word, re.I) +re.findall('^[^aeiouy]*e$', word, re.I))
        if res > 2 :
            complex_count += 1
    return complex_count
main_df['COMPLEX WORD COUNT'] = main_df.Clean_Content.apply(count_complex)
# Syllable Count per Word
def count_syllable(Clean_Content):
    word_list = word_tokenize(Clean_Content)
    syllable_count = 0
    for Word in word_list:
        word = Word.lower()
        res = len(re.findall('(?!e$)[aeiouy]+', word, re.I) +re.findall('^[^aeiouy]*e$', word, re.I))
        if res >2 :
            if word[-2]+word[-1] =='ed':
                res = res -1
            elif word[-2]+word[-1] =='es':
                res = res -1
        syllable_count += res
    return syllable_count/len(word_list)
main_df['SYLLABLE PER WORD'] = main_df.Clean_Content.apply(count_syllable)
# Percentage of Complex Words
main_df['PERCENTAGE OF COMPLEX WORDS'] = main_df['COMPLEX WORD COUNT']/main_df['total_word']
# Fog Index
main_df['FOG INDEX'] = (main_df['AVG SENTENCE LENGTH'] + main_df['PERCENTAGE OF COMPLEX WORDS'])*0.4
# Average number of words per sentence
main_df["AVG NUMBER OF WORDS PER SENTENCE"] = main_df["AVG SENTENCE LENGTH"]
# Personal Pronouns 
def personal_pro(clean_content):
    peronal_pronouns = ['I','we','my','ours','us','We','My','Ours','Us']
    word_list = word_tokenize(clean_content)
    res = 0
    for word in word_list :
        if word in peronal_pronouns:
            res +=1
    return res
main_df['PERSONAL PRONOUNS'] = main_df.Clean_Content.apply(personal_pro)
# Average Word Length 
main_df['AVG WORD LENGTH'] = main_df['total_leters']/main_df['total_word']
# Droping all the un-necessary coumns
main_df.drop(labels=['Content','sent_count','Clean_Content','total_word','total_leters','filtered_words'], axis=1, inplace = True)
df = main_df.loc[:,['URL_ID',	'URL',	'POSITIVE SCORE',	'NEGATIVE SCORE',	'POLARITY SCORE',	'SUBJECTIVITY SCORE',	'AVG SENTENCE LENGTH',	'PERCENTAGE OF COMPLEX WORDS',	'FOG INDEX',	'AVG NUMBER OF WORDS PER SENTENCE',	'COMPLEX WORD COUNT',	'WORD COUNT',	'SYLLABLE PER WORD',	'PERSONAL PRONOUNS',	'AVG WORD LENGTH']]
df.to_excel("Output Data.xlsx", index = False)
