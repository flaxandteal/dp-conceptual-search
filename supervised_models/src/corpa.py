from typing import List
from supervised_models.src.page import Page


def markdown_to_text(md):
    import markdown
    from bs4 import BeautifulSoup

    extensions = ['extra', 'smarty']
    html = markdown.markdown(md, extensions=extensions, output_format='html5')
    soup = BeautifulSoup(html, "lxml")
    return soup.text


def generate_labelled_corpus(pages: List[Page], prefix: str="__label__") -> List[dict]:
    lines = []
    for page in pages:
        if page.has_keywords():
            sentences = page.get_corpus_sentences()
            labels = " ".join(["%s%s" % (prefix, l) for l in page.get_labels()])

            if labels == '__label__exportsimportscommoditiesvolumesmret':
                print(page.description)

            for sentence in sentences:
                line = "%s %s" % (labels, sentence)
                lines.append(line)
    return lines


def write_corpus(fname_prefix: str, complete_corpus: List[str], randomize: bool=True):
    """
    Splits the corpus into training (.train) and validation (.valid) datasets
    """
    import numpy as np
    if randomize:
        import random
        random.shuffle(complete_corpus)

    size_train = int(np.round(len(complete_corpus) * (3. / 4.)))
    train_corpus = complete_corpus[:size_train]
    valid_corpus = complete_corpus[size_train:]

    for suffix, corpus in zip(['train', 'valid'], [train_corpus, valid_corpus]):
        with open("%s.%s" % (fname_prefix, suffix), "w") as f:
            for line in corpus:
                f.write("%s\n" % line)
