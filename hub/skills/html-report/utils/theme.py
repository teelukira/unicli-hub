"""Frozen visual theme for the HTML report engine — "Blueprint Dossier".

A technical-document aesthetic: warm paper background, hairline rules,
monospace engineering-annotation metadata, serif section numerals,
squared precision, accent-driven via CSS custom properties.

Crafted once via the frontend-design plugin skill, then frozen here.
The report engine reuses this; reports never hand-write CSS.

CSS CLASS INVENTORY (every class report_engine.py emits MUST appear below):
  layout   : rpt, rpt-header, rpt-title, rpt-subtitle, rpt-meta,
             rpt-meta-item, rpt-meta-key, rpt-meta-val, rpt-footer
  toc      : toc, toc--horizontal, toc--vertical, toc-link, toc-index
  section  : section, section-head, section-index, section-title,
             section-status, subsection, subsection-title
  text     : text
  stats    : stat-grid, stat-card, stat-value, stat-label
  table    : table-wrap, rpt-table, group, group-cell, cell--center,
             cell--right
  progress : progress-list, progress-item, progress-label,
             progress-track, progress-fill, progress-text
  badge    : badge + modifiers (pass fail warn info success error skip new
             gap resource catalog geo ipam zone party logical), badge-row
  inline   : c-red c-green c-amber c-blue c-gray (from [c:..]); small
  legend   : legend, legend-item, legend-dot
  status   : status-grid, status-item, status-dot, status-name,
             status-meta, is-up, is-down, is-warn
  callout  : callout, callout--info/--warn/--error/--success/--gap,
             callout-label, callout-title, callout-body
  code     : code-block, code-lang
  mermaid  : mermaid-wrap, mermaid, mermaid-fallback
  details  : rpt-details
  images   : image-grid, image-card, image-caption
  semantic color modifiers shared by stat-card/badge:
             is-green is-red is-yellow is-blue is-gray is-purple
"""

from __future__ import annotations
from pathlib import Path as _Path

# --- accent palettes -------------------------------------------------------
# Each accent only redefines CSS custom properties; the base CSS uses var().
ACCENTS: dict[str, dict[str, str]] = {
    "blueprint": {
        "--accent": "#1f4e79",
        "--accent-strong": "#15395a",
        "--accent-soft": "#eaf1f8",
        "--accent-line": "#bcd2e4",
    },
    "teal": {
        "--accent": "#0f6b66",
        "--accent-strong": "#0a4d49",
        "--accent-soft": "#e2f2f0",
        "--accent-line": "#aed8d3",
    },
    "slate": {
        "--accent": "#3f4756",
        "--accent-strong": "#2a313c",
        "--accent-soft": "#eef0f3",
        "--accent-line": "#cbd1da",
    },
    "rust": {
        "--accent": "#9a4a21",
        "--accent-strong": "#763717",
        "--accent-soft": "#f7ece5",
        "--accent-line": "#e2c5b3",
    },
    "indigo": {
        "--accent": "#3a3f8c",
        "--accent-strong": "#2a2e6b",
        "--accent-soft": "#ecedf7",
        "--accent-line": "#c6c8e4",
    },
}
DEFAULT_ACCENT = "blueprint"

MERMAID_CDN = "https://cdn.jsdelivr.net/npm/mermaid@11.4/dist/mermaid.min.js"
# Local cache for offline/static HTML builds (gitignored)
MERMAID_CACHE: _Path = _Path(__file__).parent / "_mermaid@11.4.min.js"

