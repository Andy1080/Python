import requests

r = requests.get('https://api.github.com/events')

#r = requests.post("http://httpbin.org/post")
#r = requests.put("http://httpbin.org/put")
#r = requests.delete("http://httpbin.org/delete")
#r = requests.head("http://httpbin.org/get")
#r = requests.options("http://httpbin.org/get")

out = r.json()
reponames = [x['repo']['name'] for x in out]
print reponames