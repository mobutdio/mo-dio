// API URL
const API_URL = '/api';

// Data
let playlists = [];
let currentPlaylistId = null;
let currentIndex = 0;
let isPlaying = false;
let currentVideoId = null;
let currentPlayingPlaylistId = null;

// Player modes
let shuffleMode = false;
let repeatMode = 'none';

let pendingSong = null;
let player = null;
let playerReady = false;

// DOM Elements
const searchInput = document.getElementById('searchInput');
const searchBtn = document.getElementById('searchBtn');
const playlistList = document.getElementById('playlistList');
const createPlaylistBtn = document.getElementById('createPlaylistBtn');
const deletePlaylistBtn = document.getElementById('deletePlaylistBtn');
const playlistContainer = document.getElementById('playlistContainer');
const currentPlaylistName = document.getElementById('currentPlaylistName');
const searchResults = document.getElementById('searchResults');
const recResults = document.getElementById('recResults');
const currentTitle = document.getElementById('currentTitle');
const currentArtist = document.getElementById('currentArtist');
const playPauseBtn = document.getElementById('playPauseBtn');
const prevBtn = document.getElementById('prevBtn');
const nextBtn = document.getElementById('nextBtn');
const shuffleBtn = document.getElementById('shuffleBtn');
const repeatBtn = document.getElementById('repeatBtn');
const volumeSlider = document.getElementById('volumeSlider');
const progressBar = document.getElementById('progressBar');
const progressFill = document.getElementById('progressFill');
const currentTimeSpan = document.getElementById('currentTime');
const durationSpan = document.getElementById('duration');
const playerWrapper = document.getElementById('playerWrapper');

// Modal
const playlistModal = document.getElementById('playlistModal');
const modalPlaylistList = document.getElementById('modalPlaylistList');
const closeModalBtn = document.getElementById('closeModalBtn');

// Loading elements
const loadingOverlay = document.getElementById('loadingOverlay');
const loadingBar = document.getElementById('loadingBar');
const loadingText = document.getElementById('loadingText');
const loadingMessage = document.getElementById('loadingMessage');

let loadingInterval = null;

function showLoading(message = '🔍 جاري البحث...') {
    loadingMessage.textContent = message;
    loadingOverlay.classList.remove('hidden');
    loadingBar.style.width = '0%';
    loadingText.textContent = '0%';
    
    let percent = 0;
    if (loadingInterval) clearInterval(loadingInterval);
    
    loadingInterval = setInterval(() => {
        percent += Math.random() * 15;
        if (percent >= 95) {
            percent = 95;
            clearInterval(loadingInterval);
        }
        loadingBar.style.width = percent + '%';
        loadingText.textContent = Math.floor(percent) + '%';
    }, 150);
}

function hideLoading() {
    if (loadingInterval) clearInterval(loadingInterval);
    loadingBar.style.width = '100%';
    loadingText.textContent = '100%';
    setTimeout(() => {
        loadingOverlay.classList.add('hidden');
        loadingBar.style.width = '0%';
    }, 300);
}

// YouTube Player API
function onYouTubeIframeAPIReady() {
    console.log('YouTube API ready');
}

function createPlayer(videoId) {
    if (!videoId) {
        showToast('❌ لا يوجد معرف للأغنية');
        return false;
    }
    
    console.log('Creating player with videoId:', videoId);
    
    if (player) {
        player.destroy();
    }
    
    try {
        player = new YT.Player('youtubePlayer', {
            height: '280',
            width: '100%',
            videoId: videoId,
            playerVars: {
                'autoplay': 1,
                'controls': 0,
                'rel': 0,
                'modestbranding': 1,
                'enablejsapi': 1
            },
            events: {
                'onReady': onPlayerReady,
                'onStateChange': onPlayerStateChange,
                'onError': onPlayerError
            }
        });
        return true;
    } catch(e) {
        console.error('Error creating player:', e);
        showToast('❌ خطأ في تشغيل الأغنية');
        return false;
    }
}

function onPlayerReady(event) {
    playerReady = true;
    const duration = player.getDuration();
    if (duration && duration > 0) {
        durationSpan.innerText = formatTime(duration);
    }
    player.setVolume(volumeSlider.value);
    startProgressUpdate();
    showToast('🎵 جاري التشغيل...');
}

