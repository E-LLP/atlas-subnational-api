from atlas_core.sqlalchemy import BaseModel
from atlas_core.model_mixins import IDMixin, LanguageMixin

from sqlalchemy.ext.hybrid import hybrid_method
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
import sqlalchemy as sa
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy_searchable import make_searchable
from sqlalchemy_utils.types import TSVectorType

from sqlalchemy import cast
import psycopg2,json

# sudo apt-get install python3-dev
# to get psycopg2 in case the installation fails


db = SQLAlchemy()

Base = declarative_base()

make_searchable()

class Article(Base):
    """docstring for ""ArticleiBaseself, arg):
        super(, self).Article)Basef.arg = arg
    """
    __tablename__ = 'article_1'

    id = sa.Column(sa.Integer, primary_key= True)
    name = sa.Column(sa.Unicode(255))
    content = sa.Column(sa.UnicodeText)
    search_vector = sa.Column(TSVectorType('name', 'content'))


class I18nMixinBase(object):


    #name_en = db.Column(db.UnicodeText)
    #name_short_en = db.Column(db.Unicode(50))
    #description_en = db.Column(db.UnicodeText)

    @hybrid_method
    def get_localized(self, field, lang):
        """Look up the language localized version of a field by looking up
        field_lang."""
        return getattr(self, field + "_" + lang)

    @staticmethod
    def create(fields, languages=["en"], class_name="I18nMixin"):
        localized_fields = {}
        for name, value in fields.items():
            for language in languages:
                field_name = name + "_" + language
                localized_fields[field_name] = sa.Column(value)
        #localized_fields['search_vector'] = sa.Column(TSVectorType('name_short_en'))
        return type(class_name, (I18nMixinBase,), localized_fields)


I18nMixin = I18nMixinBase.create(
    languages=["en", "es", "de"],
    fields={
        "name": sa.UnicodeText,
        "name_short": sa.Unicode(75),
        "description": sa.UnicodeText
    })


class Metadata(Base, IDMixin, I18nMixin):
    """Baseclass for all entity metadata models. Any subclass of this class
    must have two fields:
        - a LEVELS = [] list that contains all the classification levels as
        strings
        - a db.Column(db.Enum(*LEVELS)) enum field
    """

    __abstract__ = True

    code = sa.Column(sa.Unicode(25))
    parent_id = sa.Column(sa.Integer)


class HSProduct1(Metadata):
    """A product according to the HS4 (Harmonized System) classification.
    Details can be found here: http://www.wcoomd.org/en/topics/nomenclature/instrument-and-tools/hs_nomenclature_2012/hs_nomenclature_table_2012.aspx
    """
    __bind_key__ = 'text_search'
    __tablename__ = "product_test"

    #: Possible aggregation levels
    LEVELS = [
        "section",
        "2digit",
        "4digit"
    ]
    level = sa.Column(sa.Enum(*LEVELS,name="product_level"))
    # This is the column where both name_short and name_en are stored
    name_en_test = sa.Column(sa.UnicodeText)
    #my_enum = sa.Enum('country','municipality', 'department', 'population_center', name='my_enum')

    search_vector = sa.Column(TSVectorType('name_en_test'))

from sqlalchemy.dialects.postgresql import ENUM

#from flask.ext.sqlalchemy import SQLAlchemy, BaseQuery
from sqlalchemy_searchable import search
#from sqlalchemy_searchable import SearchQueryMixin

#class LocationQuery(BaseQuery, SearchQueryMixin):
#    pass

class Location1(Metadata):
    """A geographical location. Locations have multiple levels:

    A municipality is the smallest unit of location we have and has a 5-digit
    code. Cities often contain multiple municipalities, but there are also
    standalone municipalities that are not part of any city.

    A department is a grouping of municipalities to create 32ish areas of the
    country. Departments in Colombia have 2 digit codes, which are the first 2
    digits of the 5-digit codes of the constituent municipalities."""

     # query_class = LocationQuery
    __bind_key__ = 'text_search'
    __tablename__ = "location"


    #: Possible aggregation levels
    LEVELS = [
        "country",
        "municipality",
        "department",
        "population_center"
    ]
    level = sa.Column(sa.Enum(*LEVELS, name="location_levels"))
    name_short_en_test = sa.Column(sa.UnicodeText)
    #my_enum = sa.Enum('country','municipality', 'department', 'population_center', name='my_enum')

    search_vector = sa.Column(TSVectorType('name_short_en_test'))

