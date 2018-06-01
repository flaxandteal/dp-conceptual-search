"""
Trains the ONS fastText model by generating text corpa from ONS publications
@author David Sullivan 01/06/18
"""
from typing import List
from supervised_models.src.reader import DocumentReader


def get_reader() -> DocumentReader:
    from .mongo.mongo_reader import MongoReader
    return MongoReader()


def train_model(fname_prefix: str, out_fname: str, label_prefix: str="__label__"):
    # Train the model
    import fastText

    print("Training fastText model...")
    model = fastText.train_supervised(input="%s.train" % fname_prefix, label=label_prefix, \
                                      dim=300, epoch=1000, wordNgrams=2, verbose=2, minCount=15, \
                                      minCountLabel=5, lr=0.1, neg=10, thread=16, loss="ns", t=1e-5)
    print("Saving...")
    model.save_model(out_fname)
    print("Done")
    return model


def main():
    from supervised_models.src.corpa import generate_labelled_corpus

    reader = get_reader()
    pages = reader.load_pages()

    corpus = generate_labelled_corpus(pages)
    return corpus


if __name__ == "__main__":
    corpus = main()
