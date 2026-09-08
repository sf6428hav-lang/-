var links=[],history=[],isGenerating=false,currentScriptId=null,_pendingModelName='';

document.addEventListener('DOMContentLoaded',function(){renderLinks();loadHistory();loadSettings();});

function detectPlatform(u){if(/douyin\.com|v\.douyin|tiktok\.com/i.test(u))return'抖音';if(/hongguo|novelquickapp|changdunovel/i.test(u))return'红果';return'链接';}
function escapeHtml(t){var d=document.createElement('div');d.textContent=t;return d.innerHTML;}

function renderLinks(){
  var list=document.getElementById('queueList');if(!list)return;
  if(links.length===0){list.innerHTML='<div class="queue-empty"><i>🔗</i><p>暂无链接，在上方粘贴后添加</p></div>';document.getElementById('batchActions').style.display='none';document.getElementById('progressBar').style.display='none';document.getElementById('progressInfo').style.display='none';return;}
  document.getElementById('batchActions').style.display='flex';
  var html='';
  for(var i=0;i<links.length;i++){var l=links[i],dc=l.status||'wait',lm={wait:'等待',done:'已完成',running:'生成中',fail:'失败',parsing:'解析中',downloading:'下载中',generating:'生成中'},lb=lm[dc]||'等待',dv=(dc==='running'||dc==='parsing'||dc==='downloading'||dc==='generating')?'running':dc,ud=l.url.length>45?l.url.slice(0,45)+'…':l.url,p=detectPlatform(l.url);
    html+='<div class="queue-item"><span class="dot '+dv+'"></span><span class="info"><small style="color:#8e8e93">['+p+']</small> '+ud+'</span><span class="tag">'+lb+'</span><button class="del" onclick="removeLink('+i+')" '+(isGenerating?'disabled':'')+'>✕</button></div>';}
  list.innerHTML=html;document.getElementById('linkCount').textContent=links.length+' 个';
  if(!isGenerating)document.getElementById('genBtn').textContent='🎬 开始生成（'+links.length+'）';
}
function renderHistory(){
  var l=document.getElementById('historyList');if(!l)return;
  if(history.length===0){l.innerHTML='<div class="queue-empty"><i>📋</i><p>暂无历史记录</p></div>';document.getElementById('historyCount').textContent='0';return;}
  var html='';
  for(var i=0;i<history.length;i++){var item=history[i],ds='';try{var d=new Date(item.created_at);ds=d.toLocaleDateString('zh-CN',{month:'numeric',day:'numeric'})+' '+d.toLocaleTimeString('zh-CN',{hour:'2-digit',minute:'2-digit'});}catch(e){ds=item.created_at;}
    var isActive=currentScriptId===item.id;
    html+='<div class="queue-item" style="cursor:pointer'+(isActive?';background:#f0f0ff':'')+'" onclick="loadScript(\''+item.id+'\',\''+escapeHtml(item.title)+'\')"><span class="dot '+(item.status==='done'?'done':'fail')+'"></span><span class="info">'+escapeHtml(item.title)+'</span><span class="tag">'+ds+'</span></div>';}
  l.innerHTML=html;document.getElementById('historyCount').textContent=history.length;
}

function addLink(){var input=document.getElementById('linkInput'),val=input.value.trim();if(!val)return;links.push({url:val,status:'wait'});input.value='';input.focus();renderLinks();}
function removeLink(i){if(isGenerating)return;links.splice(i,1);renderLinks();}
function clearAll(){if(isGenerating)return;links=[];renderLinks();}

