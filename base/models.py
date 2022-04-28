from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class Plan(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(null=True,blank=True)
    level=models.IntegerField()

    def __str__(self):
        return self.title

class Subject(models.Model):
    name = models.TextField()
    description = models.TextField(null=True,blank=True)

    def __str__(self):
        return self.name

class Question(models.Model):
    question = models.TextField()
    subject = models.ForeignKey(Subject,on_delete=models.CASCADE, null=False, blank=False)
    hint = models.TextField(null=True,blank=True)
    plan = models.ForeignKey(Plan,on_delete=models.SET_NULL, null=True, blank=False)

    def __str__(self):
        return self.question

class Option(models.Model):
    question = models.ForeignKey(Question,on_delete=models.CASCADE, null=False, blank=False)
    option = models.TextField()
    is_answer = models.BooleanField(default=False)

    def __str__(self):
        return self.option

class History(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE, null=False, blank=False)
    plan = models.ForeignKey(Plan,on_delete=models.DO_NOTHING, null=False, blank=False)
    subject = models.ForeignKey(Subject,on_delete=models.DO_NOTHING, null=True, blank=False)
    score = models.DecimalField(max_digits=5,decimal_places=2,null=True,blank=True)
    complete = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    complete_at = models.DateTimeField(null=True,blank=True)

    def __str__(self):
        return str(self.plan.id) +'-'+ self.user.username
    def getScore(self):
        return self.score*10
    class Meta:
        ordering = ['created']


class Arcade(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE, null=False, blank=False)
    plan = models.ForeignKey(Plan,on_delete=models.CASCADE, null=False, blank=False)
    history = models.ForeignKey(History,on_delete=models.CASCADE, null=False, blank=False)
    question = models.ForeignKey(Question,on_delete=models.CASCADE, null=False, blank=False)
    selected = models.ForeignKey(Option,on_delete=models.DO_NOTHING, null=True, blank=True)
    selected_as_text = models.TextField(null=True, blank=True)
    passed = models.BooleanField(default=False)
    is_last_viewed = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)

