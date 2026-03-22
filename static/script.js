let nextPostSeconds = 0;
let timerInterval = null;

function startTimer(hms) {
    const clockEl = document.getElementById('timer-clock');
    const timerLabel = document.querySelector('.timer-label');

    if (!hms || hms === "LIMIT") {
        if (hms === "LIMIT") {
            if (clockEl) {
                clockEl.textContent = "WAIT";
                clockEl.style.color = "#f87171";
            }
            if (timerLabel) timerLabel.textContent = "Daily Limit Reached";
        }
        return;
    }

    if (timerLabel) timerLabel.textContent = "Next Auto-Post In:";

    if (hms.includes(':')) {
        const parts = hms.split(':').map(Number);
        const newSeconds = (parts[0] * 3600) + (parts[1] * 60) + parts[2];
        if (Math.abs(newSeconds - nextPostSeconds) > 10 || nextPostSeconds === 0) {
            nextPostSeconds = newSeconds;
        }
    }

    if (timerInterval) clearInterval(timerInterval);
    updateTimerDisplay();

    timerInterval = setInterval(() => {
        if (nextPostSeconds > 0) {
            nextPostSeconds--;
            updateTimerDisplay();
        } else {
            clearInterval(timerInterval);
            fetchStats();
        }
    }, 1000);
}

function updateTimerDisplay() {
    const clockEl = document.getElementById('timer-clock');
    if (!clockEl) return;
    if (nextPostSeconds <= 0) {
        if (clockEl.textContent !== "WAIT") {
            clockEl.textContent = "READY";
            clockEl.style.color = "#4ade80";
        }
        return;
    }
    const h = Math.floor(nextPostSeconds / 3600);
    const m = Math.floor((nextPostSeconds % 3600) / 60);
    const s = nextPostSeconds % 60;
    clockEl.textContent = `${h.toString().padStart(2, '0')}:${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
    clockEl.style.color = "#f59e0b";
}

function formatCompact(num) {
    if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
    if (num >= 1000) return (num / 1000).toFixed(1) + 'K';
    return num;
}

async function fetchStats() {
    try {
        const response = await fetch('/api/stats');
        const data = await response.json();

        // Update basic cards
        document.getElementById('videos-queued').textContent = data.videos_queued || 0;
        document.getElementById('total-posted').textContent = data.total_posted || 0;
        document.getElementById('days-remaining').textContent = Math.max(0, Math.round((data.videos_queued || 0) / (data.config.max_daily || 3)));

        // Update engagement metrics
        if (data.metrics) {
            document.getElementById('total-views').textContent = formatCompact(data.metrics.total_views);
            document.getElementById('total-likes').textContent = formatCompact(data.metrics.total_likes);

            // Monetization Progress
            const subs = data.metrics.subscribers || 0;
            const subPercent = Math.min(100, (subs / 1000) * 100);
            document.getElementById('sub-progress-text').textContent = `${subs.toLocaleString()} / 1,000`;
            document.getElementById('sub-progress-fill').style.width = `${subPercent}%`;

            const totalViews = data.metrics.total_views || 0;
            const viewsPercent = Math.min(100, (totalViews / 10000000) * 100);
            document.getElementById('views-progress-text').textContent = `${formatCompact(totalViews)} / 10M`;
            document.getElementById('views-progress-fill').style.width = `${viewsPercent}%`;
        }

        // Update channel profile
        if (data.channel) {
            document.getElementById('channel-info').innerHTML = `
                <img src="${data.channel.thumbnail}" class="channel-avatar">
                <span>${data.channel.title}</span>
            `;
        }

        const statusDot = document.getElementById('status-dot');
        const statusText = document.getElementById('status-text');
        if (!data.can_post_now) {
            startTimer(data.next_post_timer);
            statusDot.style.background = "#f59e0b";
            statusText.textContent = data.next_post_timer === "LIMIT" ? "Locked" : "Pacing";
        } else {
            if (timerInterval) clearInterval(timerInterval);
            nextPostSeconds = 0;
            updateTimerDisplay();
            statusDot.style.background = "#4ade80";
            statusText.textContent = "Live";
        }
    } catch (err) {
        console.error('Error fetching stats:', err);
    }
}

async function fetchLogs() {
    try {
        const response = await fetch('/api/logs');
        const logs = await response.json();
        const container = document.getElementById('logs-container');
        container.innerHTML = '';
        logs.forEach(log => {
            const date = new Date(log.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
            const item = document.createElement('div');
            item.className = 'log-item';
            const isSuccess = log.status === 'success';
            const color = isSuccess ? '#4ade80' : '#f87171';
            const thumbUrl = log.video_id ? `https://img.youtube.com/vi/${log.video_id}/0.jpg` : 'https://via.placeholder.com/120x68/1e293b/94a3b8?text=Shorts';
            const shortsUrl = log.video_id ? `https://www.youtube.com/shorts/${log.video_id}` : '#';
            item.innerHTML = `
                <img src="${thumbUrl}" class="log-thumb" onerror="this.src='https://via.placeholder.com/120x68/1e293b/94a3b8?text=YouTube'">
                <div class="log-main">
                    <h4>${log.title || log.filename}</h4>
                    <p style="font-size: 0.75rem; color: #94a3b8">${date} • <span style="color:${color}">${(log.status || 'unknown').toUpperCase()}</span></p>
                </div>
                ${isSuccess ? `<a href="${shortsUrl}" target="_blank" class="log-link"><i data-lucide="external-link" style="width:14px"></i> Link</a>` : ''}
            `;
            container.appendChild(item);
        });
        if (typeof lucide !== 'undefined') lucide.createIcons();
    } catch (err) {
        console.error('Error fetching logs:', err);
    }
}

document.getElementById('trigger-btn').addEventListener('click', async () => {
    const btn = document.getElementById('trigger-btn');
    const originalContent = btn.innerHTML;
    try {
        btn.innerHTML = '<span>🚀 Processing...</span>';
        btn.disabled = true;
        await fetch('/api/trigger', { method: 'POST' });
        alert("🚀 Manual Override Active! Posting the next Reel regardless of limits.");
        setTimeout(() => {
            btn.innerHTML = originalContent;
            btn.disabled = false;
            fetchStats();
            fetchLogs();
        }, 12000);
    } catch (err) {
        alert("Error during manual override.");
        btn.innerHTML = originalContent;
        btn.disabled = false;
    }
});

fetchStats();
fetchLogs();
setInterval(() => {
    fetchStats();
    fetchLogs();
}, 20000);
