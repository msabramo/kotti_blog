# -*- coding: utf-8 -*-


def test_blog_view(kotti_blog_populate_settings,
                   db_session, dummy_request):
    from kotti.resources import get_root
    from kotti_blog.resources import Blog, BlogEntry
    from kotti_blog.views import Views

    root = get_root()
    root['blog'] = Blog(u'Blog')
    root['blog']['a'] = BlogEntry()
    root['blog']['b'] = BlogEntry()
    view = Views(root['blog'], dummy_request)
    result = view.view_blog()

    assert result['macros'] is not None
    assert result['use_pagination'] is True
    assert result['api'] is not None
    assert result['link_headline'] is True
    assert len(result['items']) == 2


def test_use_auto_pagination_view(kotti_blog_populate_settings,
                                  db_session, dummy_request):
    from kotti.resources import get_root
    from kotti_blog.views import use_auto_pagination

    result = use_auto_pagination(get_root(), dummy_request)
    assert result['use_auto_pagination'] is False


def test_archives_filter(kotti_blog_populate_settings,
                         db_session, dummy_request):
    import datetime
    from dateutil.tz import tzutc
    from kotti.resources import get_root
    from kotti_blog.resources import Blog, BlogEntry
    from kotti_blog.views import Views

    root = get_root()
    root['blog'] = Blog(u'Blog')
    root['blog']['a'] = BlogEntry(title=u'Old one',
                                  date=datetime.datetime(2012, 7, 28,
                                                         tzinfo=tzutc()))
    root['blog']['b'] = BlogEntry(title=u'Old two',
                                  date=datetime.datetime(2012, 7, 29,
                                                         tzinfo=tzutc()))
    root['blog']['d'] = BlogEntry(title=u'New one',
                                  date=datetime.datetime(2013, 7, 7,
                                                         tzinfo=tzutc()))

    dummy_request.GET['selected-date'] = '2012_07'
    view = Views(root['blog'], dummy_request)
    result = view.view_blog()
    assert len(result['items']) == 2

    titles = [i.title for i in result['items']]
    assert 'Old one' in titles
    assert 'Old two' in titles
    assert 'New one' not in titles

    dummy_request.GET['selected-date'] = '2013_07'
    view = Views(root['blog'], dummy_request)
    result = view.view_blog()
    assert len(result['items']) == 1

    dummy_request.GET['selected-date'] = '2013_12'
    view = Views(root['blog'], dummy_request)
    result = view.view_blog()
    assert len(result['items']) == 0


def test_tags_filter(kotti_blog_populate_settings,
                     db_session, dummy_request):
    from kotti.resources import get_root
    from kotti_blog.resources import Blog, BlogEntry
    from kotti_blog.views import Views

    root = get_root()
    root['blog'] = Blog(u'Blog')
    root['blog']['a'] = BlogEntry(title=u'One')
    root['blog']['a'].tags = [u'a', u'b', u'a b']
    root['blog']['b'] = BlogEntry(title=u'Two')
    root['blog']['b'].tags = [u'a', 'öffi'.decode('utf-8')]

    dummy_request.GET['selected-tag'] = u'd'
    view = Views(root['blog'], dummy_request)
    result = view.view_blog()
    assert len(result['items']) == 0

    dummy_request.GET['selected-tag'] = 'a'
    view = Views(root['blog'], dummy_request)
    result = view.view_blog()
    assert len(result['items']) == 2

    dummy_request.GET['selected-tag'] = 'b'
    view = Views(root['blog'], dummy_request)
    result = view.view_blog()
    assert len(result['items']) == 1
    assert result['items'][0].title == 'One'

    dummy_request.GET['selected-tag'] = 'a b'
    view = Views(root['blog'], dummy_request)
    result = view.view_blog()
    assert len(result['items']) == 1
    assert result['items'][0].title == 'One'

    dummy_request.GET['selected-tag'] = '%C3%B6ffi'
    view = Views(root['blog'], dummy_request)
    result = view.view_blog()
    assert len(result['items']) == 1
    assert result['items'][0].title == 'Two'


def test_include_social(kotti_blog_populate_settings,
                        config, db_session, dummy_request):
    from kotti.resources import get_root
    from kotti_settings.util import set_setting
    from kotti_blog.resources import Blog, BlogEntry
    from kotti_blog.views import Views
    import fanstatic

    root = get_root()
    root['blog'] = Blog(u'Blog')
    root['blog']['a'] = BlogEntry(title=u'One')

    dummy = fanstatic.init_needed()
    set_setting('kotti_blog-include_social', False)
    view = Views(root['blog']['a'], dummy_request)
    result = view.view_blogentry()
    resources = fanstatic.get_needed().resources()
    resource_names = [res.filename for res in resources]
    assert result['include_social'] == False
    assert 'jquery.socialshareprivacy.en.js' not in resource_names

    set_setting('kotti_blog-include_social', True)
    view = Views(root['blog']['a'], dummy_request)
    result = view.view_blogentry()
    resources = fanstatic.get_needed().resources()
    resource_names = [res.filename for res in resources]
    assert result['include_social'] == True
    assert 'jquery.socialshareprivacy.en.js' in resource_names

    dummy = fanstatic.init_needed()
    settings = config.get_settings()
    settings['pyramid.default_locale_name'] = 'de'
    view = Views(root['blog']['a'], dummy_request)
    result = view.view_blogentry()
    resources = fanstatic.get_needed().resources()
    resource_names = [res.filename for res in resources]
    assert 'jquery.socialshareprivacy.en.js' not in resource_names
    assert 'jquery.socialshareprivacy.de.js' in resource_names
