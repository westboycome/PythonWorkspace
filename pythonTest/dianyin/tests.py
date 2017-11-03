from django.test import TestCase
from .dytt import dytt8
# Create your tests here.

t = dytt8(4)
print(t.list_url())
for url in t.http_url():
    print(url)