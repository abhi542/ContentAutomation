let nextPostSeconds = 0;
let timerInterval = null;

function startTimer(seconds) {
    if (timerInterval) clearInterval(timerInterval);

    if (seconds === -1) {
        setTimerUI("WAIT", "#f87171", "Daily Limit Reached");
        return;
    }

    if (seconds <= 0) {
        setTimerUI("READY", "#4ade80", "System Available");
        return;
    }

    nextPostSeconds = seconds;
    setTimerUI(formatSeconds(nextPostSeconds), "#3b82f6", "Next Auto-Post In");

    timerInterval = setInterval(() => {
        if (nextPostSeconds > 0) {
            nextPostSeconds--;
            setTimerUI(formatSeconds(nextPostSeconds), "#3b82f6", "Next Auto-Post In");
        } else {
            clearInterval(timerInterval);
            fetchStats();
        }
    }, 1000);
}

function setTimerUI(clock, color, label) {
    const clockEl = document.getElementById('timer-clock');
    const labelEl = document.getElementById('timer-label');
    if (clockEl) {
        clockEl.textContent = clock;
        clockEl.style.color = color;
    }
    if (labelEl) labelEl.textContent = label;
}

function formatSeconds(totalSec) {
    const h = Math.floor(totalSec / 3600);
    const m = Math.floor((totalSec % 3600) / 60);
    const s = totalSec % 60;
    return `${h.toString().padStart(2, '0')}:${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
}

function formatCompact(num) {
    if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
    if (num >= 1000) return (num / 1000).toFixed(1) + 'K';
    return num;
}

async function fetchStats() {
    try {
        const response = await fetch('/api/stats?t=' + Date.now());
        const data = await response.json();

        // Safety wrapper to prevent script crashes
        const setSafe = (id, val) => {
            const el = document.getElementById(id);
            if (el) el.textContent = val;
        };

        // Update basic info
        setSafe('videos-queued', data.videos_queued || 0);

        // Monetization & Metrics
        if (data.metrics) {
            setSafe('total-views', formatCompact(data.metrics.total_views));
            setSafe('latest-views', formatCompact(data.live_stats ? data.live_stats.viewCount : 0));
            setSafe('latest-likes', formatCompact(data.metrics.total_likes));
            setSafe('latest-comments', formatCompact(data.metrics.total_comments || 0));

            const maxDaily = (data.config && data.config.max_daily) || 3;
            const coverage = Math.max(0, Math.round((data.videos_queued || 0) / maxDaily));
            setSafe('days-remaining', coverage + 'd');

            // Progress bars
            updateProgress('sub', data.metrics.subscribers, 1000);
            updateProgress('views', data.metrics.shorts_views_90d || 0, 10000000, "10M");
            updateProgress('hours', 8.5, 4000, "4K"); // Placeholder
        }

        if (data.config) {
            setSafe('setting-limit', `${data.config.max_daily} Posts`);
            setSafe('setting-gap', `${data.config.gap_hours} Hours`);
        }

        // Channel
        if (data.channel) {
            const chEl = document.getElementById('channel-info');
            if (chEl) {
                chEl.innerHTML = `
                    <img src="${data.channel.thumbnail}" class="channel-avatar">
                    <span class="channel-name">${data.channel.title}</span>
                `;
            }
        }

        // Status & Timer
        const dot = document.getElementById('status-dot');
        const text = document.getElementById('status-text');

        if (data.can_post_now) {
            if (dot) dot.style.background = "#10b981";
            if (text) text.textContent = "Live";
            startTimer(0);
        } else {
            if (dot) dot.style.background = data.wait_seconds === -1 ? "#f87171" : "#f59e0b";
            if (text) text.textContent = data.wait_seconds === -1 ? "Locked" : "Pacing";
            startTimer(data.wait_seconds);
        }
    } catch (err) {
        console.error('Error in fetchStats:', err);
    }
}

function updateProgress(id, val, target, targetLabel) {
    const text = document.getElementById(`${id}-count`);
    const fill = document.getElementById(`${id}-fill`);
    if (text) {
        text.textContent = `${val.toLocaleString()} / ${targetLabel || formatCompact(target)}`;
    }
    if (fill) {
        fill.style.width = Math.min(100, (val / target) * 100) + '%';
    }
}

async function fetchLogs() {
    try {
        const response = await fetch('/api/logs?t=' + Date.now());
        const logs = await response.json();
        const container = document.getElementById('logs-container');
        if (!container) return;

        container.innerHTML = '';
        logs.forEach(log => {
            const date = new Date(log.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
            const item = document.createElement('div');
            item.className = 'log-item';

            const isSuccess = log.status === 'success';
            const statusColor = isSuccess ? '#10b981' : '#f87171';
            const thumbUrl = log.video_id ? `https://img.youtube.com/vi/${log.video_id}/mqdefault.jpg` : 'https://via.placeholder.com/44';

            item.innerHTML = `
                <img src="${thumbUrl}" class="log-thumb">
                <div class="log-main">
                    <h4>${log.title || log.filename}</h4>
                    <p>${date} • <span style="color:${statusColor}">${(log.status || 'unknown').toUpperCase()}</span></p>
                </div>
                ${isSuccess ? `<a href="${log.youtube_url || '#'}" target="_blank" class="log-link">Video</a>` : ''}
            `;
            container.appendChild(item);
        });

        if (typeof lucide !== 'undefined') lucide.createIcons();
    } catch (err) {
        console.error('Error in fetchLogs:', err);
    }
}

document.getElementById('trigger-btn').addEventListener('click', async () => {
    const btn = document.getElementById('trigger-btn');
    const original = btn.innerHTML;
    try {
        btn.innerHTML = '<span>🚀 Initializing...</span>';
        btn.disabled = true;
        await fetch('/api/trigger', { method: 'POST' });
        alert("🚀 Manual Override Engaged. Processing next reel...");
        setTimeout(() => {
            btn.innerHTML = original;
            btn.disabled = false;
            fetchStats();
            fetchLogs();
        }, 12000);
    } catch (err) {
        alert("Error triggering automation.");
        btn.innerHTML = original;
        btn.disabled = false;
    }
});

fetchStats();
fetchLogs();
setInterval(() => {
    fetchStats();
    fetchLogs();
}, 20000);