# Post-render JS: fixes SVG width attr (Mermaid sets width="100%"; we need
# the natural pixel width so overflow-x:auto on the wrapper actually scrolls)
# and injects a fullscreen expand button + zoom/pan modal for every diagram.
MERMAID_ENHANCE_JS = r"""(function(){
  function fixSvg(svg){
    var vb=svg.getAttribute('viewBox');
    if(!vb)return;
    var p=vb.trim().split(/\s+/).map(parseFloat);
    if(p.length<4||!(p[2]>0))return;
    svg.setAttribute('width',p[2]);
    svg.setAttribute('height',p[3]);
    svg.style.maxWidth='none';
    svg.style.display='block';
  }
  var _modal=null,_canvas=null,_svg=null;
  var _scale=1,_tx=0,_ty=0,_drag=false,_lx=0,_ly=0;
  function mkModal(){
    var m=document.createElement('div');
    m.className='dgm-modal';
    m.innerHTML=
      '<div class="dgm-toolbar">'+
      '<button class="dgm-tb-btn" data-act="zin" title="확대 (+)">＋</button>'+
      '<button class="dgm-tb-btn" data-act="zout" title="축소 (−)">－</button>'+
      '<button class="dgm-tb-btn" data-act="fit" title="맞춤 (0)">⊡</button>'+
      '<span class="dgm-tb-sep"></span>'+
      '<button class="dgm-tb-btn dgm-close" data-act="close" title="닫기 (ESC)">✕</button>'+
      '</div>'+
      '<div class="dgm-canvas"></div>';
    document.body.appendChild(m);
    _canvas=m.querySelector('.dgm-canvas');
    m.querySelector('.dgm-toolbar').addEventListener('click',function(e){
      var b=e.target.closest('[data-act]');if(!b)return;
      var a=b.dataset.act;
      if(a==='zin')zoom(1.25,null,null);
      else if(a==='zout')zoom(0.8,null,null);
      else if(a==='fit')fitDgm();
      else if(a==='close')closeModal();
    });
    _canvas.addEventListener('wheel',function(e){
      e.preventDefault();
      var r=_canvas.getBoundingClientRect();
      zoom(e.deltaY<0?1.1:1/1.1,e.clientX-r.left,e.clientY-r.top);
    },{passive:false});
    _canvas.addEventListener('mousedown',function(e){
      if(e.button!==0)return;
      _drag=true;_lx=e.clientX;_ly=e.clientY;
    });
    window.addEventListener('mousemove',function(e){
      if(!_drag)return;
      _tx+=e.clientX-_lx;_ty+=e.clientY-_ly;
      _lx=e.clientX;_ly=e.clientY;applyT();
    });
    window.addEventListener('mouseup',function(){_drag=false;});
    var _pd=0,_ps=1;
    _canvas.addEventListener('touchstart',function(e){
      e.preventDefault();
      if(e.touches.length===1){_lx=e.touches[0].clientX;_ly=e.touches[0].clientY;}
      else if(e.touches.length===2){
        _pd=Math.hypot(e.touches[1].clientX-e.touches[0].clientX,e.touches[1].clientY-e.touches[0].clientY);
        _ps=_scale;
      }
    },{passive:false});
    _canvas.addEventListener('touchmove',function(e){
      e.preventDefault();
      if(e.touches.length===1){
        _tx+=e.touches[0].clientX-_lx;_ty+=e.touches[0].clientY-_ly;
        _lx=e.touches[0].clientX;_ly=e.touches[0].clientY;applyT();
      } else if(e.touches.length===2&&_pd>0){
        var d=Math.hypot(e.touches[1].clientX-e.touches[0].clientX,e.touches[1].clientY-e.touches[0].clientY);
        _scale=Math.max(0.1,Math.min(8,_ps*d/_pd));applyT();
      }
    },{passive:false});
    document.addEventListener('keydown',function(e){
      if(!_modal||!_modal.classList.contains('open'))return;
      if(e.key==='Escape')closeModal();
      else if(e.key==='+'||e.key==='=')zoom(1.2,null,null);
      else if(e.key==='-'||e.key==='_')zoom(1/1.2,null,null);
      else if(e.key==='0')fitDgm();
    });
    return m;
  }
  function getModal(){return _modal||(_modal=mkModal());}
  function applyT(){
    if(!_svg)return;
    _svg.style.transform='translate('+_tx.toFixed(1)+'px,'+_ty.toFixed(1)+'px) scale('+_scale.toFixed(4)+')';
  }
  function zoom(f,cx,cy){
    var os=_scale;
    _scale=Math.max(0.1,Math.min(8,_scale*f));
    if(cx!=null){_tx=cx-(cx-_tx)*(_scale/os);_ty=cy-(cy-_ty)*(_scale/os);}
    applyT();
  }
  function fitDgm(){
    if(!_svg||!_canvas)return;
    var cw=_canvas.clientWidth,ch=_canvas.clientHeight;
    var sw=parseFloat(_svg.getAttribute('width'))||400;
    var sh=parseFloat(_svg.getAttribute('height'))||300;
    _scale=Math.min(cw/sw,ch/sh)*0.88;
    _tx=(cw-sw*_scale)/2;_ty=(ch-sh*_scale)/2;
    applyT();
  }
  function openModal(wrap){
    var m=getModal();
    _canvas.innerHTML='';
    var orig=wrap.querySelector('svg');
    if(orig){
      _svg=orig.cloneNode(true);
      _svg.style.cssText='display:block;max-width:none!important;position:absolute;top:0;left:0;transform-origin:0 0;';
      _canvas.appendChild(_svg);
    }
    _scale=1;_tx=0;_ty=0;
    m.classList.add('open');
    document.body.style.overflow='hidden';
    setTimeout(fitDgm,60);
  }
  function closeModal(){
    if(!_modal)return;
    _modal.classList.remove('open');
    document.body.style.overflow='';
    _svg=null;
  }
  function addBtn(wrap){
    if(wrap.querySelector('.dgm-expand'))return;
    var b=document.createElement('button');
    b.className='dgm-expand';b.title='전체화면으로 보기';
    b.innerHTML='&#x26F6;';
    b.onclick=function(e){e.stopPropagation();openModal(wrap);};
    wrap.appendChild(b);
  }
  function enhance(){
    document.querySelectorAll('.mermaid-wrap').forEach(function(w){
      var s=w.querySelector('svg');if(s){fixSvg(s);addBtn(w);}
    });
  }
  var tries=0;
  function poll(){if(document.querySelector('.mermaid svg')||tries++>25)enhance();else setTimeout(poll,150);}
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',function(){setTimeout(poll,100);});
  else setTimeout(poll,100);
  setTimeout(enhance,3500);
})();"""

