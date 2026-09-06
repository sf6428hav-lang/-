// ===== State =====
var links = [];
var history = [];
var isGenerating = false;
var currentScriptId = null;

// ===== Init =====
document.addEventListener('DOMContentLoaded', function() {
  renderLinks();
  loadHistory();
  loadSettings();
});

// ===== Link Queue =====
function detectPlatform(url) {
  if (/douyin\.com|v\.douyin|tiktok\.com/i.test(url)) return 'douyin';
  if (/hongguo|novelquickapp|changdunovel/i.test(url)) return 'hongguo';
  return 'link';
}

function platformLabel(p) {
  return { douyin: '\u62b9\u97f3', hongguo: '\u7ea2\u679c', link: '\u94fe\u63a5' }[p] || '\u94fe\u63a5';
}

function renderLinks() {
  var list = document.getElementById('queueList');
  if (!list) return;

  if (links.length === 0) {
    list.innerHTML = '<div class="queue-empty"><i>\ud83d\udd17</i><p>\u6682\u65e0\u94fe\u63a5\uff0c\u5728\u4e0a\u65b9\u7c98\u8d34\u540e\u6dfb\u52a0</p></div>';
    document.getElementById('batchActions').style.display = 'none';
    document.getElementById('progressBar').style.display = 'none';
    document.getElementById('progressInfo').style.display = 'none';
    document.getElementById('linkCount').textContent = '0 \u4e2a';
    return;
  }

  document.getElementById('batchActions').style.display = 'flex';
  var html = '';
  for (var i = 0; i < links.length; i++) {
    var l = links[i];
    var dotClass = l.status || 'wait';
    var labelMap = { wait: '\u7b49\u5f85', done: '\u5df2\u5b8c\u6210', running: '\u751f\u6210\u4e2d', fail: '\u5931\u8d25',
                     parsing: '\u89e3\u6790\u4e2d', downloading: '\u4e0b\u8f7d\u4e2d', generating: '\u751f\u6210\u4e2d' };
    var label = labelMap[dotClass] || '\u7b49\u5f85';
    // map running/parsing/downloading/generating dot class to 'running' visual
    var dotVisual = (dotClass === 'running' || dotClass === 'parsing' || dotClass === 'downloading' || dotClass === 'generating') ? 'running' : dotClass;
    var urlDisplay = l.url.length > 40 ? l.url.slice(0, 40) + '\u2026' : l.url;
    var platform = detectPlatform(l.url);
    html += '<div class="queue-item">' +
      '<span class="dot ' + dotVisual + '"></span>' +
      '<span class="info"><small style="color:#8e8e93">[' + platformLabel(platform) + ']</small> ' + urlDisplay + '</span>' +
      '<span class="tag">' + label + '</span>' +
      '<button class="del" onclick="removeLink(' + i + ')" ' + (isGenerating ? 'disabled' : '') + '>\u2715</button>' +
      '</div>';
  }
  list.innerHTML = html;
  document.getElementById('linkCount').textContent = links.length + ' \u4e2a';

  var genBtn = document.getElementById('genBtn');
  if (!isGenerating) {
    genBtn.textContent = '\ud83c\udfac \u5f00\u59cb\u751f\u6210\uff08' + links.length + '\uff09';
  }
}

function addLink() {
  var input = document.getElementById('linkInput');
  var val = input.value.trim();
  if (!val) return;
  links.push({ url: val, status: 'wait' });
  input.value = '';
  input.focus();
  renderLinks();
}

function removeLink(idx) {
  if (isGenerating) return;
  links.splice(idx, 1);
  renderLinks();
}

function clearAll() {
  if (isGenerating) return;
  links = [];
  renderLinks();
}