function onPlayerStateChange(event) {
    console.log('Player state changed:', event.data);
    
    if (event.data === YT.PlayerState.ENDED) {
        if (repeatMode === 'one') {
            player.seekTo(0);
            player.playVideo();
        } else {
            nextSong();
        }
    } else if (event.data === YT.PlayerState.PLAYING) {
        isPlaying = true;
        playPauseBtn.innerHTML = '<i class="fas fa-pause"></i>';
        const duration = player.getDuration();
        if (duration && duration > 0 && durationSpan.innerText === '0:00') {
            durationSpan.innerText = formatTime(duration);
        }
    } else if (event.data === YT.PlayerState.PAUSED) {
        isPlaying = false;
        playPauseBtn.innerHTML = '<i class="fas fa-play"></i>';
    } else if (event.data === YT.PlayerState.BUFFERING) {
        console.log('Buffering...');
    } else if (event.data === YT.PlayerState.UNSTARTED) {
        console.log('Unstarted');
    }
}

function onPlayerError(event) {
    console.error('YouTube error:', event);
    let errorMsg = '⚠️ خطأ في التشغيل';
    if (event.data === 2) errorMsg = '❌ فيديو غير صالح';
    else if (event.data === 5) errorMsg = '❌ خطأ في HTML5 player';
    else if (event.data === 100) errorMsg = '❌ الفيديو غير متاح';
    else if (event.data === 101) errorMsg = '❌ الفيديو محظور';
    showToast(errorMsg);
    playerReady = false;
}

function startProgressUpdate() {
    function updateProgress() {
        if (player && player.getCurrentTime) {
            try {
                const current = player.getCurrentTime();
                const duration = player.getDuration();
                if (duration && duration > 0) {
                    const percent = (current / duration) * 100;
                    progressFill.style.width = percent + '%';
                    currentTimeSpan.innerText = formatTime(current);
                    if (durationSpan.innerText === '0:00') {
                        durationSpan.innerText = formatTime(duration);
                    }
                }
            } catch(e) {}
            requestAnimationFrame(updateProgress);
        } else {
            requestAnimationFrame(updateProgress);
        }
    }
    requestAnimationFrame(updateProgress);
}

function seekToTime(percent) {
    if (player && playerReady) {
        try {
            const duration = player.getDuration();
            if (duration && duration > 0) {
                const seekTime = percent * duration;
                player.seekTo(seekTime, true);
            }
        } catch(e) {}
    }
}

// Initialize
function init() {
    loadData();
    if (playlists.length === 0) {
        playlists.push({
            id: Date.now(),
            name: 'المفضلة',
            songs: []
        });
        saveData();
    }
    currentPlaylistId = playlists[0].id;
    renderPlaylistsList();
    renderCurrentPlaylist();
    loadRecommendations();

    searchBtn.addEventListener('click', searchSongs);
    searchInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') searchSongs();
    });
    createPlaylistBtn.addEventListener('click', createNewPlaylist);
    deletePlaylistBtn.addEventListener('click', deleteCurrentPlaylist);
    playPauseBtn.addEventListener('click', playPause);
    prevBtn.addEventListener('click', prevSong);
    nextBtn.addEventListener('click', nextSong);
    shuffleBtn.addEventListener('click', toggleShuffle);
    repeatBtn.addEventListener('click', toggleRepeat);
    volumeSlider.addEventListener('input', (e) => {
        if (player && playerReady) player.setVolume(e.target.value);
    });
    progressBar.addEventListener('click', (e) => {
        if (!player || !playerReady) {
            showToast('🎵 شغل أغنية أولاً');
            return;
        }
        const rect = progressBar.getBoundingClientRect();
        const x = e.clientX - rect.left;
        let percent = x / rect.width;
        if (percent > 1) percent = 1;
        if (percent < 0) percent = 0;
        seekToTime(percent);
    });
    closeModalBtn.addEventListener('click', closeModal);
    playlistModal.addEventListener('click', (e) => {
        if (e.target === playlistModal) closeModal();
    });

    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
            document.getElementById(btn.dataset.tab + 'Panel').classList.add('active');
            if (btn.dataset.tab === 'recommendations') loadRecommendations();
        });
    });
}

function loadData() {
    const saved = localStorage.getItem('dio_multi_playlists');
    if (saved) playlists = JSON.parse(saved);
}

function saveData() {
    localStorage.setItem('dio_multi_playlists', JSON.stringify(playlists));
    renderPlaylistsList();
    renderCurrentPlaylist();
}