function startGenerate(){
  if(isGenerating||links.length===0)return;
  var pending=links.filter(function(l){return l.status==='wait'||l.status==='fail';});
  if(pending.length===0){toast('没有待生成的链接');return;}
  links.forEach(function(l){if(l.status==='fail')l.status='wait';});
  isGenerating=true;var btn=document.getElementById('genBtn');btn.disabled=true;btn.textContent='⏳ 生成中 …';
  document.getElementById('progressBar').style.display='block';document.getElementById('progressInfo').style.display='flex';document.getElementById('progressFill').style.width='0%';
  var total=links.filter(function(l){return l.status==='wait';}).length;
  document.getElementById('progressText').textContent='0 / '+total;document.getElementById('progressPct').textContent='0%';
  var urls=links.filter(function(l){return l.status==='wait';}).map(function(l){return l.url;});

  fetch('/api/generate',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({links:urls})})
  .then(function(response){
    var reader=response.body.getReader(),decoder=new TextDecoder(),buffer='',doneCount=0,failCount=0,waitLinks=links.filter(function(l){return l.status==='wait';});
    function read(){reader.read().then(function(result){
      if(result.done){finishGen(doneCount,failCount);return;}
      buffer+=decoder.decode(result.value,{stream:true});var lines=buffer.split('\n');buffer=lines.pop();
      for(var i=0;i<lines.length;i++){var line=lines[i].trim();if(!line.startsWith('data: '))continue;
        try{var data=JSON.parse(line.slice(6));
          if(data.type==='progress'&&data.index!==undefined){var linkIdx=links.indexOf(waitLinks[data.index]);if(linkIdx>=0){links[linkIdx].status=data.status;if(data.status==='done')doneCount++;else if(data.status==='failed'){failCount++;links[linkIdx].status='fail';}}renderLinks();var pct=Math.round(((doneCount+failCount)/total)*100);document.getElementById('progressFill').style.width=pct+'%';document.getElementById('progressText').textContent=(doneCount+failCount)+' / '+total;document.getElementById('progressPct').textContent=pct+'%';}
          if(data.type==='complete'){finishGen(doneCount,failCount);if(data.records&&data.records.length>0){var first=data.records.find(function(r){return r.status==='done';});if(first){if(first.output){currentScriptId=first.id;document.getElementById('resultTitle').innerHTML='📄 '+escapeHtml(first.title);document.getElementById('scriptArea').textContent=first.output;document.getElementById('charCount').textContent=first.output.length;}else{loadScript(first.id,first.title);}}}return;}
        }catch(e){}}
      read();});}
    read();
  }).catch(function(err){toast('生成请求失败: '+err.message);isGenerating=false;btn.disabled=false;btn.textContent='🎬 开始生成';});
}
function finishGen(doneCount,failCount){isGenerating=false;var btn=document.getElementById('genBtn');btn.disabled=false;btn.textContent='🎬 开始生成';document.getElementById('progressFill').style.width='100%';if(doneCount>0)toast('✅ 生成完成'+(failCount>0?'，'+failCount+' 个失败':''));else if(failCount>0)toast('❌ 生成失败');loadHistory();renderLinks();}
function loadHistory(){fetch('/api/history?page=1&page_size=50').then(function(r){return r.json();}).then(function(data){history=data.items||[];renderHistory();}).catch(function(){history=[];renderHistory();});}
function loadScript(id,title){currentScriptId=id;document.getElementById('resultTitle').innerHTML='📄 '+escapeHtml(title);document.getElementById('scriptArea').textContent='加载中…';fetch('/api/scripts/'+id).then(function(r){if(!r.ok)throw new Error('Not found');return r.json();}).then(function(data){document.getElementById('scriptArea').textContent=data.output;document.getElementById('charCount').textContent=data.output.length;renderHistory();}).catch(function(){document.getElementById('scriptArea').textContent='(暂无内容)';document.getElementById('charCount').textContent='0';});}

function reformatScript(){
  if(!currentScriptId){toast('请先选择一个剧本');return;}
  var area = document.getElementById('scriptArea');
  var text = area.textContent || '';
  if(!text || text === '加载中…'){toast('暂无可排版内容');return;}
  var formatted = formatScriptText(text);
  area.textContent = formatted;
  document.getElementById('charCount').textContent = formatted.length;
  toast('✅ 排版完成');
}

