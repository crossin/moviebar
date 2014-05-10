#-*- coding: utf-8 -*-
import os

from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.db.models import Q
from django.template.response import TemplateResponse
from . import models


def home(request):
    newest = models.Movie.objects.filter(newest_score__gt=0).exclude(filename='').order_by('-newest_score')[:7]
    hottest = models.Movie.objects.filter(hottest_score__gt=0).exclude(filename='').order_by('-hottest_score')[:7]
    classic = models.Movie.objects.filter(classic_score__gt=0).exclude(filename='').order_by('-classic_score')[:7]
    tags = models.Tag.objects.filter(selected=True)[:7]
    messages = models.Message.objects.all()
    return TemplateResponse(
        request,
        'home.html',
        {
            'newest': newest,
            'hottest': hottest,
            'classic': classic,
            'tags': tags,
            'msgs': messages,
        })


def alltags(request):
    start = int(request.GET.get('start', 1))
    count = models.Tag.objects.count()
    tags = models.Tag.objects.all().order_by('-score')[24 * (start - 1):24 * start]
    pages = count / 24 + 1
    return TemplateResponse(
        request,
        'alltags.html',
        {
            'tags': tags,
            'pages': pages,
            'start': start,
        })


def tag(request, tag_id):
    tag = models.Tag.objects.get(id=tag_id)
    start = int(request.GET.get('start', 1))
    count = tag.movies.exclude(filename='').count()
    movies = tag.movies.exclude(filename='').order_by('-score_douban')[12 * (start - 1):12 * start]
    pages = count / 12 + 1
    return TemplateResponse(
        request,
        'tag.html',
        {
            'tag': tag,
            'movies': movies,
            'pages': pages,
            'start': start,
        })


def selected(request):
    movie_type = request.GET.get('type', 'newest')
    start = int(request.GET.get('start', 1))
    if movie_type == 'classic':
        allmovies = models.Movie.objects.filter(classic_score__gt=0).exclude(filename='').order_by('-classic_score')
        name = u"经典好片"
    elif movie_type == 'hottest':
        allmovies = models.Movie.objects.filter(hottest_score__gt=0).exclude(filename='').order_by('-hottest_score')
        name = u"本周热门"
    else:
        allmovies = models.Movie.objects.filter(newest_score__gt=0).exclude(filename='').order_by('-newest_score')
        name = u"新片推荐"
    count = allmovies.count()
    movies = allmovies[12 * (start - 1):12 * start]
    pages = count / 12 + 1
    return TemplateResponse(
        request,
        'selected.html',
        {
            'type': movie_type,
            'type_name': name,
            'movies': movies,
            'pages': pages,
            'start': start,
        })


def movie(request, movie_id):
    movie = models.Movie.objects.get(id=movie_id)
    if request.GET.get('play', '0') == '1':
        # to change on windows
        '''
        os.system(
            'totem "%s"' %
            (settings.STATICFILES_DIRS[0] + movie.filename.encode('utf-8'))
        )'''
        import win32api
        movie_file = movie.filename
        win32api.ShellExecute(0, 'open', movie_file, '','',1)

    tags = movie.tags.all()[:4]
    if len(movie.description) > 310:
        movie.description = movie.description[:310] + '...'
    return TemplateResponse(
        request,
        'movie.html',
        {
            'movie': movie,
            'tags': tags,
        })


@login_required
def update_create_from_file(request):
    newadd = []
    if request.method == 'POST':
        path = settings.STATICFILES_DIRS[0]
        files = os.listdir(path)
        movies = [f for f in files if f.split('.')[-1] in settings.MOVIE_TYPES]
        for movie in movies:
            if not models.Movie.objects.filter(filename=movie).exists():
                name = ''.join(movie.split('.')[:-1])
                photo = next(
                    (f for f in files if name == ''.join(
                        f.split('.')[:-1]) and f != movie),
                    '')
                models.Movie.objects.create(name=name,
                                            filename=movie,
                                            photo=photo)
                newadd.append(name)

    return TemplateResponse(
        request,
        'update.html',
        {
            'newadd': newadd,
        })