MERMAID_INIT = (
    "mermaid.initialize({startOnLoad:true,theme:'neutral',"
    "fontFamily:'IBM Plex Sans, sans-serif',"
    "flowchart:{useMaxWidth:false,nodeSpacing:60,rankSpacing:90,padding:20},"
    "er:{useMaxWidth:false,diagramPadding:30},"
    "themeVariables:{primaryColor:'#eaf1f8',primaryBorderColor:'#1f4e79',"
    "lineColor:'#5a6573',nodeBorder:'#1f4e79',clusterBkg:'#f0f5fa',"
    "clusterBorder:'#1f4e79',fontSize:'16px',edgeLabelBackground:'#ffffff'}});"
)


def accent_root(name: str) -> str:
    """Return a `:root` CSS block for the given accent (falls back to default)."""
    vals = ACCENTS.get(name, ACCENTS[DEFAULT_ACCENT])
    body = "".join(f"{k}:{v};" for k, v in vals.items())
    return f":root{{{body}}}"


# --- frozen stylesheet -----------------------------------------------------
THEME_CSS = r"""
:root{
  --paper:#faf8f4; --paper-2:#f3efe7; --ink:#1b1d21; --ink-soft:#5a6066;
  --line:#d8d2c6; --line-soft:#e7e2d7;
  --ok:#2f7d4f; --ok-soft:#e6f1ea; --bad:#bf3b2f; --bad-soft:#f8e7e5;
  --warn:#b07514; --warn-soft:#f7eed9; --info:#2b6cb0; --info-soft:#e6eef7;
  --gap:#7b4ea8; --gap-soft:#efe8f6;
  --mono:'IBM Plex Mono',ui-monospace,'SF Mono',Menlo,Consolas,monospace;
  --sans:'IBM Plex Sans',-apple-system,'Segoe UI',sans-serif;
  --serif:'IBM Plex Serif',Georgia,'Times New Roman',serif;
}

*{box-sizing:border-box;margin:0;padding:0}
html{-webkit-text-size-adjust:100%}
body{
  font-family:var(--sans); color:var(--ink); background:var(--paper);
  line-height:1.6; font-size:15px; -webkit-font-smoothing:antialiased;
  padding:40px 24px 80px;
}
@media screen and (min-width:760px){
  body{
    background-image:
      linear-gradient(var(--line-soft) 1px,transparent 1px),
      linear-gradient(90deg,var(--line-soft) 1px,transparent 1px);
    background-size:28px 28px; background-position:-1px -1px;
  }
}
a{color:var(--accent); text-decoration:none}
a:hover{text-decoration:underline; text-underline-offset:2px}
code{
  font-family:var(--mono); font-size:.86em; background:var(--paper-2);
  border:1px solid var(--line-soft); border-radius:2px; padding:.05em .35em;
  color:var(--accent-strong);
}
small{font-size:.82em; color:var(--ink-soft)}
strong{font-weight:600}

/* ---- main frame --------------------------------------------------------- */
.rpt{
  max-width:1180px; margin:0 auto; background:var(--paper);
  border:1px solid var(--line); box-shadow:0 1px 0 var(--line),
  0 18px 50px -28px rgba(27,29,33,.4);
}

/* ---- header ------------------------------------------------------------- */
.rpt-header{
  position:relative; padding:38px 44px 30px;
  border-bottom:3px double var(--line);
  background:
    linear-gradient(180deg,var(--accent-soft),transparent 90%);
}
.rpt-header::before,.rpt-header::after{
  content:""; position:absolute; width:14px; height:14px;
  border:1.5px solid var(--accent);
}
.rpt-header::before{top:12px; left:12px; border-right:0; border-bottom:0}
.rpt-header::after{bottom:12px; right:12px; border-left:0; border-top:0}
.rpt-kicker{
  font-family:var(--mono); font-size:11px; letter-spacing:.22em;
  text-transform:uppercase; color:var(--accent); margin-bottom:10px;
  display:flex; align-items:center; gap:8px;
}
.rpt-kicker::before{
  content:""; width:22px; height:2px; background:var(--accent); display:inline-block;
}
.rpt-title{
  font-family:var(--serif); font-weight:700; font-size:34px;
  line-height:1.18; letter-spacing:-.012em; color:var(--ink);
}
.rpt-subtitle{
  margin-top:8px; font-size:15.5px; color:var(--ink-soft); max-width:62ch;
}
.rpt-meta{
  margin-top:22px; display:grid;
  grid-template-columns:repeat(auto-fill,minmax(220px,1fr));
  border-top:1px solid var(--line); border-left:1px solid var(--line);
}
.rpt-meta-item{
  border-right:1px solid var(--line); border-bottom:1px solid var(--line);
  padding:9px 14px; background:rgba(255,255,255,.5);
}
.rpt-meta-key{
  font-family:var(--mono); font-size:9.5px; letter-spacing:.16em;
  text-transform:uppercase; color:var(--ink-soft); display:block;
}
.rpt-meta-val{
  font-family:var(--mono); font-size:13px; color:var(--ink); margin-top:3px;
}

/* ---- table of contents -------------------------------------------------- */
.toc--horizontal{
  position:sticky; top:0; z-index:30;
  display:flex; flex-wrap:wrap; gap:2px;
  padding:8px 44px; background:var(--accent-strong);
  border-bottom:1px solid var(--accent-strong);
}
.toc--horizontal .toc-link{
  font-family:var(--mono); font-size:11.5px; color:#dfe7ee;
  padding:4px 10px; border-radius:2px; white-space:nowrap;
}
.toc--horizontal .toc-link:hover{background:rgba(255,255,255,.14); text-decoration:none}
.toc--horizontal .toc-index{color:var(--accent-line); margin-right:5px}
.toc--vertical{
  margin:28px 44px 0; padding:18px 22px; background:var(--paper-2);
  border:1px solid var(--line); border-left:3px solid var(--accent);
}
.toc--vertical .toc-title{
  font-family:var(--mono); font-size:10.5px; letter-spacing:.18em;
  text-transform:uppercase; color:var(--accent); margin-bottom:10px;
}
.toc--vertical ol{list-style:none; columns:2; column-gap:34px}
.toc--vertical .toc-link{
  display:block; padding:4px 0; font-size:14px; color:var(--ink);
  border-bottom:1px dotted var(--line);
}
.toc--vertical .toc-link:hover{color:var(--accent)}
.toc--vertical .toc-index{
  font-family:var(--mono); font-size:11px; color:var(--accent);
  margin-right:8px;
}

/* ---- sections ----------------------------------------------------------- */
.section{
  padding:34px 44px; border-bottom:1px solid var(--line-soft);
  animation:rpt-rise .5s cubic-bezier(.2,.7,.2,1) both;
}
.section:nth-child(1){animation-delay:.02s}
.section:nth-child(2){animation-delay:.06s}
.section:nth-child(3){animation-delay:.1s}
.section:nth-child(4){animation-delay:.14s}
.section:nth-child(n+5){animation-delay:.18s}
@keyframes rpt-rise{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:none}}
.section-head{
  display:flex; align-items:baseline; gap:14px;
  padding-bottom:9px; margin-bottom:20px;
  border-bottom:2px solid var(--accent);
}
.section-index{
  font-family:var(--serif); font-weight:700; font-size:30px;
  color:var(--accent-line); line-height:1; min-width:1.4ch;
}
.section-title{
  font-family:var(--sans); font-weight:700; font-size:21px;
  letter-spacing:-.01em; flex:1;
}
.section-status{margin-left:auto; align-self:center}
.subsection{margin-top:26px}
.subsection-title{
  font-family:var(--mono); font-size:13px; font-weight:600;
  letter-spacing:.04em; color:var(--accent-strong);
  padding-bottom:6px; margin-bottom:13px;
  border-bottom:1px dashed var(--line);
}
.section>*+*,.subsection>*+*{margin-top:16px}
.text{font-size:15px; color:var(--ink); max-width:78ch}

/* ---- stat grid ---------------------------------------------------------- */
.stat-grid{
  display:grid; gap:0;
  grid-template-columns:repeat(auto-fit,minmax(150px,1fr));
  border-top:1px solid var(--line); border-left:1px solid var(--line);
}
.stat-card{
  position:relative; padding:18px 18px 16px;
  border-right:1px solid var(--line); border-bottom:1px solid var(--line);
  background:var(--paper);
}
.stat-card::before{
  content:""; position:absolute; top:0; left:0; width:26px; height:3px;
  background:var(--accent);
}
.stat-value{
  font-family:var(--mono); font-weight:600; font-size:30px;
  line-height:1; letter-spacing:-.02em; color:var(--ink);
}
.stat-label{
  margin-top:9px; font-family:var(--mono); font-size:10px;
  letter-spacing:.13em; text-transform:uppercase; color:var(--ink-soft);
}
.stat-card.is-green::before{background:var(--ok)}
.stat-card.is-green .stat-value{color:var(--ok)}
.stat-card.is-red::before{background:var(--bad)}
.stat-card.is-red .stat-value{color:var(--bad)}
.stat-card.is-yellow::before{background:var(--warn)}
.stat-card.is-yellow .stat-value{color:var(--warn)}
.stat-card.is-blue::before{background:var(--info)}
.stat-card.is-blue .stat-value{color:var(--info)}
.stat-card.is-purple::before{background:var(--gap)}
.stat-card.is-purple .stat-value{color:var(--gap)}
.stat-card.is-gray::before{background:var(--ink-soft)}

/* ---- tables ------------------------------------------------------------- */
.table-wrap{overflow-x:auto; border:1px solid var(--line)}
.rpt-table{
  width:100%; border-collapse:collapse; font-size:13.5px; background:var(--paper);
}
.rpt-table thead th{
  position:sticky; top:0; z-index:5;
  background:var(--accent-strong); color:#fff;
  font-family:var(--mono); font-weight:500; font-size:10.5px;
  letter-spacing:.08em; text-transform:uppercase;
  text-align:left; padding:9px 13px; white-space:nowrap;
}
.rpt-table tbody td{
  padding:8px 13px; border-bottom:1px solid var(--line-soft);
  border-right:1px solid var(--line-soft); vertical-align:top;
}
.rpt-table tbody tr:last-child td{border-bottom:0}
.rpt-table tbody tr:nth-child(even):not(.group){background:rgba(243,239,231,.5)}
.rpt-table tbody tr:hover:not(.group){background:var(--accent-soft)}
.rpt-table tr.group td.group-cell{
  background:var(--accent-soft);
  border-top:2px solid var(--accent); border-bottom:1px solid var(--accent-line);
  font-family:var(--mono); font-size:11.5px; font-weight:600;
  letter-spacing:.03em; color:var(--accent-strong);
  padding:7px 13px; text-transform:none;
}
.rpt-table td.cell--center{text-align:center}
.rpt-table td.cell--right{text-align:right; font-variant-numeric:tabular-nums}
.rpt-table td code{white-space:nowrap}

/* ---- progress ----------------------------------------------------------- */
.progress-list{
  display:flex; flex-direction:column; gap:11px;
  border:1px solid var(--line); padding:16px 18px; background:var(--paper-2);
}
.progress-item{display:grid; grid-template-columns:1fr; gap:5px}
.progress-label{
  display:flex; justify-content:space-between; align-items:baseline;
  font-size:13px;
}
.progress-label .progress-text{
  font-family:var(--mono); font-size:11.5px; color:var(--ink-soft);
}
.progress-track{
  height:9px; background:var(--paper); border:1px solid var(--line);
  overflow:hidden;
}
.progress-fill{
  height:100%; background:var(--accent);
  background-image:repeating-linear-gradient(135deg,
    rgba(255,255,255,.22) 0 5px,transparent 5px 10px);
}
.progress-fill.is-green{background-color:var(--ok)}
.progress-fill.is-red{background-color:var(--bad)}
.progress-fill.is-yellow{background-color:var(--warn)}
.progress-fill.is-blue{background-color:var(--info)}

/* ---- badges ------------------------------------------------------------- */
.badge{
  display:inline-block; font-family:var(--mono); font-size:10.5px;
  font-weight:600; letter-spacing:.05em; text-transform:uppercase;
  padding:2px 7px; border-radius:2px; border:1px solid;
  white-space:nowrap; line-height:1.5; vertical-align:baseline;
}
.badge.pass,.badge.success{color:var(--ok); background:var(--ok-soft); border-color:#bcdcc8}
.badge.fail,.badge.error{color:var(--bad); background:var(--bad-soft); border-color:#e7bdb8}
.badge.warn{color:var(--warn); background:var(--warn-soft); border-color:#e4cf9c}
.badge.info{color:var(--info); background:var(--info-soft); border-color:#bcd2ea}
.badge.skip{color:var(--ink-soft); background:var(--paper-2); border-color:var(--line)}
.badge.new{color:#fff; background:var(--accent); border-color:var(--accent)}
.badge.gap{color:var(--gap); background:var(--gap-soft); border-color:#d2c0e4}
.badge.resource{color:#1d5e8a; background:#e4f0f8; border-color:#bcd9eb}
.badge.catalog{color:#2c6e4a; background:#e4f1e9; border-color:#bcdcc8}
.badge.geo{color:#8a6d12; background:#f6efd6; border-color:#e1d29a}
.badge.ipam{color:#a23b32; background:#f7e6e4; border-color:#e7bdb8}
.badge.zone{color:#9a571c; background:#f6e9da; border-color:#e3c9a5}
.badge.party{color:#6b4ba0; background:#ece4f5; border-color:#cfbfe6}
.badge.logical{color:#4a4f59; background:#ebebed; border-color:#d3d4d8}

/* ---- standalone badge row ---------------------------------------------- */
.badge-row{display:flex; flex-wrap:wrap; gap:6px; align-items:center}

/* ---- inline color spans ([c:..]) --------------------------------------- */
.c-red{color:var(--bad); font-weight:600}
.c-green{color:var(--ok); font-weight:600}
.c-amber{color:var(--warn); font-weight:600}
.c-blue{color:var(--info); font-weight:600}
.c-gray{color:var(--ink-soft)}

/* ---- legend ------------------------------------------------------------- */
.legend{
  display:flex; flex-wrap:wrap; gap:7px 20px;
  padding:11px 16px; background:var(--paper-2); border:1px solid var(--line);
}
.legend-item{
  display:flex; align-items:center; gap:8px;
  font-family:var(--mono); font-size:12px; color:var(--ink);
}
.legend-dot{
  width:11px; height:11px; border:1px solid rgba(0,0,0,.2);
  flex:none; display:inline-block;
}

/* ---- status grid -------------------------------------------------------- */
.status-grid{
  display:grid; gap:10px;
  grid-template-columns:repeat(auto-fill,minmax(230px,1fr));
}
.status-item{
  display:flex; align-items:flex-start; gap:11px;
  padding:12px 14px; background:var(--paper); border:1px solid var(--line);
  border-left:3px solid var(--ink-soft);
}
.status-item.is-up{border-left-color:var(--ok)}
.status-item.is-down{border-left-color:var(--bad)}
.status-item.is-warn{border-left-color:var(--warn)}
.status-dot{
  width:9px; height:9px; border-radius:50%; margin-top:5px; flex:none;
  background:var(--ink-soft);
}
.status-item.is-up .status-dot{background:var(--ok); box-shadow:0 0 0 3px var(--ok-soft)}
.status-item.is-down .status-dot{background:var(--bad); box-shadow:0 0 0 3px var(--bad-soft)}
.status-item.is-warn .status-dot{background:var(--warn); box-shadow:0 0 0 3px var(--warn-soft)}
.status-name{font-weight:600; font-size:13.5px}
.status-meta{
  font-family:var(--mono); font-size:11px; color:var(--ink-soft); margin-top:2px;
}

/* ---- callouts ----------------------------------------------------------- */
.callout{
  border:1px solid var(--line); border-left:4px solid var(--ink-soft);
  background:var(--paper-2); padding:14px 18px;
}
.callout-label{
  font-family:var(--mono); font-size:9.5px; letter-spacing:.16em;
  text-transform:uppercase; font-weight:600; color:var(--ink-soft);
}
.callout-title{font-weight:700; font-size:14.5px; margin-top:3px}
.callout-body{margin-top:5px; font-size:14px; color:var(--ink)}
.callout-body code{background:rgba(255,255,255,.7)}
.callout--info{border-left-color:var(--info); background:var(--info-soft)}
.callout--info .callout-label{color:var(--info)}
.callout--warn{border-left-color:var(--warn); background:var(--warn-soft)}
.callout--warn .callout-label{color:var(--warn)}
.callout--error{border-left-color:var(--bad); background:var(--bad-soft)}
.callout--error .callout-label{color:var(--bad)}
.callout--success{border-left-color:var(--ok); background:var(--ok-soft)}
.callout--success .callout-label{color:var(--ok)}
.callout--gap{border-left-color:var(--gap); background:var(--gap-soft)}
.callout--gap .callout-label{color:var(--gap)}

/* ---- code block --------------------------------------------------------- */
.code-block{
  position:relative; background:#1c2530; border:1px solid #2c3947;
  overflow:hidden;
}
.code-lang{
  display:block; font-family:var(--mono); font-size:9.5px;
  letter-spacing:.16em; text-transform:uppercase; color:#8a97a6;
  background:#161d26; padding:5px 14px; border-bottom:1px solid #2c3947;
}
.code-block pre{
  font-family:var(--mono); font-size:12.5px; line-height:1.65;
  color:#dfe6ee; padding:14px 16px; overflow-x:auto; white-space:pre;
}

/* ---- mermaid ------------------------------------------------------------ */
.mermaid-wrap{
  position:relative;
  border:1px solid var(--line); background:var(--paper);
  padding:20px 24px; overflow-x:auto; overflow-y:visible;
}
.mermaid-wrap .mermaid{display:block}
/* max-width:none overrides Mermaid's inline style; JS also fixes width attr */
.mermaid-wrap svg{max-width:none!important;height:auto!important;display:block}
.mermaid-fallback{
  font-family:var(--mono); font-size:12px; color:var(--ink-soft);
  padding:8px;
}

/* ---- diagram expand button ---------------------------------------------- */
.dgm-expand{
  position:absolute; top:8px; right:8px; z-index:5;
  width:30px; height:30px; padding:0; border-radius:3px;
  border:1px solid rgba(188,210,228,.5);
  background:rgba(21,57,90,.75); color:#c8dae8;
  cursor:pointer; font-size:16px; line-height:30px; text-align:center;
  opacity:.7; transition:opacity .15s,background .15s;
}
.dgm-expand:hover{opacity:1; background:var(--accent-strong); color:#fff}

/* ---- diagram fullscreen modal (zoom + pan) ------------------------------ */
.dgm-modal{
  display:none; position:fixed; inset:0; z-index:9999;
  flex-direction:column;
}
.dgm-modal.open{display:flex}
.dgm-toolbar{
  flex:none; display:flex; align-items:center; gap:4px;
  padding:8px 12px; background:#111827;
  border-bottom:1px solid #1f2d3d;
}
.dgm-tb-btn{
  min-width:34px; height:34px; padding:0 8px; border-radius:4px;
  border:1px solid #253347; background:#1a2535; color:#8eaac8;
  cursor:pointer; font-size:18px; line-height:34px; text-align:center;
  transition:background .12s,color .12s;
}
.dgm-tb-btn:hover{background:#253347; color:#d0e4f5}
.dgm-tb-sep{width:1px; height:22px; background:#253347; margin:0 4px}
.dgm-tb-btn.dgm-close{margin-left:auto; color:#c87878}
.dgm-tb-btn.dgm-close:hover{background:#3a1a1a; color:#f08080; border-color:#5a2222}
.dgm-canvas{
  flex:1; position:relative; overflow:hidden;
  cursor:grab; user-select:none; -webkit-user-select:none;
  background:#0d1520;
  background-image:radial-gradient(circle,#1a2535 1px,transparent 1px);
  background-size:24px 24px;
}
.dgm-canvas:active{cursor:grabbing}
.dgm-canvas svg{
  position:absolute; top:0; left:0;
  max-width:none!important; display:block; transform-origin:0 0;
  background:var(--paper); border:1px solid var(--line);
  box-shadow:0 8px 40px rgba(0,0,0,.6); padding:20px;
}

/* ---- details ------------------------------------------------------------ */
.rpt-details{border:1px solid var(--line); background:var(--paper)}
.rpt-details>summary{
  cursor:pointer; padding:11px 16px; font-family:var(--mono);
  font-size:12.5px; font-weight:600; color:var(--accent-strong);
  background:var(--paper-2); list-style:none;
}
.rpt-details>summary::-webkit-details-marker{display:none}
.rpt-details>summary::before{
  content:"\25B8"; display:inline-block; margin-right:9px;
  color:var(--accent); transition:transform .15s ease;
}
.rpt-details[open]>summary::before{transform:rotate(90deg)}
.rpt-details[open]>summary{border-bottom:1px solid var(--line)}
.rpt-details-body{padding:16px}
.rpt-details-body>*+*{margin-top:14px}

/* ---- image grid --------------------------------------------------------- */
.image-grid{
  display:grid; gap:14px;
  grid-template-columns:repeat(auto-fill,minmax(260px,1fr));
}
.image-card{border:1px solid var(--line); background:var(--paper); padding:8px}
.image-card img{
  width:100%; height:auto; display:block; border:1px solid var(--line-soft);
}
.image-caption{
  font-family:var(--mono); font-size:11px; color:var(--ink-soft);
  margin-top:7px; padding:0 2px;
}

/* ---- footer ------------------------------------------------------------- */
.rpt-footer{
  padding:20px 44px; border-top:3px double var(--line);
  background:var(--paper-2);
  font-family:var(--mono); font-size:11px; letter-spacing:.04em;
  color:var(--ink-soft); display:flex; justify-content:space-between;
  flex-wrap:wrap; gap:8px;
}
.rpt-footer::before{content:"\25AA"; color:var(--accent); margin-right:6px}

/* ---- motion / responsive / print --------------------------------------- */
@media (prefers-reduced-motion:reduce){
  .section{animation:none}
}
@media (max-width:680px){
  body{padding:16px 8px 48px}
  .rpt-header,.section,.rpt-footer{padding-left:20px; padding-right:20px}
  .toc--horizontal{padding-left:20px; padding-right:20px}
  .toc--vertical{margin-left:20px; margin-right:20px}
  .toc--vertical ol{columns:1}
  .rpt-title{font-size:26px}
}
@media print{
  body{background:#fff; padding:0}
  body[style]{background:#fff}
  .rpt{border:0; box-shadow:none; max-width:none}
  .toc--horizontal{position:static; background:var(--accent-strong)}
  .section{animation:none; page-break-inside:auto}
  .section-head{page-break-after:avoid}
  .stat-card,.callout,.mermaid-wrap,.image-card,.rpt-details{
    page-break-inside:avoid;
  }
  .rpt-table thead th{position:static}
  *{-webkit-print-color-adjust:exact; print-color-adjust:exact}
}
"""
