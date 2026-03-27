#!/usr/bin/env python3
from flask import Flask,render_template_string,jsonify
import json,os,requests
from bs4 import BeautifulSoup
from datetime import datetime

app=Flask(__name__)
DATA_DIR=os.path.join(os.path.dirname(__file__),'data')
os.makedirs(DATA_DIR,exist_ok=True)

HEADERS={'User-Agent':'Mozilla/5.0'}

def fetch(url):
    try:
        r=requests.get(url,headers=HEADERS,timeout=8)
        r.encoding='utf-8'
        return r.text
    except:return None

def scrape():
    data=[]
    # 党政政策
    for url,src,cat in [
        ('http://www.gov.cn/zhengce/index.htm','中国政府网','国务院文件'),
        ('http://www.xinhuanet.com/politics/','新华网','时政'),
    ]:
        html=fetch(url)
        if html:
            soup=BeautifulSoup(html,'html.parser')
            for a in soup.select('h3 a,h2 a')[:5]:
                t=a.get_text().strip()
                if t and len(t)>5:
                    href=a.get('href','')
                    if href and not href.startswith('http'):
                        href='http://www.gov.cn'+href
                    data.append({'title':t,'url':href,'source':src,'category':cat,'date':datetime.now().strftime('%Y-%m-%d'),'type':'policy'})
    # 新闻
    for url,src,cat in [
        ('https://news.cctv.com/','央视新闻','国内'),
        ('https://www.bbc.com/news/world','BBC','国际'),
    ]:
        html=fetch(url)
        if html:
            soup=BeautifulSoup(html,'html.parser')
            for a in soup.select('h3 a,h2 a')[:5]:
                t=a.get_text().strip()
                if t and len(t)>10:
                    data.append({'title':t,'url':url,'source':src,'category':cat,'date':datetime.now().strftime('%Y-%m-%d'),'type':'news'})
    # 示例数据
    if len(data)<3:
        data.append({'title':'习近平主持召开中央深改委会议','url':'http://www.gov.cn','source':'中国政府网','category':'中央会议','date':datetime.now().strftime('%Y-%m-%d'),'type':'policy'})
        data.append({'title':'全球股市今日涨跌互现','url':'https://www.reuters.com','source':'Reuters','category':'财经','date':datetime.now().strftime('%Y-%m-%d'),'type':'news'})
    with open(os.path.join(DATA_DIR,'data.json'),'w',encoding='utf-8')as f:
        json.dump(data,f,ensure_ascii=False,indent=2)
    return data

def load():
    p=os.path.join(DATA_DIR,'data.json')
    if os.path.exists(p):
        with open(p,'r',encoding='utf-8')as f:return json.load(f)
    return[]

scrape()

HTML='''<!DOCTYPE html>
<html lang="zh">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>资讯聚合</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:'PingFang SC',sans-serif;background:linear-gradient(135deg,#1a1a2e,#16213e);min-height:100vh;color:#eee}
.header{background:linear-gradient(90deg,#667eea,#764ba2);padding:25px;text-align:center}
.header h1{font-size:24px}
.container{max-width:900px;margin:0 auto;padding:20px}
.toolbar{display:flex;gap:10px;margin-bottom:20px;flex-wrap:wrap}
.search{flex:1;min-width:200px}
.search input{width:100%;padding:10px;border-radius:20px;background:rgba(255,255,255,0.1);border:none;color:#fff;font-size:14px}
.btn{padding:8px 16px;border-radius:20px;background:transparent;border:1px solid rgba(255,255,255,0.3);color:#fff;cursor:pointer}
.btn:hover,.btn.active{background:#667eea}
.grid{display:grid;gap:12px}
.card{background:rgba(255,255,255,0.08);border-radius:10px;padding:18px}
.card a{color:#fff;text-decoration:none;font-size:15px}
.card a:hover{color:#667eea}
.meta{display:flex;gap:8px;margin-top:10px;flex-wrap:wrap}
.badge{padding:3px 10px;border-radius:10px;font-size:11px;background:rgba(102,126,234,0.2);color:#a5b4fc}
.fab{position:fixed;bottom:30px;right:30px;width:50px;height:50px;border-radius:50%;background:linear-gradient(135deg,#667eea,#764ba2);border:none;color:#fff;font-size:20px;cursor:pointer}
</style>
</head>
<body>
<div class="header"><h1>📰 资讯聚合平台</h1><p>党政政策 · 全球新闻</p></div>
<div class="container">
<div class="toolbar">
<div class="search"><input type="text" placeholder="搜索..." oninput="render()"></div>
<button class="btn active" onclick="setType('all')">全部</button>
<button class="btn" onclick="setType('policy')">政策</button>
<button class="btn" onclick="setType('news')">新闻</button>
</div>
<div style="margin-bottom:15px">共 <span id="c">0</span> 条</div>
<div class="grid" id="g"></div>
</div>
<button class="fab" onclick="refresh()">↻</button>
<script>
let data=[],cur='all';
function load(){fetch('/api/data').then(r=>r.json()).then(d=>{data=d;render();document.getElementById('c').textContent=d.length})}
function render(){let f=cur==='all'?data:data.filter(x=>x.type===cur);let s=document.querySelector('.search input').value.toLowerCase();if(s)f=f.filter(x=>x.title.toLowerCase().includes(s));document.getElementById('g').innerHTML=f.length?f.map(x=>`<div class="card"><a href="${x.url}" target="_blank">${x.title}</a><div class="meta"><span class="badge">${x.source}</span><span class="badge">${x.category}</span><span class="badge">${x.date}</span></div></div>`).join(''):'暂无数据'}
function setType(t){cur=t;document.querySelectorAll('.btn').forEach(b=>b.classList.remove('active'));event.target.classList.add('active');render()}
function refresh(){fetch('/api/refresh',{method:'POST'}).then(()=>load())}
load();
</script>
</body>
</html>'''

@app.route('/')
def idx():return render_template_string(HTML)
@app.route('/api/data')
def api():return jsonify(load())
@app.route('/api/refresh',methods=['POST'])
def ref():import subprocess,system as s;subprocess.run([s.executable,__file__],capture_output=True,timeout=120);return jsonify({'ok':1})

if __name__=='__main__':
    app.run(host='0.0.0.0',port=int(os.environ.get('PORT',5000)))