@login_required
def update_get_filename(request):
    newadd = []
    if request.method == 'POST':
        # path 1
        for i in (0, 1):
            path = settings.STATICFILES_DIRS[i]
            files = os.listdir(path)
            files = [f.decode('cp936') for f in files]
            movies = models.Movie.objects.all()
            for movie in movies:
                filename = movie.year + movie.name
                path_file = next(
                    (f for f in files if filename == ''.join(
                        f.split('.')[:-1])),
                    '')
                if path_file:
                    movie.filename = path + path_file
                    movie.save()
                    newadd.append(path+path_file)
    return TemplateResponse(
        request,
        'update.html',
        {
            'newadd': newadd,
        })


@login_required
def update(request):
    newadd = []
    if request.method == 'POST':
        # update files to list
        if 'update' in request.POST:
            for i in (0, 1):
                path = settings.STATICFILES_DIRS[i]
                files = os.listdir(path)
                files = [f.decode('cp936') for f in files]
#                files = [f.decode('utf8') for f in files]
                files = [f for f in files if f.split('.')[-1] in settings.MOVIE_TYPES]
                from os.path import dirname, join as join_path
                id_file = join_path(dirname(__file__), './movie-ids.txt')
                import codecs
                f = codecs.open(id_file, 'r', 'utf-8')
#                f = open(id_file, 'r')
                doubans = f.readlines()
                f.close()
                count = len(files)
                j = 0
                for f in files:
                    name = ''.join(f.split('.')[:-1])[4:]
                    print name
                    movie, c = models.Movie.objects.get_or_create(name=name)
                    if movie.filename == '':
                        movie.filename = path + f
                        movie.save()
                        newadd.append(f)
                    if movie.douban_id is None:
                        for douban in doubans:
                            if name in douban:
                                did = douban.split()[0]
                                movie.douban_id = did
                                movie.save()
                    j += 1
                    print 'folder %d: %d / %d' % (i, j, count)
        elif 'check' in request.POST:
            movies = models.Movie.objects.all()
            movie_files = []
            for i in (0, 1):
                path = settings.STATICFILES_DIRS[i]
                files = os.listdir(path)
                files = [f.decode('cp936') for f in files]
#                files = [f.decode('utf8') for f in files]
                movie_files += [f for f in files if f.split('.')[-1] in settings.MOVIE_TYPES]
            names = [''.join(f.split('.')[:-1])[4:] for f in movie_files]
            print movie_files
            print [m.name for m in movies]
            print names
            for m in movies:
                if m.name not in names:
                    newadd.append(m.name)
        elif 'list' in request.POST:
            movies = models.Movie.objects.all()
            from os.path import dirname, join as join_path
            list_file = join_path(dirname(__file__), './movie-list.txt')
            import codecs
            f = codecs.open(list_file, 'r', 'utf-8')
            movie_list = f.readlines()
            f.close()
            for m in movie_list:
                year = m[:4]
                name = m[4:].strip()
                print [name]
                if not models.Movie.objects.filter(
                        name=name, year=year).exists():
                    newadd.append(m)
    return TemplateResponse(
        request,
        'update.html',
        {
            'newadd': newadd,
        })


def coupon(request):
    return TemplateResponse(
        request,
        'coupon.html',
        {})


def search(request):
    movies = None
    keyword = ''
    start = int(request.GET.get('start', 1))
    pages = 1
    keyword = request.GET.get('keyword', '').strip()
    count = 0
    if keyword:
        all_movies = models.Movie.objects.exclude(filename='').filter(
            Q(name__contains=keyword)
            | Q(alias__contains=keyword)
            | Q(english__contains=keyword)
        ).order_by('-year')
        count = all_movies.count()
        movies = all_movies[12 * (start - 1):12 * start]
        pages = count / 12 + 1
    if count == 1:
        from django.shortcuts import redirect
        return redirect('/movie/%d' % movies[0].id)
    return TemplateResponse(
        request,
        'search.html',
        {
            'keyword': keyword,
            'movies': movies,
            'pages': pages,
            'start': start,
        })