function formatScriptText(text){
  var lines = text.split('
');
  var out = [];
  var prevBlank = false;
  for(var i=0;i<lines.length;i++){
    var line = lines[i].trim();
    if(!line){
      if(!prevBlank && out.length > 0 && out[out.length-1] !== ''){ out.push(''); }
      prevBlank = true;
      continue;
    }
    prevBlank = false;
    out.push(line);
  }
  // 去除首尾多余空行
  while(out.length && out[0] === '') out.shift();
  while(out.length && out[out.length-1] === '') out.pop();
  return out.join('
');
}

function downloadDocx(){if(!currentScriptId){toast('请先选择一个剧本');return;}window.open('/api/scripts/'+currentScriptId+'/download?format=docx','_blank');}
function downloadTxt(){if(!currentScriptId){toast('请先选择一个剧本');return;}window.open('/api/scripts/'+currentScriptId+'/download?format=txt','_blank');}

// ===== Settings with localStorage =====
function showSettings(){document.getElementById('settingsModal').classList.add('show');}
function hideSettings(){document.getElementById('settingsModal').classList.remove('show');}

function loadSettings(){
  var s=localStorage.getItem("scriptGenSettings");
  if(s){try{var d=JSON.parse(s);document.getElementById("apiUrl").value=d.url||"";document.getElementById("apiKey").value=d.key||"";if(d.model)_pendingModelName=d.model;if(d.url&&d.key)setTimeout(fetchModels,500);}catch(e){}return;}
  fetch("/api/settings").then(function(r){return r.json();}).then(function(d){
    document.getElementById("apiUrl").value=d.api_base_url||"";
    if(d.model_name)_pendingModelName=d.model_name;
  }).catch(function(){});
}

function saveSettings(){
  var url=document.getElementById('apiUrl').value.trim(),key=document.getElementById('apiKey').value.trim();
  if(!url){toast('请填写 API 地址');return;}
  var model=document.getElementById('modelName').value||'gemini-1.5-pro';
  localStorage.setItem('scriptGenSettings',JSON.stringify({url:url,key:key,model:model}));
  var payload={api_base_url:url,api_key:key||'****',model_name:model,prompt_template:'default'};
  fetch('/api/settings',{method:'PUT',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)}).then(function(r){return r.json();}).then(function(){hideSettings();toast('✅ 设置已保存');}).catch(function(err){toast('保存失败: '+err.message);});
}

function fetchModels(){
  var baseUrl=document.getElementById('apiUrl').value.trim(),key=document.getElementById('apiKey').value.trim();
  if(!baseUrl&&!key){toast('请先填写 API 地址和 Key');return;}
  var params='';if(baseUrl)params+='api_base_url='+encodeURIComponent(baseUrl);if(key)params+=(params?'&':'')+'api_key='+encodeURIComponent(key);
  var select=document.getElementById('modelName');select.innerHTML='<option value="">加载中...</option>';
  fetch('/api/models?'+params).then(function(r){return r.json();}).then(function(data){
    if(data.error){toast('获取失败: '+data.error);select.innerHTML='<option value="">获取失败</option>';return;}
    if(!data.models||data.models.length===0){select.innerHTML='<option value="">未找到模型</option>';return;}
    var html='',target=_pendingModelName||'';for(var i=0;i<data.models.length;i++){var m=data.models[i],sel=(m===target)?' selected':'';html+='<option value="'+m+'"'+sel+'>'+m+'</option>';}
    select.innerHTML=html;_pendingModelName='';toast('已获取 '+data.models.length+' 个模型');
  }).catch(function(err){toast('获取失败: '+err.message);select.innerHTML='<option value="">获取失败</option>';});
}

function toast(msg){var e=document.getElementById('toast');e.textContent=msg;e.classList.add('show');setTimeout(function(){e.classList.remove('show');},2500);}

renderLinks();renderHistory();loadSettings();