// ===== Generation =====
function startGenerate() {
  if (isGenerating || links.length === 0) return;

  var pending = links.filter(function(l) { return l.status === 'wait' || l.status === 'fail'; });
  if (pending.length === 0) {
    toast('\u6ca1\u6709\u5f85\u751f\u6210\u7684\u94fe\u63a5');
    return;
  }

  // Reset failed items to wait
  links.forEach(function(l) {
    if (l.status === 'fail') l.status = 'wait';
  });

  isGenerating = true;
  var btn = document.getElementById('genBtn');
  btn.disabled = true;
  btn.textContent = '\u23f3 \u751f\u6210\u4e2d\u2026';

  document.getElementById('progressBar').style.display = 'block';
  document.getElementById('progressInfo').style.display = 'flex';
  document.getElementById('progressFill').style.width = '0%';

  var total = links.filter(function(l) { return l.status === 'wait'; }).length;
  document.getElementById('progressText').textContent = '0 / ' + total;
  document.getElementById('progressPct').textContent = '0%';

  // Collect links to send
  var urls = links.filter(function(l) { return l.status === 'wait'; }).map(function(l) { return l.url; });

  // Use SSE
  fetch('/api/generate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ links: urls })
  }).then(function(response) {
    var reader = response.body.getReader();
    var decoder = new TextDecoder();
    var buffer = '';
    var doneCount = 0;
    var failCount = 0;
    var waitLinks = links.filter(function(l) { return l.status === 'wait'; });

    function read() {
      reader.read().then(function(result) {
        if (result.done) {
          finishGeneration(doneCount, failCount);
          return;
        }

        buffer += decoder.decode(result.value, { stream: true });
        var lines = buffer.split('\n');
        buffer = lines.pop();

        for (var i = 0; i < lines.length; i++) {
          var line = lines[i].trim();
          if (!line.startsWith('data: ')) continue;

          try {
            var data = JSON.parse(line.slice(6));

            if (data.type === 'progress' && data.index !== undefined) {
              var linkIdx = links.indexOf(waitLinks[data.index]);
              if (linkIdx >= 0) {
                links[linkIdx].status = data.status;
                links[linkIdx].message = data.message;
                if (data.status === 'done') {
                  doneCount++;
                  links[linkIdx].recordId = data.recordId;
                } else if (data.status === 'failed') {
                  failCount++;
                  links[linkIdx].status = 'fail';
                }
              }
              renderLinks();

              var pct = Math.round(((doneCount + failCount) / total) * 100);
              document.getElementById('progressFill').style.width = pct + '%';
              document.getElementById('progressText').textContent = (doneCount + failCount) + ' / ' + total;
              document.getElementById('progressPct').textContent = pct + '%';

              document.getElementById('statusText').textContent = data.message || '';
            }

            if (data.type === 'complete') {
              finishGeneration(doneCount, failCount);
              // Auto-show first generated script
              if (data.records && data.records.length > 0) {
                var first = data.records.find(function(r) { return r.status === 'done'; });
                if (first) {
                  loadScript(first.id, first.title);
                }
              }
              return;
            }
          } catch (e) {
            // ignore parse errors
          }
        }

        read();
      });
    }

    read();
  }).catch(function(err) {
    toast('\u751f\u6210\u8bf7\u6c42\u5931\u8d25: ' + err.message);
    isGenerating = false;
    document.getElementById('genBtn').disabled = false;
    document.getElementById('genBtn').textContent = '\ud83c\udfac \u5f00\u59cb\u751f\u6210';
  });
}

function finishGeneration(doneCount, failCount) {
  isGenerating = false;
  var btn = document.getElementById('genBtn');
  btn.disabled = false;
  btn.textContent = '\ud83c\udfac \u5f00\u59cb\u751f\u6210';
  document.getElementById('progressFill').style.width = '100%';
  document.getElementById('statusText').textContent = '';

  if (doneCount > 0) {
    toast('\u2705 \u751f\u6210\u5b8c\u6210' + (failCount > 0 ? '\uff0c' + failCount + ' \u4e2a\u5931\u8d25' : ''));
  } else if (failCount > 0) {
    toast('\u274c \u751f\u6210\u5931\u8d25');
  }

  loadHistory();
  renderLinks();
}

// ===== History =====
function loadHistory() {
  fetch('/api/history?page=1&page_size=50')
    .then(function(r) { return r.json(); })
    .then(function(data) {
      history = data.items || [];
      renderHistory();
    })
    .catch(function() {
      history = [];
      renderHistory();
    });
}