function renderPlaylistsList() {
    if (playlists.length === 0) {
        playlistList.innerHTML = '<li style="color:#888;">لا توجد بلاي ليست</li>';
        return;
    }
    playlistList.innerHTML = playlists.map(p => `
        <li onclick="switchPlaylist(${p.id})" class="${currentPlaylistId === p.id ? 'active' : ''}">
            <i class="fas ${currentPlaylistId === p.id ? 'fa-check-circle' : 'fa-circle'}"></i>
            <span>${escapeHtml(p.name)}</span>
            <span style="margin-right: auto; font-size: 11px;">${p.songs.length}</span>
        </li>
    `).join('');
}

function renderCurrentPlaylist() {
    const playlist = getCurrentPlaylist();
    if (!playlist) return;
    currentPlaylistName.innerHTML = `<i class="fas fa-headphones"></i> ${escapeHtml(playlist.name)} (${playlist.songs.length} أغنية)`;
    if (playlist.songs.length === 0) {
        playlistContainer.innerHTML = '<div class="empty-playlist">📭 البلاي ليست فارغة<br>➕ أضف أغاني من البحث</div>';
        return;
    }
    playlistContainer.innerHTML = playlist.songs.map((song, idx) => `
        <div class="playlist-item ${idx === currentIndex && currentPlayingPlaylistId === currentPlaylistId ? 'active' : ''}">
            <img src="${song.thumbnail}" onclick="playSongById('${song.videoId}','${escapeHtml(song.title)}','${currentPlaylistId}',${idx})">
            <div class="playlist-info" onclick="playSongById('${song.videoId}','${escapeHtml(song.title)}','${currentPlaylistId}',${idx})">
                <h4>${escapeHtml(song.title.substring(0, 45))}</h4>
                <p>Dio Music • ${formatTime(song.duration)}</p>
            </div>
            <div class="playlist-actions">
                <button onclick="event.stopPropagation();playSongById('${song.videoId}','${escapeHtml(song.title)}','${currentPlaylistId}',${idx})"><i class="fas fa-play"></i></button>
                <button onclick="event.stopPropagation();removeFromPlaylist(${idx})"><i class="fas fa-trash"></i></button>
            </div>
        </div>
    `).join('');
}

function switchPlaylist(id) {
    currentPlaylistId = id;
    renderPlaylistsList();
    renderCurrentPlaylist();
    document.querySelector('.tab-btn[data-tab="playlist"]').click();
}

function getCurrentPlaylist() {
    return playlists.find(p => p.id === currentPlaylistId);
}

function createNewPlaylist() {
    let name = prompt('اسم البلاي ليست الجديدة:', 'بلاي ليست جديدة');
    if (name && name.trim()) {
        playlists.push({ id: Date.now(), name: name.trim(), songs: [] });
        saveData();
        currentPlaylistId = playlists[playlists.length - 1].id;
        renderPlaylistsList();
        renderCurrentPlaylist();
        showToast('✅ تم إنشاء بلاي ليست جديدة');
    }
}

function deleteCurrentPlaylist() {
    if (playlists.length === 1) {
        showToast('⚠️ لا يمكن حذف آخر بلاي ليست');
        return;
    }
    if (confirm('هل أنت متأكد من حذف هذه البلاي ليست؟')) {
        let index = playlists.findIndex(p => p.id === currentPlaylistId);
        playlists.splice(index, 1);
        currentPlaylistId = playlists[0].id;
        saveData();
        showToast('🗑️ تم الحذف');
    }
}

function removeFromPlaylist(index) {
    const playlist = getCurrentPlaylist();
    playlist.songs.splice(index, 1);
    if (currentPlayingPlaylistId === currentPlaylistId && currentIndex >= playlist.songs.length) currentIndex = 0;
    saveData();
    showToast('🗑️ تم الحذف');
}

function showPlaylistModal(songData) {
    pendingSong = songData;
    modalPlaylistList.innerHTML = playlists.map(p => `
        <li onclick="addToSelectedPlaylist(${p.id})">
            <i class="fas fa-music"></i>
            <span>${escapeHtml(p.name)}</span>
            <span style="margin-right: auto; font-size: 11px;">${p.songs.length}</span>
        </li>
    `).join('');
    playlistModal.classList.add('active');
}

function closeModal() {
    playlistModal.classList.remove('active');
    pendingSong = null;
}

