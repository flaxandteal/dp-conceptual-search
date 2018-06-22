class Field(object):
    def __init__(self, name, boost=None, highlight=False):
        self.name = name
        self.boost = boost
        self.highlight = highlight

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

    @property
    def field_name_boosted(self):
        return "%s^%d" % (self.name, int(self.boost)
                          ) if self.boost is not None else self.name


uri = Field("uri")
# elastic search internal search score field in results
_score = Field("_score")
title_no_dates = Field("description.title.title_no_dates", 10)
title_first_letter = Field("description.title.title_first_letter")
title_raw = Field("description.title.title_raw")
title = Field("description.title", 10, highlight=True)
title_no_stem = Field("description.title.title_no_stem", 10)
title_no_synonym_no_stem = Field(
    "description.title.title_no_synonym_no_stem")  # used for suggestions
edition = Field("description.edition", highlight=True)
summary = Field("description.summary", highlight=True)
releaseDate = Field("description.releaseDate")
metaDescription = Field("description.metaDescription", highlight=True)
keywords = Field("description.keywords", highlight=True)
_type = Field("_type")
cdid = Field("description.cdid", highlight=True)
datasetId = Field("description.datasetId", highlight=True)
searchBoost = Field("searchBoost", 100)
latestRelease = Field("description.latestRelease")
published = Field("description.published")
cancelled = Field("description.cancelled")
topics = Field("topics")
embedding_vector = Field("embedding_vector")

field_list = [
    uri,
    _score,
    title_no_dates,
    title_first_letter,
    title_raw,
    title,
    title_no_stem,
    title_no_synonym_no_stem,
    edition,
    summary,
    releaseDate,
    metaDescription,
    keywords,
    _type,
    cdid,
    datasetId,
    searchBoost,
    latestRelease,
    published,
    cancelled,
    topics]

highlight_fields = [f for f in field_list if f.highlight]

suggestion_field = title_no_synonym_no_stem
