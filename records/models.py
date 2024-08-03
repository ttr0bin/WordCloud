from django.db import models

class Record(models.Model):
  category    = models.IntegerField()
  title       = models.TextField()    # 제목
  content     = models.TextField()    # 본문