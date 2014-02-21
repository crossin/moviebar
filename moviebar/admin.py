import urllib2
import json
import re
from django import forms
from django.contrib import admin, messages
from django.template.response import TemplateResponse

from . import models


class TagAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'selected']


class MovieAdmin(admin.ModelAdmin):
    def tag(self, obj):
        return ', '.join(obj.tags.values_list('name', flat=True))

    list_display = ['id', 'name', 'tag', 'filename', 'photo', 'description',
                    'newest_score', 'hottest_score', 'classic_score',
                    'douban_id', 'score_imdb']
    actions = ['add_tag', 'get_douban_info', 'get_cover_image', 'get_imdb']
    search_fields = ['name']

    class AddTagForm(forms.Form):
        tags = forms.CharField()
        _selected_action = forms.CharField(widget=forms.MultipleHiddenInput)

    def add_tag(self, request, queryset):
        if request.POST.get('addtag'):
            form = MovieAdmin.AddTagForm(request.POST)
            if form.is_valid():
                tags = form.cleaned_data['tags'].split()
                for movie in queryset:
                    for t in tags:
                        tag, c = models.Tag.objects.get_or_create(name=t)
                        movie.tags.add(tag)
                messages.success(request,
                                 ('%d tags added to %d exps.'
                                  % (len(tags), len(queryset))))
            else:
                raise forms.ValidationError('form error')
        else:
            form = MovieAdmin.AddTagForm()
            context = {
                'queryset': queryset,
                'action_checkbox_name': admin.helpers.ACTION_CHECKBOX_NAME,
                'form': form,
            }
            return TemplateResponse(request, 'addtag.html',
                                    context, current_app=self.admin_site.name)

    def get_douban_info(self, request, queryset):
        count = queryset.count()
        i = 0
        for movie in queryset:
            url = 'http://api.douban.com/v2/movie/subject/%s' % movie.douban_id
            resp = urllib2.urlopen(url)
            html = resp.read()
            data = json.loads(html)
            movie.photo = data['images']['large']
            movie.english = data['original_title']
            if data['aka']:
                movie.alias = data['aka'][0]
            movie.country = data['countries'][0]
            movie.year = data['year']
            movie.score_douban = data['rating']['average']
            movie.description = data['summary']
            movie.save()
            tags = data['genres']
            for t in tags:
                tag, c = models.Tag.objects.get_or_create(name=t)
                movie.tags.add(tag)
            i += 1
            print '%d / %d' % (i, count)

    def get_cover_image(self, request, queryset):
        count = queryset.count()
        i = 0
        for movie in queryset:
            if movie.photo.startswith('http'):
                picurl = movie.photo
                pic = urllib2.urlopen(picurl).read()
                pictype = picurl.split('.')[-1]
                picname = movie.name + '.' + pictype
                from os.path import dirname, join as join_path
                file_addr = join_path(
                    dirname(__file__),
                    ('../posters/%s' % picname))
                f = file(file_addr, "wb")
                f.write(pic)
                f.close()
                movie.photo = picname
                movie.save()
            i += 1
            print '%d / %d' % (i, count)

    def get_imdb(self, request, queryset):
        count = queryset.count()
        i = 0
        for movie in queryset:
            if movie.score_imdb == 0:
                d_url = 'http://movie.douban.com/subject/%d/' % movie.douban_id
                douban = urllib2.urlopen(d_url).read()
                try:
                    r = re.search('http://www.imdb.com/title/(?P<imdb>.*?\d+)', douban)
                except:
                    r = None
                if r is None:
                    sc = 0
                else:
                    i_id = r.group('imdb')
                    url = r.group() + '/'
                try:
                    i_url = 'http://www.omdbapi.com/?i=%s' % i_id
                    resp = urllib2.urlopen(i_url)
                    html = resp.read()
                    data = json.loads(html)
                    sc = float(data['imdbRating'])
                except:
                    resp = urllib2.urlopen(url)
                    html = resp.read()
                    r = re.search('<strong><span itemprop="ratingValue">(?P<imdb>\d+.\d+)</span></strong>', html)
                    sc = float(r.group('imdb'))
                movie.score_imdb = sc
                movie.save()
            i += 1
            print '%d / %d' % (i, count)


class MessageAdmin(admin.ModelAdmin):
    list_display = ['id', 'content']

admin.site.register(models.Tag, TagAdmin)
admin.site.register(models.Movie, MovieAdmin)
admin.site.register(models.Message, MessageAdmin)
