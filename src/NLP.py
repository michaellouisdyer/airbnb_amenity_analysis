import spacy
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.pipeline import Pipeline
from sklearn.svm import LinearSVC
from sklearn.feature_extraction.stop_words import ENGLISH_STOP_WORDS as stopwords
from string import punctuation
from sklearn.linear_model import LassoCV
from spacy.lang.en import English
parser = English()

def get_corpus(text_type):
    if text_type == 'all':
        prop = pd.read_csv('../data/denver_properties.csv')
        return prop['title'].str.cat(prop[['description',  'desc_space', 'desc_transit', 'desc_neighborhood', 'desc_interaction', 'desc_rules', 'desc_notes', 'desc_access']], sep = ".", na_rep = ""), prop['c_revenue_native_ltm']


    else:
        prop = pd.read_csv('../data/denver_properties.csv')[[text_type, 'c_revenue_native_ltm']].dropna()
        return prop[text_type], prop['c_revenue_native_ltm']

def spacy_tokenizer(doc):
    tokens = parser(doc)
    tokens = [tok.lemma_.lower().strip() if tok.lemma_ != "-PRON-" else tok.lower_ for tok in tokens]
    tokens = [tok for tok in tokens if (tok not in stopwords and tok not in punctuation)]
    return tokens

def do_NLP():
    corpus, target = get_corpus('all')
    vec =  TfidfVectorizer(tokenizer = spacy_tokenizer, max_features = 500, max_df = 1.0, ngram_range = (1,5))
    matrix = vec.fit_transform(corpus)
    matrix.shape
    len(vec.vocabulary_)
    ls = LassoCV(verbose =  True, n_jobs = -1)
    print("fitting model")
    ls.fit(matrix, target)
    print("done")
    coefficients_df = pd.DataFrame.from_dict(dict(zip(vec.get_feature_names(), ls.coef_)), orient='index').sort_values(by=0)
    score = ls.score(matrix, target)
    print(f"R^2 = {score: .3f} \n Alpha: {ls.alpha_ : .3f}")
    most_common_words = np.array(vec.get_feature_names())[matrix.toarray().sum(axis=0).argsort()[::-1]]
    import pdb; pdb.set_trace()
