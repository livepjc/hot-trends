"""
读取 fetch.py 输出的 JSON，生成自包含的 HTML 页面。
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).parent
INPUT = sys.argv[1] if len(sys.argv) > 1 else HERE / "hot-data.json"
OUTPUT = HERE / "index.html"

HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>实时热点聚合 - 微博/B站/抖音</title>
<style>
:root{--bg:#0a0a12;--card:rgba(255,255,255,.03);--card-h:rgba(255,255,255,.07);--bd:rgba(255,255,255,.07);--tx:#e8e8f0;--dm:rgba(255,255,255,.45);--dy:#fe2c55;--bl:#00a1d6;--wb:#ff8200}
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,BlinkMacSystemFont,"PingFang SC","Microsoft YaHei",sans-serif;background:var(--bg);color:var(--tx);min-height:100vh;line-height:1.6}
.glow{position:fixed;inset:0;pointer-events:none;z-index:0;overflow:hidden}
.or{position:absolute;border-radius:50%;filter:blur(120px);opacity:.08}
.o1{width:500px;height:500px;background:var(--dy);top:-180px;left:-80px;animation:f1 22s ease-in-out infinite}
.o2{width:450px;height:450px;background:var(--bl);bottom:-150px;right:-80px;animation:f2 26s ease-in-out infinite}
.o3{width:350px;height:350px;background:var(--wb);top:40%;left:45%;animation:f3 20s ease-in-out infinite}
@keyframes f1{0%,100%{transform:translate(0,0)}50%{transform:translate(60px,50px)}}
@keyframes f2{0%,100%{transform:translate(0,0)}50%{transform:translate(-50px,-70px)}}
@keyframes f3{0%,100%{transform:scale(1)}50%{transform:scale(1.15)}}
.W{max-width:1440px;margin:0 auto;padding:20px 24px 40px;position:relative;z-index:1}
.hd{text-align:center;padding:24px 0 8px}
.hd h1{font-size:clamp(24px,5vw,36px);font-weight:800;background:linear-gradient(135deg,var(--dy),var(--bl),var(--wb));-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}
.hd .sub{color:var(--dm);font-size:14px;margin-top:4px}
.tabs{display:flex;justify-content:center;gap:12px;margin:20px 0;flex-wrap:wrap}
.tab{padding:10px 24px;border-radius:25px;border:1px solid var(--bd);background:var(--card);color:var(--dm);cursor:pointer;font-size:14px;transition:all .3s}
.tab:hover,.tab.on{background:var(--card-h);color:var(--tx);border-color:rgba(255,255,255,.15)}
.tab.on.dy{border-color:var(--dy);color:var(--dy)}.tab.on.bl{border-color:var(--bl);color:var(--bl)}.tab.on.wb{border-color:var(--wb);color:var(--wb)}
.cols{display:grid;grid-template-columns:repeat(3,1fr);gap:20px}
@media(max-width:900px){.cols{grid-template-columns:1fr}.W{padding:12px 14px 30px}.hd h1{font-size:22px}.hd .sub{font-size:12px}.tabs{gap:8px;margin:14px 0}.tab{padding:8px 16px;font-size:13px}.cl h2{font-size:16px}.it{padding:12px 14px;gap:10px;border-radius:10px}.rk{width:26px;height:26px;font-size:12px}.tt{font-size:14px}.ht{font-size:11px}}
.pn{display:none}.pn.on{display:block}
.cl h2{font-size:18px;font-weight:700;margin-bottom:16px;display:flex;align-items:center;gap:8px}
.cl h2 .dot{width:10px;height:10px;border-radius:50%;display:inline-block}
.cl h2 .dot.dy{background:var(--dy)}.cl h2 .dot.bl{background:var(--bl)}.cl h2 .dot.wb{background:var(--wb)}
.cl h2 .time{font-size:12px;color:var(--dm);font-weight:400;margin-left:auto}
.it{display:flex;align-items:center;gap:12px;padding:10px 16px;border-radius:12px;background:var(--card);border:1px solid var(--bd);margin-bottom:8px;transition:all .2s;cursor:pointer;text-decoration:none;color:inherit}
.it:hover{background:var(--card-h);transform:translateY(-1px)}
.rk{width:28px;height:28px;border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:13px;font-weight:700;flex-shrink:0}
.r1{background:var(--dy);color:#fff}.r2{background:#ff6b81;color:#fff}.r3{background:var(--wb);color:#fff}
.rn{background:var(--card);color:var(--dm)}
.tt{flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;font-size:14px}
.ht{font-size:12px;color:var(--dm);white-space:nowrap}
.lb{text-align:center;padding:20px;color:var(--dm)}
.ft{text-align:center;padding:20px;color:var(--dm);font-size:12px}
</style>
</head>
<body>
<div class="glow"><div class="or o1"></div><div class="or o2"></div><div class="or o3"></div></div>
<div class="W">
<div class="hd">
  <h1>实时热点聚合</h1>
  <p class="sub" id="ut">__UPDATE_TIME__</p>
</div>
<div class="tabs" id="tabs"></div>
<div class="cols" id="cols"></div>
<div class="ft">数据来源：微博 / B站 / 抖音 &nbsp;|&nbsp; 自动每5分钟更新</div>
</div>
<script>
var D=__DATA__;
var P=[{k:'weibo',n:'微博',i:'\uD83D\uDD34',c:'wb'},{k:'bilihot',n:'B\u7AD9',i:'\uD83D\uDCFA',c:'bl'},{k:'douyin',n:'\u6296\u97F3',i:'\uD83C\uDFB5',c:'dy'}];
function rc(i){return i<=1?'r r1':i<=2?'r r2':i<=3?'r r3':'r rn'}
function rl(d){
  if(!d||!d.data||!d.data.length)return '<div class="lb">\u6682\u65E0\u6570\u636E</div>';
  var h='';
  for(var i=0;i<d.data.length;i++){var it=d.data[i];
    h+='<a class="it" href="'+it.url+'" target="_blank" rel="noopener"><span class="'+rc(it.index)+'">'+it.index+'</span><span class="tt">'+it.title+'</span>'+(it.hot?'<span class="ht">'+it.hot+'</span>':'')+'</a>';}
  return h;
}
function render(){
  var t='<div class="tab on" onclick="showAll()">\uD83D\uDCCA \u5168\u90E8</div>';
  var c='';
  for(var i=0;i<P.length;i++){
    var p=P[i];t+='<div class="tab '+p.c+'" onclick="showP(\''+p.k+'\')">'+p.i+' '+p.n+'</div>';
    var d=D[p.k];
    c+='<div class="pn '+p.k+'"><div class="cl"><h2><span class="dot '+p.c+'"></span>'+p.i+' '+(d?d.title:p.n)+' '+(d?(d.subtitle||''):'')+(d&&d.update_time?'<span class="time">'+d.update_time+'</span>':'')+'</h2>'+(d?rl(d):'<div class="lb">\u6682\u65E0\u6570\u636E</div>')+'</div></div>';
  }
  document.getElementById('tabs').innerHTML=t;
  document.getElementById('cols').innerHTML=c;
  showAll();
}
function showAll(){var a=document.querySelectorAll('.pn');for(var i=0;i<a.length;i++)a[i].classList.add('on');var b=document.querySelectorAll('.tab');for(var i=0;i<b.length;i++)b[i].classList.toggle('on',i===0)}
function showP(k){var a=document.querySelectorAll('.pn');for(var i=0;i<a.length;i++)a[i].classList.toggle('on',a[i].classList.contains(k));for(var i=0;i<P.length;i++){document.querySelectorAll('.tab')[i+1].classList.toggle('on',P[i].k===k)}document.querySelectorAll('.tab')[0].classList.remove('on')}
render();
// 每5分钟自动刷新页面（GitHub Actions会更新页面内容）
setTimeout(function(){location.reload()},300000);
</script>
</body>
</html>"""


def main():
    data = json.loads(Path(INPUT).read_text(encoding="utf-8"))

    update_time = data.get("update_time", "刚刚更新")
    html = HTML_TEMPLATE.replace("__UPDATE_TIME__", f"更新于 {update_time}")
    html = html.replace("__DATA__", json.dumps(data.get("data", {}), ensure_ascii=False))

    OUTPUT.write_text(html, encoding="utf-8")
    print(f"  -> {OUTPUT.name} ({OUTPUT.stat().st_size / 1024:.0f} KB)")
    print("  DONE")


if __name__ == "__main__":
    main()
