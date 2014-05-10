from django.db import models


class Tag(models.Model):
    name = models.CharField(max_length=30, unique=True)
    selected = models.BooleanField(default=False)
    score = models.IntegerField(default=0)

    def __unicode__(self):
        return self.name


class Movie(models.Model):
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=3000, blank=True)
    filename = models.CharField(max_length=128, blank=True)
    photo = models.CharField(max_length=128, blank=True)
    tags = models.ManyToManyField(Tag, null=True, blank=True,
                                  related_name='movies')
    newest = models.BooleanField(default=False)
    hottest = models.BooleanField(default=False)
    classic = models.BooleanField(default=False)
    newest_score = models.IntegerField(default=0)
    hottest_score = models.IntegerField(default=0)
    classic_score = models.IntegerField(default=0)
    country = models.CharField(max_length=20, blank=True)
    year = models.CharField(max_length=20, blank=True)
    score_douban = models.FloatField(default=0.0)
    score_imdb = models.FloatField(default=0.0)
    douban_id = models.IntegerField(null=True, blank=True)
    alias = models.CharField(max_length=50, blank=True)
    english = models.CharField(max_length=80, blank=True)

    def __unicode__(self):
        return self.name


class Message(models.Model):
    content = models.CharField(max_length=300)