function addToSelectedPlaylist(playlistId) {
    if (!pendingSong) return;
    const targetPlaylist = playlists.find(p => p.id === playlistId);
    if (targetPlaylist.songs.some(s => s.videoId === pendingSong.videoId)) {
        showToast('⚠️ الأغنية موجودة بالفعل');
        closeModal();
        return;
    }
    targetPlaylist.songs.push({ ...pendingSong });
    saveData();
    showToast(`✅ "${pendingSong.title.substring(0, 30)}" تمت الإضافة`);
    closeModal();
    if (playlistId === currentPlaylistId) renderCurrentPlaylist();
}

async function searchSongs() {
    const query = searchInput.value.trim();
    if (!query) { showToast('⚠️ اكتب اسم الأغنية'); return; }
    
    showLoading('🔍 جاري البحث عن: ' + query);
    
    try {
        const res = await fetch(`${API_URL}/search?q=${encodeURIComponent(query)}&limit=20`);
        const data = await res.json();
        const songs = data.results || data;
        
        setTimeout(() => {
            hideLoading();
            if (songs && songs.length > 0) {
                searchResults.innerHTML = songs.map(song => {
                    const videoId = song.id;
                    return `
                        <div class="song-card">
                            <img src="${song.thumbnail}" onclick="playSongById('${videoId}','${escapeHtml(song.title)}','${currentPlaylistId}',0)">
                            <h4>${escapeHtml(song.title.substring(0, 35))}</h4>
                            <p>${song.duration ? formatTime(song.duration) : 'Live'}</p>
                            <button class="add-btn" onclick="event.stopPropagation(); showPlaylistModal({videoId:'${videoId}',title:'${escapeHtml(song.title)}',thumbnail:'${song.thumbnail}',duration:${song.duration || 0},id:Date.now()})">
                                <i class="fas fa-plus"></i> أضف
                            </button>
                        </div>
                    `;
                }).join('');
                showToast(`✅ ${songs.length} نتيجة`);
            } else {
                searchResults.innerHTML = '<div class="empty-playlist">❌ لا توجد نتائج<br>💡 جرب كلمات مختلفة</div>';
                showToast('❌ لا توجد نتائج');
            }
        }, 500);
    } catch (e) {
        hideLoading();
        showToast('❌ خطأ في البحث');
        console.error(e);
    }
}

async function loadRecommendations() {
    recResults.innerHTML = '<div class="empty-playlist">🎵 جاري التحميل...</div>';
    try {
        const res = await fetch(`${API_URL}/recommendations`);
        const songs = await res.json();
        if (songs && songs.length > 0) {
            recResults.innerHTML = songs.map(song => {
                const videoId = song.id;
                return `
                    <div class="song-card">
                        <img src="${song.thumbnail}" onclick="playSongById('${videoId}','${escapeHtml(song.title)}','${currentPlaylistId}',0)">
                        <h4>${escapeHtml(song.title.substring(0, 35))}</h4>
                        <p>${song.duration ? formatTime(song.duration) : 'Live'}</p>
                        <button class="add-btn" onclick="event.stopPropagation(); showPlaylistModal({videoId:'${videoId}',title:'${escapeHtml(song.title)}',thumbnail:'${song.thumbnail}',duration:${song.duration || 0},id:Date.now()})">
                            <i class="fas fa-plus"></i> أضف
                        </button>
                    </div>
                `;
            }).join('');
        } else {
            recResults.innerHTML = '<div class="empty-playlist">🎵 لا توجد توصيات حالياً</div>';
        }
    } catch (e) {
        recResults.innerHTML = '<div class="empty-playlist">❌ خطأ في التحميل</div>';
    }
}

function playSongById(videoId, title, playlistId, index) {
    if (!videoId) { 
        showToast('❌ لا يمكن تشغيل هذه الأغنية - معرف غير صالح'); 
        return; 
    }
    
    console.log('Playing song:', videoId, title);
    
    currentTitle.innerHTML = title.substring(0, 50);
    currentArtist.innerHTML = 'Dio Music';
    currentVideoId = videoId;
    currentPlayingPlaylistId = playlistId;
    currentIndex = index;
    
    progressFill.style.width = '0%';
    currentTimeSpan.innerText = '0:00';
    durationSpan.innerText = '0:00';
    playerReady = false;
    
    playerWrapper.style.display = 'block';
    
    // Create player with videoId
    const success = createPlayer(videoId);
    if (!success) {
        showToast('❌ فشل في تشغيل الأغنية');
    }
    
    renderCurrentPlaylist();
    
    fetch(`${API_URL}/last-played`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title: title })
    }).catch(e => console.error(e));
    
    setTimeout(loadRecommendations, 1000);
}

