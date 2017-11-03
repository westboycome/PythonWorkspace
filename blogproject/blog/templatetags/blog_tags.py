#存放自定义的模板标签代码
from ..models import Post, Category, Tag
from django import template
from django.db.models.aggregates import Count

#实例化
register = template.Library()

#获取数据库中前 num 篇文章，这里 num 默认为 5
#装饰
@register.simple_tag
def get_recent_posts(num=5):
    return Post.objects.all().order_by('-created_time')[:num]

#dates 方法会返回一个列表，列表中的元素为每一篇文章的创建时间,精确到月份，降序排列
#
@register.simple_tag
def archives():
    return Post.objects.dates('created_time', 'month', order='DESC')

@register.simple_tag
def get_categories():
    return Category.objects.annotate(num_posts=Count('post')).filter(num_posts__gt=0)

@register.simple_tag
def get_tags():
    return Tag.objects.annotate(num_posts=Count('post')).filter(num_posts__gt=0)