function renderHistory() {
  var list = document.getElementById('historyList');
  if (!list) return;

  if (history.length === 0) {
    list.innerHTML = '<div class="queue-empty"><i>\ud83d\udccb</i><p>\u6682\u65e0\u5386\u53f2\u8bb0\u5f55</p></div>';
    document.getElementById('historyCount').textContent = '0';
    return;
  }

  var html = '';
  for (var i = 0; i < history.length; i++) {
    var item = history[i];
    var dateStr = '';
    try {
      var d = new Date(item.created_at);
      dateStr = d.toLocaleDateString('zh-CN', { month: 'numeric', day: 'numeric' }) + ' ' +
                d.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' });
    } catch (e) {
      dateStr = item.created_at;
    }

    var isActive = currentScriptId === item.id;
    html += '<div class="queue-item" style="cursor:pointer' + (isActive ? ';background:#f0f0ff' : '') + '" onclick="loadScript(\'' + item.id + '\',\'' + escapeHtml(item.title) + '\')">' +
      '<span class="dot ' + (item.status === 'done' ? 'done' : 'fail') + '"></span>' +
      '<span class="info">' + escapeHtml(item.title) + '</span>' +
      '<span class="tag">' + dateStr + '</span>' +
      '</div>';
  }
  list.innerHTML = html;
  document.getElementById('historyCount').textContent = history.length;
}

function escapeHtml(text) {
  var div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

// ===== Script Display =====
function loadScript(id, title) {
  currentScriptId = id;
  document.getElementById('resultTitle').innerHTML = '\ud83d\udcc4 ' + escapeHtml(title);
  document.getElementById('scriptArea').textContent = '\u52a0\u8f7d\u4e2d\u2026';

  fetch('/api/scripts/' + id)
    .then(function(r) {
      if (!r.ok) throw new Error('Not found');
      return r.json();
    })
    .then(function(data) {
      document.getElementById('scriptArea').textContent = data.output;
      document.getElementById('charCount').textContent = data.output.length;
      renderHistory();
    })
    .catch(function() {
      document.getElementById('scriptArea').textContent = '(\u6682\u65e0\u5185\u5bb9)';
      document.getElementById('charCount').textContent = '0';
    });
}

// ===== Download =====
function downloadDocx() {
  if (!currentScriptId) {
    toast('\u8bf7\u5148\u9009\u62e9\u4e00\u4e2a\u5267\u672c');
    return;
  }
  window.open('/api/scripts/' + currentScriptId + '/download?format=docx', '_blank');
}

function downloadTxt() {
  if (!currentScriptId) {
    toast('\u8bf7\u5148\u9009\u62e9\u4e00\u4e2a\u5267\u672c');
    return;
  }
  window.open('/api/scripts/' + currentScriptId + '/download?format=txt', '_blank');
}

// ===== Settings =====
function showSettings() {
  document.getElementById('settingsModal').classList.add('show');
}

function hideSettings() {
  document.getElementById('settingsModal').classList.remove('show');
}

function loadSettings() {
  fetch('/api/settings')
    .then(function(r) { return r.json(); })
    .then(function(data) {
      document.getElementById('apiUrl').value = data.api_base_url || '';
      document.getElementById('apiKey').value = '';
      document.getElementById('apiKey').placeholder = data.api_key || '\u8f93\u5165\u4f60\u7684 Gemini API Key';
    })
    .catch(function() {
      // ignore
    });
}

function saveSettings() {
  var url = document.getElementById('apiUrl').value.trim();
  var key = document.getElementById('apiKey').value.trim();

  if (!url) {
    toast('\u8bf7\u586b\u5199 API Base URL');
    return;
  }

  var model = document.getElementById('modelName').value.trim() || 'gemini-1.5-pro';
  var payload = { api_base_url: url, api_key: key || '****', model_name: model, prompt_template: 'default' };

  fetch('/api/settings', {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  })
    .then(function(r) { return r.json(); })
    .then(function() {
      hideSettings();
      toast('\u2705 \u8bbe\u7f6e\u5df2\u4fdd\u5b58');
      loadSettings();
    })
    .catch(function(err) {
      toast('\u4fdd\u5b58\u5931\u8d25: ' + err.message);
    });
}

// ===== Toast =====
function toast(msg) {
  var e = document.getElementById('toast');
  e.textContent = msg;
  e.classList.add('show');
  setTimeout(function() { e.classList.remove('show'); }, 2500);
}