function getNextIndex() {
    const playlist = playlists.find(p => p.id === currentPlayingPlaylistId);
    if (!playlist || playlist.songs.length === 0) return -1;
    if (shuffleMode) {
        let newIndex = Math.floor(Math.random() * playlist.songs.length);
        while (newIndex === currentIndex && playlist.songs.length > 1) newIndex = Math.floor(Math.random() * playlist.songs.length);
        return newIndex;
    }
    return (currentIndex + 1) % playlist.songs.length;
}

function nextSong() {
    const playlist = playlists.find(p => p.id === currentPlayingPlaylistId);
    if (!playlist || playlist.songs.length === 0) { 
        showToast('🎵 البلاي ليست فارغة'); 
        return; 
    }
    let nextIdx = getNextIndex();
    if (nextIdx === -1) return;
    currentIndex = nextIdx;
    let song = playlist.songs[currentIndex];
    playSongById(song.videoId, song.title, currentPlayingPlaylistId, currentIndex);
}

function prevSong() {
    const playlist = playlists.find(p => p.id === currentPlayingPlaylistId);
    if (!playlist || playlist.songs.length === 0) { 
        showToast('🎵 البلاي ليست فارغة'); 
        return; 
    }
    if (shuffleMode) {
        let newIndex = Math.floor(Math.random() * playlist.songs.length);
        while (newIndex === currentIndex && playlist.songs.length > 1) newIndex = Math.floor(Math.random() * playlist.songs.length);
        currentIndex = newIndex;
    } else {
        currentIndex = (currentIndex - 1 + playlist.songs.length) % playlist.songs.length;
    }
    let song = playlist.songs[currentIndex];
    playSongById(song.videoId, song.title, currentPlayingPlaylistId, currentIndex);
}

function playPause() {
    if (!player || !playerReady) {
        const playlist = getCurrentPlaylist();
        if (playlist && playlist.songs.length > 0) {
            playSongById(playlist.songs[0].videoId, playlist.songs[0].title, currentPlaylistId, 0);
        } else {
            showToast('🎵 أضف أغاني أولاً');
        }
        return;
    }
    if (isPlaying) {
        player.pauseVideo();
    } else {
        player.playVideo();
    }
}

function toggleShuffle() {
    shuffleMode = !shuffleMode;
    if (shuffleMode) {
        shuffleBtn.classList.add('mode-btn-active');
        showToast('🔀 تشغيل عشوائي');
    } else {
        shuffleBtn.classList.remove('mode-btn-active');
        showToast('🔀 إيقاف العشوائي');
    }
}

function toggleRepeat() {
    if (repeatMode === 'none') {
        repeatMode = 'one';
        repeatBtn.innerHTML = '<i class="fas fa-repeat-1"></i>';
        repeatBtn.classList.add('mode-btn-active');
        showToast('🔁 تكرار أغنية واحدة');
    } else if (repeatMode === 'one') {
        repeatMode = 'all';
        repeatBtn.innerHTML = '<i class="fas fa-repeat"></i>';
        repeatBtn.classList.add('mode-btn-active');
        showToast('🔄 تكرار البلاي ليست');
    } else {
        repeatMode = 'none';
        repeatBtn.innerHTML = '<i class="fas fa-repeat"></i>';
        repeatBtn.classList.remove('mode-btn-active');
        showToast('⏹️ إيقاف التكرار');
    }
}

function formatTime(sec) {
    if (!sec || isNaN(sec) || sec === 0) return '0:00';
    const mins = Math.floor(sec / 60);
    const secs = Math.floor(sec % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
}

function escapeHtml(str) {
    if (!str) return '';
    return str.replace(/[&<>]/g, m => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;' }[m]));
}

function showToast(msg) {
    const toast = document.createElement('div');
    toast.className = 'toast';
    toast.innerHTML = msg;
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 2500);
}

// Make functions global for onclick
window.switchPlaylist = switchPlaylist;
window.playSongById = playSongById;
window.removeFromPlaylist = removeFromPlaylist;
window.addToSelectedPlaylist = addToSelectedPlaylist;
window.showPlaylistModal = showPlaylistModal;

init();