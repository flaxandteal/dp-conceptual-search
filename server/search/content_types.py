"""
Content types lifted out of Babbage
"""


class ContentType(object):
    def __init__(self, name, weight=1.0):
        self.name = name
        self.weight = weight


# Content types
home_page = ContentType("home_page")
home_page_census = ContentType("home_page_census")
taxonomy_landing_page = ContentType("taxonomy_landing_page")
product_page = ContentType("product_page")
bulletin = ContentType("bulletin", 1.55)
article = ContentType("article", 1.30)
article_download = ContentType("article_download", 1.30)
timeseries = ContentType("timeseries", 1.20)
data_slice = ContentType("data_slice")
compendium_landing_page = ContentType("compendium_landing_page", 1.30)
compendium_chapter = ContentType("compendium_chapter")
compendium_data = ContentType("compendium_data")
static_landing_page = ContentType("static_landing_page")
static_article = ContentType("static_article")
static_methodology = ContentType("static_methodology")
static_methodology_download = ContentType("static_methodology_download")
static_page = ContentType("static_page")
static_qmi = ContentType("static_qmi")
static_foi = ContentType("static_foi")
static_adhoc = ContentType("static_adhoc", 1.25)
dataset = ContentType("dataset")
dataset_landing_page = ContentType("dataset_landing_page", 1.35)
timeseries_dataset = ContentType("timeseries_dataset")
release = ContentType("release")
reference_tables = ContentType("reference_tables")
chart = ContentType("chart")
table = ContentType("table")
equation = ContentType("equation")
departments = ContentType("departments")

content_types = [
    home_page,
    home_page_census,
    taxonomy_landing_page,
    product_page,
    bulletin,
    article,
    article_download,
    timeseries,
    data_slice,
    compendium_landing_page,
    compendium_chapter,
    compendium_data,
    static_landing_page,
    static_article,
    static_methodology,
    static_methodology_download,
    static_page,
    static_qmi,
    static_foi,
    static_adhoc,
    dataset,
    dataset_landing_page,
    timeseries_dataset,
    release,
    reference_tables,
    chart,
    table,
    equation,
    departments]
