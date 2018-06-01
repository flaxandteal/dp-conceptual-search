def main(corpus_fname_prefix: str, model_out_fname:str, reader_type: str='mongo'):
    from supervised_models.python.train import train_model
    from supervised_models.python.corpa import generate_labelled_corpus, write_corpus

    if reader_type is not None:
        if reader_type == 'mongo':
            from supervised_models.python.mongo.mongo_reader import MongoReader
            reader = MongoReader()
        elif reader_type == 'elasticsearch':
            from supervised_models.python.elasticsearch.elasticsearch_reader import ElasticsearchReader
            reader = ElasticsearchReader()
        else:
            raise RuntimeError("Unknown reader type: %s" % reader_type)

        pages = reader.load_pages()
        print("Loaded %d pages" % len(pages))

        corpus = generate_labelled_corpus(pages)
        print("Corpus contains %d lines" % len(corpus))

        write_corpus(corpus_fname_prefix, corpus, randomize=True)

    model = train_model(corpus_fname_prefix, model_out_fname, label_prefix='__label__')

    valid_fname = "%s.valid" % corpus_fname_prefix
    for k in [1, 5]:
        N, P, R = model.test(valid_fname, k)
        print("Total number of samples=", N)
        print("P@%d=" % k, P)
        print("R@%d=" % k, R)


def print_usage(argv):
    print("Usage (existing corpus): python %s <corpus_fname_prefix> <model_out_fname>" % argv[0])
    print("Usage (build corpus + model): python %s <corpus_fname_prefix> <model_out_fname> <reader_type>" % argv[0])
    exit()


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print_usage(sys.argv)

    corpus_fname_prefix = sys.argv[1]
    model_out_fname = sys.argv[2]

    reader_type = None
    if len(sys.argv) == 4:
        reader_type = sys.argv[3]

    main(corpus_fname_prefix, model_out_fname, reader_type=reader_type)

