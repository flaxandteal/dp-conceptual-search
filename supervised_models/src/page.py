from typing import Set, List


class Page(object):
    def __init__(self, json: dict):
        self._json = json

    def __getattr__(self, item):
        try:
            return self._json[item]
        except KeyError:
            pass
        # If that fails, return default behavior so we don't break Python
        try:
            return self._json[item]
        except KeyError:
            raise AttributeError

    def get_corpus_sentences(self) -> List[str]:
        """
        Combines several text fields into one long text corpus and processes the sentences
        :return:
        """
        from supervised_models.src.utils import parse_sentences

        if self.has_description():
            fields = ['title', 'headline1', 'headline2', 'headline3', 'summary']
            description = self.description

            sentences = []
            for field in fields:
                if field in description:
                    text = description[field]
                    sentences.extend(text.split("."))

            # Handle markdown sections
            if 'sections' in self._json:
                from supervised_models.src.corpa import markdown_to_text
                sections = self.sections
                for section in sections:
                    if "title" in section:
                        text = section["title"]
                        sentences.extend(text.split("."))
                    if "markdown" in section:
                        text = markdown_to_text(section["markdown"])
                        sentences.extend(text.split("."))
            return parse_sentences(sentences)
        return None

    def has_description(self):
        return "description" in self._json and isinstance(self.description, dict)

    def has_keywords(self):
        return self.has_description() and "keywords" in self.description

    def get_labels(self) -> Set[str]:
        if self.has_keywords():
            from supervised_models.src.utils import parse
            keywords = self.description["keywords"]

            labels = []
            for entry in keywords:
                if ',' in entry:
                    entry = entry.split(',')

                if isinstance(entry, str):
                    labels.append(parse(entry))
                elif hasattr(entry, "__iter__"):
                    labels.extend([parse(keyword) for keyword in entry])

            return set(labels)
        return set()