class Industry1(Metadata):
    """An ISIC 4 industry."""
    __bind_key__ = 'text_search'
    __tablename__ = "industry"


    #: Possible aggregation levels
    LEVELS = [
        "section",
        "division",
        "group",
        "class"
    ]
    #level = db.Column(db.Enum(*LEVELS))
    level = db.Column(db.Enum(*LEVELS, name="industry_levels"))
    name_en_test = db.Column(db.UnicodeText)
    search_vector = sa.Column(TSVectorType('name_en_test'))

#SQLALCHEMY_DATABASE_URI = "postgresql://postgres:postgres@localhost/colombia"

#SQLALCHEMY_BINDS = {
#    'text_search':        'postgresql://postgres:postgres@localhost/sqlalchemy_searchable_text'
#}
engine2 = create_engine('postgresql://postgres:postgres@localhost/atlas')
#engine2 = create_engine('postgresql://postgres:postgres@localhost/test4')
#engine = create_engine(bind=['text_search'])
#app = Flask(__name__)
#db = SQLAlchemy(app)
sa.orm.configure_mappers()  #
Base.metadata.create_all(engine2) # this is where things get created.
#db.create_all(bind=['text_search'])


def do_posgres_update():
    pass

    Session = sessionmaker(bind = engine2)
    session = Session()

    article1 = Article(name=u'third article', content=u'this is the third article')
    article2 = Article(name=u'fourth article', content=u'This is the fourth article')

    #session.add(article1)
    #session.add(article2)
    #session.commit()

# This needs to be done for each of the language
#search_vector = TSVectorType('name', regconfig='pg_catalog.finnish')





def do_location_query(search_str) :
    Session = sessionmaker(bind = engine2)
    session = Session()

    query_location = session.query(Location1)
    query_location = search(query_location, search_str,sort=True)
    #print (query_location.first().name_short_en_test)
    rl = query_location.all()
    #print (rl)
    for r in rl :
        print (r.name_short_en_test)

    return dict(location=[x.name_short_en_test for x in rl])
    #print (Location.query.search(u'pri').limit(5).all())

def do_product_query(search_str) :
    Session = sessionmaker(bind = engine2)
    session = Session()

    query_product = session.query(HSProduct1)
    query_product = search(query_product, search_str,sort=True)
    #print (query_product.first().name_en_test)
    rl = query_product.all()
    #print (rl)
    for r in rl :
        print (r.name_en_test)
    from flask import jsonify
    #return dict(product=[x.name_en_test for x in rl])
    return dict(textsearch=[{"name":x.name_en,
                            "code": x.code,
                            "description_en": x.description_en,
                            "description_es": x.description_es,
                            "level":x.level,
                            "id": x.id,
                            "name_short_en": x.name_short_en,
                            "name_short_es": x.name_short_es,
                            "parent_id": 0} for x in rl])

def do_industry_query(search_str) :
    Session = sessionmaker(bind = engine2)
    session = Session()

    query_industry = session.query(Industry1)
    query_industry = search(query_industry, search_str,sort=True)
    #print (query_industry.first().name_en_test)
    rl = query_industry.all()
    return dict(textsearch=[{"name":x.description_en,
                            "code": x.code,
                            "description_en": x.description_en,
                            "description_es": x.description_es,
                            "level":x.level,
                            "id": x.id,
                            "name_short_en": x.name_short_en,
                            "name_short_es": x.name_en_test,
                            "parent_id": 0} for x in rl])

from sqlalchemy_searchable import parse_search_query

def combined_search_query(search_str):
    Session = sessionmaker(bind = engine2)
    session = Session()
    #results_location = do_location_query(search_str)
    #results_industry = do_industry_query(search_str)
    results_product = do_product_query(search_str)
    #results = [results_industry,results_product,results_location]
    results = dict({"textsearch":results_product})
    return json.dumps(results_product)