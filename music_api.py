from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import yt_dlp
import random

app = Flask(__name__)
CORS(app)

last_played_song = None

def search_youtube(query):
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'extract_flat': True,
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch15:{query}", download=False)
            results = []
            for entry in info.get('entries', []):
                if entry and entry.get('id'):
                    results.append({
                        'id': entry['id'],
                        'title': entry.get('title', 'No title'),
                        'duration': entry.get('duration', 0),
                        'embed_url': f"https://www.youtube.com/embed/{entry['id']}",
                        'thumbnail': f"https://img.youtube.com/vi/{entry['id']}/hqdefault.jpg"
                    })
            return results
    except Exception as e:
        print(f"Search error: {e}")
        return []

def get_recommendations():
    global last_played_song
    if last_played_song:
        results = search_youtube(last_played_song)
        if results:
            return results[:8]
    
    defaults = ["pop music", "top songs", "trending", "hits", "remix", "relaxing"]
    all_recs = []
    for q in defaults:
        res = search_youtube(q)
        if res:
            all_recs.extend(res[:2])
    return all_recs[:12]

HTML = '''
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dio Music - Listeen With No Limits</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
    <script src="https://www.youtube.com/iframe_api"></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }

        body {
            background: linear-gradient(135deg, #0f0c29 0%, #1a1a3e 50%, #24243e 100%);
            min-height: 100vh;
            color: white;
            padding-bottom: 140px;
        }

        ::-webkit-scrollbar { width: 6px; }
        ::-webkit-scrollbar-track { background: rgba(255,255,255,0.1); border-radius: 10px; }
        ::-webkit-scrollbar-thumb { background: #a855f7; border-radius: 10px; }

        .container { max-width: 1400px; margin: 0 auto; padding: 20px; }

        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 30px;
            flex-wrap: wrap;
            gap: 20px;
        }
        .logo h1 {
            font-size: 28px;
            background: linear-gradient(135deg, #ffffff, #a855f7, #c084fc);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .logo p { font-size: 12px; color: #a0a0c0; margin-top: 5px; }

        .search-box {
            background: rgba(255,255,255,0.08);
            border-radius: 50px;
            padding: 5px 20px;
            display: flex;
            align-items: center;
            gap: 15px;
            border: 1px solid rgba(168,85,247,0.3);
            transition: all 0.3s;
        }
        .search-box:focus-within {
            border-color: #a855f7;
            box-shadow: 0 0 15px rgba(168,85,247,0.3);
        }
        .search-box i { color: #a855f7; font-size: 18px; }
        .search-box input {
            flex: 1;
            background: none;
            border: none;
            padding: 14px 0;
            color: white;
            font-size: 15px;
            outline: none;
        }
        .search-box input::placeholder { color: #888; }
        .search-box button {
            background: linear-gradient(135deg, #7c3aed, #a855f7);
            border: none;
            padding: 10px 25px;
            border-radius: 40px;
            color: white;
            font-weight: bold;
            cursor: pointer;
            transition: transform 0.2s;
        }
        .search-box button:hover { transform: scale(1.02); }

        .main-layout {
            display: flex;
            gap: 25px;
            margin-top: 20px;
            flex-wrap: wrap;
        }

        .sidebar {
            width: 280px;
            background: rgba(15, 12, 35, 0.6);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 20px;
            border: 1px solid rgba(168,85,247,0.2);
            height: fit-content;
        }
        .sidebar h3 {
            font-size: 16px;
            margin-bottom: 15px;
            color: #c084fc;
        }
        .playlist-list {
            list-style: none;
            margin-bottom: 20px;
            max-height: 400px;
            overflow-y: auto;
        }
        .playlist-list li {
            padding: 12px 15px;
            margin-bottom: 5px;
            border-radius: 12px;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 12px;
            transition: all 0.2s;
            color: #ccc;
        }
        .playlist-list li i { width: 24px; color: #a855f7; }
        .playlist-list li:hover {
            background: rgba(168,85,247,0.2);
            color: white;
        }
        .playlist-list li.active {
            background: linear-gradient(135deg, rgba(124,58,237,0.3), rgba(168,85,247,0.2));
            border-right: 3px solid #a855f7;
            color: white;
        }
        .create-playlist-btn {
            width: 100%;
            padding: 12px;
            background: rgba(168,85,247,0.2);
            border: 1px dashed #a855f7;
            border-radius: 12px;
            color: #a855f7;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
            transition: all 0.2s;
        }
        .create-playlist-btn:hover {
            background: rgba(168,85,247,0.4);
        }

        .main-content {
            flex: 1;
            min-width: 300px;
        }

        .tabs {
            display: flex;
            gap: 10px;
            margin-bottom: 25px;
            background: rgba(0,0,0,0.3);
            padding: 5px;
            border-radius: 50px;
            width: fit-content;
        }
        .tab {
            padding: 10px 25px;
            border-radius: 40px;
            cursor: pointer;
            transition: all 0.3s;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .tab i { font-size: 16px; }
        .tab.active {
            background: linear-gradient(135deg, #7c3aed, #a855f7);
            color: white;
        }

        .panel { display: none; animation: fadeIn 0.3s; }
        .panel.active { display: block; }
        @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }

        .songs-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
            gap: 20px;
        }
        .song-card {
            background: rgba(255,255,255,0.06);
            border-radius: 16px;
            padding: 15px;
            cursor: pointer;
            transition: all 0.3s;
            border: 1px solid rgba(168,85,247,0.1);
        }
        .song-card:hover {
            background: rgba(168,85,247,0.15);
            transform: translateY(-5px);
            border-color: #a855f7;
        }
        .song-card img {
            width: 100%;
            aspect-ratio: 1;
            border-radius: 12px;
            object-fit: cover;
        }
        .song-card h4 {
            margin: 12px 0 5px;
            font-size: 14px;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }
        .song-card p { font-size: 11px; color: #aaa; }
        .add-btn {
            margin-top: 10px;
            padding: 6px 12px;
            background: rgba(168,85,247,0.3);
            border: none;
            border-radius: 25px;
            color: white;
            cursor: pointer;
            font-size: 12px;
            transition: all 0.2s;
            width: 100%;
        }
        .add-btn:hover { background: #a855f7; }

        .playlist-songs {
            margin-top: 20px;
        }
        .playlist-song-item {
            background: rgba(255,255,255,0.05);
            border-radius: 12px;
            padding: 12px;
            margin-bottom: 8px;
            display: flex;
            align-items: center;
            gap: 15px;
            transition: all 0.2s;
        }
        .playlist-song-item:hover { background: rgba(168,85,247,0.1); }
        .playlist-song-item img {
            width: 45px;
            height: 45px;
            border-radius: 8px;
            cursor: pointer;
        }
        .playlist-song-info {
            flex: 1;
            cursor: pointer;
        }
        .playlist-song-info h4 { font-size: 14px; }
        .playlist-song-info p { font-size: 11px; color: #aaa; }
        .playlist-song-actions button {
            background: none;
            border: none;
            color: #aaa;
            font-size: 16px;
            cursor: pointer;
            padding: 5px 8px;
            transition: all 0.2s;
        }
        .playlist-song-actions button:hover { color: #a855f7; }
        .playlist-song-actions .delete-song:hover { color: #ef4444; }

        .player-bar {
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            background: linear-gradient(90deg, #0f0a1a, #1a0f2e);
            padding: 15px 25px;
            border-top: 1px solid rgba(168,85,247,0.3);
            backdrop-filter: blur(10px);
            z-index: 1000;
        }
        .player-info {
            display: flex;
            align-items: center;
            gap: 15px;
            margin-bottom: 10px;
        }
        .player-info i { font-size: 28px; color: #a855f7; }
        .player-info h4 { font-size: 14px; }
        
        .progress-section {
            margin: 10px 0;
        }
        .progress-bar-container {
            display: flex;
            align-items: center;
            gap: 15px;
            flex: 1;
        }
        .progress-bar {
            flex: 1;
            height: 5px;
            background: rgba(255,255,255,0.2);
            border-radius: 5px;
            cursor: pointer;
            position: relative;
        }
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #a855f7, #c084fc);
            border-radius: 5px;
            width: 0%;
            transition: width 0.1s linear;
        }
        .time {
            font-size: 12px;
            color: #aaa;
            min-width: 45px;
        }
        
        .player-controls {
            display: flex;
            justify-content: center;
            gap: 20px;
            align-items: center;
            margin: 10px 0;
        }
        .player-controls button {
            background: none;
            border: none;
            color: white;
            font-size: 18px;
            cursor: pointer;
            transition: all 0.2s;
            width: 40px;
            height: 40px;
            border-radius: 50%;
        }
        .player-controls button:hover {
            background: rgba(168,85,247,0.2);
            color: #a855f7;
        }
        .player-controls .play-btn {
            background: #a855f7;
            width: 48px;
            height: 48px;
            font-size: 20px;
        }
        .player-controls .play-btn:hover {
            background: #7c3aed;
            transform: scale(1.05);
            color: white;
        }
        .mode-btn.active {
            color: #a855f7;
            background: rgba(168,85,247,0.2);
        }
        
        .volume-control {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-top: 10px;
        }
        .volume-control input {
            width: 100px;
            height: 4px;
            -webkit-appearance: none;
            background: rgba(255,255,255,0.2);
            border-radius: 5px;
        }
        .volume-control input::-webkit-slider-thumb {
            -webkit-appearance: none;
            width: 12px;
            height: 12px;
            background: #a855f7;
            border-radius: 50%;
            cursor: pointer;
        }

        #youtubePlayer {
            width: 100%;
            height: 280px;
            border-radius: 16px;
            margin-top: 20px;
        }

        .empty-state {
            text-align: center;
            padding: 50px;
            color: #888;
        }

        .loading-overlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(5, 4, 14, 0.92);
            backdrop-filter: blur(8px);
            z-index: 9999;
            display: flex;
            justify-content: center;
            align-items: center;
            flex-direction: column;
            gap: 25px;
        }
        .loading-overlay.hidden {
            display: none;
        }
        .loading-container {
            position: relative;
            width: 70%;
            max-width: 450px;
            height: 24px;
            background: radial-gradient(circle, #1b0f2e, #0a0515);
            border-radius: 30px;
            overflow: hidden;
            border: 1px solid #a855f7;
        }
        .loading-bar {
            position: absolute;
            top: 0;
            left: 0;
            height: 100%;
            width: 0%;
            background: linear-gradient(90deg, #a855f7, #7c3aed, #c084fc);
            border-radius: 30px;
            transition: width 0.15s linear;
        }
        .loading-text {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            font-size: 11px;
            font-weight: bold;
            color: #fff;
            z-index: 2;
        }
        .loading-message {
            color: #c084fc;
            font-size: 14px;
            animation: pulse 1s infinite;
        }
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }

        .modal {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0,0,0,0.8);
            z-index: 2000;
            align-items: center;
            justify-content: center;
            backdrop-filter: blur(5px);
        }
        .modal.active {
            display: flex;
        }
        .modal-content {
            background: linear-gradient(135deg, #1a0f2e, #0f0a1a);
            border-radius: 20px;
            padding: 25px;
            width: 320px;
            border: 1px solid #a855f7;
        }
        .modal-content h3 {
            margin-bottom: 20px;
            color: #c084fc;
        }
        .modal-playlist-list {
            list-style: none;
            max-height: 300px;
            overflow-y: auto;
            margin-bottom: 20px;
        }
        .modal-playlist-list li {
            padding: 12px;
            margin-bottom: 8px;
            background: rgba(255,255,255,0.05);
            border-radius: 10px;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .modal-playlist-list li:hover {
            background: rgba(168,85,247,0.3);
        }
        .modal-playlist-list li i { color: #a855f7; }
        .modal-close {
            width: 100%;
            padding: 10px;
            background: rgba(239,68,68,0.3);
            border: none;
            border-radius: 10px;
            color: white;
            cursor: pointer;
        }

        .toast {
            position: fixed;
            bottom: 120px;
            right: 20px;
            background: #10b981;
            padding: 12px 24px;
            border-radius: 50px;
            z-index: 2000;
            animation: slideIn 0.3s;
            font-size: 13px;
        }
        @keyframes slideIn {
            from { transform: translateX(100%); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }

        @media (max-width: 768px) {
            .sidebar { width: 100%; }
            .songs-grid { grid-template-columns: repeat(auto-fill, minmax(150px, 1fr)); }
            #youtubePlayer { height: 200px; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="logo">
                <h1><i class="fas fa-headphones"></i> Dio Music</h1>
                <p>Listen With No Limits</p>
            </div>
            <div class="search-box">
                <i class="fas fa-search"></i>
                <input type="text" id="searchInput" placeholder="ابحث عن أغنية، فنان...">
                <button onclick="searchSongs()">بحث</button>
            </div>
        </div>

        <div class="main-layout">
            <div class="sidebar">
                <h3><i class="fas fa-list"></i> بلاي ليستاتي</h3>
                <ul class="playlist-list" id="playlistList"></ul>
                <button class="create-playlist-btn" onclick="createNewPlaylist()">
                    <i class="fas fa-plus"></i> بلاي ليست جديدة
                </button>
            </div>

            <div class="main-content">
                <div class="tabs">
                    <div class="tab active" data-tab="search">
                        <i class="fas fa-search"></i> بحث
                    </div>
                    <div class="tab" data-tab="current-playlist">
                        <i class="fas fa-music"></i> البلاي ليست
                    </div>
                    <div class="tab" data-tab="recommendations">
                        <i class="fas fa-chart-line"></i> توصيات
                    </div>
                </div>

                <div id="searchPanel" class="panel active">
                    <div id="searchResults" class="songs-grid"></div>
                </div>

                <div id="currentPlaylistPanel" class="panel">
                    <div>
                        <h3 id="currentPlaylistName" style="margin-bottom: 20px;"></h3>
                        <button class="add-btn" onclick="deleteCurrentPlaylist()" style="background: #ef4444; margin-bottom: 15px; width: auto;">
                            <i class="fas fa-trash"></i> حذف البلاي ليست
                        </button>
                    </div>
                    <div id="playlistSongsContainer"></div>
                </div>

                <div id="recPanel" class="panel">
                    <h3 style="margin-bottom: 20px;"><i class="fas fa-star"></i> موصى بها لك</h3>
                    <div id="recResults" class="songs-grid"></div>
                </div>

                <div id="playerWrapper" style="display: none;">
                    <div id="youtubePlayer"></div>
                </div>
            </div>
        </div>
    </div>

    <div class="player-bar">
        <div class="player-info">
            <i class="fas fa-music"></i>
            <div><h4 id="currentTitle">اختار أغنية</h4></div>
        </div>
        
        <div class="progress-section">
            <div class="progress-bar-container">
                <span class="time" id="currentTime">0:00</span>
                <div class="progress-bar" id="progressBar">
                    <div class="progress-fill" id="progressFill"></div>
                </div>
                <span class="time" id="totalDuration">0:00</span>
            </div>
        </div>
        
        <div class="player-controls">
            <button id="shuffleBtn" onclick="toggleShuffle()"><i class="fas fa-random"></i></button>
            <button onclick="prevSong()"><i class="fas fa-backward-step"></i></button>
            <button class="play-btn" onclick="playPause()" id="playPauseBtn"><i class="fas fa-play"></i></button>
            <button onclick="nextSong()"><i class="fas fa-forward-step"></i></button>
            <button id="repeatBtn" onclick="toggleRepeat()"><i class="fas fa-repeat"></i></button>
        </div>
        
        <div class="volume-control">
            <i class="fas fa-volume-up"></i>
            <input type="range" id="volume" min="0" max="100" value="70">
        </div>
    </div>

    <div id="playlistModal" class="modal">
        <div class="modal-content">
            <h3><i class="fas fa-folder-plus"></i> اختر البلاي ليست</h3>
            <ul class="modal-playlist-list" id="modalPlaylistList"></ul>
            <button class="modal-close" onclick="closeModal()"><i class="fas fa-times"></i> إلغاء</button>
        </div>
    </div>

    <div id="loadingOverlay" class="loading-overlay hidden">
        <div class="loading-container">
            <div class="loading-bar" id="loadingBar"></div>
            <div class="loading-text" id="loadingText">0%</div>
        </div>
        <div class="loading-message" id="loadingMessage">🔍 جاري البحث...</div>
    </div>

    <script>
        let playlists = [];
        let currentPlaylistId = null;
        let currentIndex = 0;
        let isPlaying = false;
        let currentVideoId = null;
        let currentPlayingPlaylistId = null;
        let shuffleMode = false;
        let repeatMode = 'none';
        let pendingSong = null;
        
        let player = null;
        let playerReady = false;
        
        // DOM Elements
        const searchInput = document.getElementById('searchInput');
        const playlistList = document.getElementById('playlistList');
        const playlistSongsContainer = document.getElementById('playlistSongsContainer');
        const currentPlaylistName = document.getElementById('currentPlaylistName');
        const searchResults = document.getElementById('searchResults');
        const recResults = document.getElementById('recResults');
        const currentTitle = document.getElementById('currentTitle');
        const playPauseBtn = document.getElementById('playPauseBtn');
        const progressFill = document.getElementById('progressFill');
        const currentTimeSpan = document.getElementById('currentTime');
        const totalDurationSpan = document.getElementById('totalDuration');
        const progressBar = document.getElementById('progressBar');
        const volumeSlider = document.getElementById('volume');
        const playerWrapper = document.getElementById('playerWrapper');
        
        // Loading functions
        function showLoading(msg) {
            document.getElementById('loadingMessage').textContent = msg;
            document.getElementById('loadingOverlay').classList.remove('hidden');
            let loadingBar = document.getElementById('loadingBar');
            let loadingText = document.getElementById('loadingText');
            loadingBar.style.width = '0%';
            loadingText.textContent = '0%';
            let percent = 0;
            let interval = setInterval(() => {
                percent += Math.random() * 15;
                if (percent >= 95) {
                    percent = 95;
                    clearInterval(interval);
                }
                loadingBar.style.width = percent + '%';
                loadingText.textContent = Math.floor(percent) + '%';
            }, 150);
            return interval;
        }
        
        function hideLoading(interval) {
            if(interval) clearInterval(interval);
            let loadingBar = document.getElementById('loadingBar');
            let loadingText = document.getElementById('loadingText');
            loadingBar.style.width = '100%';
            loadingText.textContent = '100%';
            setTimeout(() => {
                document.getElementById('loadingOverlay').classList.add('hidden');
                loadingBar.style.width = '0%';
            }, 300);
        }
        
        // YouTube Player
        function onYouTubeIframeAPIReady() {
            console.log('YouTube API ready');
        }
        
        function createPlayer(videoId) {
            if(player) player.destroy();
            player = new YT.Player('youtubePlayer', {
                height: '280',
                width: '100%',
                videoId: videoId,
                playerVars: { 'autoplay': 1, 'controls': 0, 'rel': 0, 'modestbranding': 1, 'enablejsapi': 1 },
                events: {
                    'onReady': onPlayerReady,
                    'onStateChange': onPlayerStateChange,
                    'onError': onPlayerError
                }
            });
        }
        
        function onPlayerReady(event) {
            playerReady = true;
            let duration = player.getDuration();
            totalDurationSpan.innerText = formatTime(duration);
            player.setVolume(volumeSlider.value);
            startProgressUpdate();
        }
        
        function onPlayerStateChange(event) {
            if(event.data === YT.PlayerState.ENDED) {
                if(repeatMode === 'one') { player.seekTo(0); player.playVideo(); }
                else { nextSong(); }
            } else if(event.data === YT.PlayerState.PLAYING) {
                isPlaying = true;
                playPauseBtn.innerHTML = '<i class="fas fa-pause"></i>';
                let duration = player.getDuration();
                if(duration) totalDurationSpan.innerText = formatTime(duration);
            } else if(event.data === YT.PlayerState.PAUSED) {
                isPlaying = false;
                playPauseBtn.innerHTML = '<i class="fas fa-play"></i>';
            }
        }
        
        function onPlayerError(event) {
            console.error('Error:', event);
            showToast('⚠️ خطأ في التشغيل');
        }
        
        function startProgressUpdate() {
            function update() {
                if(player && player.getCurrentTime && playerReady) {
                    let current = player.getCurrentTime();
                    let duration = player.getDuration();
                    if(duration > 0) {
                        let percent = (current / duration) * 100;
                        progressFill.style.width = percent + '%';
                        currentTimeSpan.innerText = formatTime(current);
                    }
                }
                requestAnimationFrame(update);
            }
            update();
        }
        
        function seek(e) {
            if(!player || !playerReady) return;
            let rect = progressBar.getBoundingClientRect();
            let x = e.clientX - rect.left;
            let percent = x / rect.width;
            if(percent > 1) percent = 1;
            if(percent < 0) percent = 0;
            let duration = player.getDuration();
            player.seekTo(percent * duration, true);
        }
        
        // Data functions
        function loadData() {
            let saved = localStorage.getItem('dio_playlists');
            if(saved) playlists = JSON.parse(saved);
        }
        
        function saveData() {
            localStorage.setItem('dio_playlists', JSON.stringify(playlists));
            renderPlaylistsList();
            renderCurrentPlaylist();
        }
        
        function renderPlaylistsList() {
            if(playlists.length === 0) {
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
            let playlist = playlists.find(p => p.id === currentPlaylistId);
            if(!playlist) return;
            currentPlaylistName.innerHTML = `<i class="fas fa-headphones"></i> ${escapeHtml(playlist.name)} (${playlist.songs.length} أغنية)`;
            if(playlist.songs.length === 0) {
                playlistSongsContainer.innerHTML = '<div class="empty-state">📭 البلاي ليست فارغة<br>➕ أضف أغاني من البحث</div>';
                return;
            }
            playlistSongsContainer.innerHTML = playlist.songs.map((song, idx) => `
                <div class="playlist-song-item ${idx === currentIndex && currentPlayingPlaylistId === currentPlaylistId ? 'active' : ''}">
                    <img src="${song.thumbnail}" onclick="playSong('${song.videoId}','${escapeHtml(song.title)}','${currentPlaylistId}',${idx})">
                    <div class="playlist-song-info" onclick="playSong('${song.videoId}','${escapeHtml(song.title)}','${currentPlaylistId}',${idx})">
                        <h4>${escapeHtml(song.title.substring(0,50))}</h4>
                        <p>${formatTime(song.duration)}</p>
                    </div>
                    <div class="playlist-song-actions">
                        <button onclick="playSong('${song.videoId}','${escapeHtml(song.title)}','${currentPlaylistId}',${idx})"><i class="fas fa-play"></i></button>
                        <button class="delete-song" onclick="removeFromPlaylist(${idx})"><i class="fas fa-trash"></i></button>
                    </div>
                </div>
            `).join('');
        }
        
        function switchPlaylist(id) {
            currentPlaylistId = id;
            renderPlaylistsList();
            renderCurrentPlaylist();
            document.querySelector('.tab[data-tab="current-playlist"]').click();
        }
        
        function createNewPlaylist() {
            let name = prompt('اسم البلاي ليست الجديدة:', 'بلاي ليست جديدة');
            if(name && name.trim()) {
                playlists.push({ id: Date.now(), name: name.trim(), songs: [] });
                saveData();
                currentPlaylistId = playlists[playlists.length-1].id;
                renderPlaylistsList();
                renderCurrentPlaylist();
                showToast('✅ تم الإنشاء');
            }
        }
        
        function deleteCurrentPlaylist() {
            if(playlists.length === 1) { showToast('⚠️ لا يمكن الحذف'); return; }
            if(confirm('حذف هذه البلاي ليست؟')) {
                let index = playlists.findIndex(p => p.id === currentPlaylistId);
                playlists.splice(index, 1);
                currentPlaylistId = playlists[0].id;
                saveData();
                showToast('🗑️ تم الحذف');
            }
        }
        
        function removeFromPlaylist(index) {
            let playlist = playlists.find(p => p.id === currentPlaylistId);
            playlist.songs.splice(index, 1);
            if(currentPlayingPlaylistId === currentPlaylistId && currentIndex >= playlist.songs.length) currentIndex = 0;
            saveData();
            showToast('🗑️ تم الحذف');
        }
        
        function showPlaylistModal(songData) {
            pendingSong = songData;
            let modalList = document.getElementById('modalPlaylistList');
            modalList.innerHTML = playlists.map(p => `
                <li onclick="addToSelectedPlaylist(${p.id})">
                    <i class="fas fa-music"></i>
                    <span>${escapeHtml(p.name)}</span>
                    <span style="margin-right: auto;">${p.songs.length}</span>
                </li>
            `).join('');
            document.getElementById('playlistModal').classList.add('active');
        }
        
        function closeModal() {
            document.getElementById('playlistModal').classList.remove('active');
            pendingSong = null;
        }
        
        function addToSelectedPlaylist(playlistId) {
            if(!pendingSong) return;
            let target = playlists.find(p => p.id === playlistId);
            if(target.songs.some(s => s.videoId === pendingSong.videoId)) {
                showToast('⚠️ موجودة بالفعل');
                closeModal();
                return;
            }
            target.songs.push(pendingSong);
            saveData();
            showToast(`✅ تمت الإضافة إلى ${target.name}`);
            closeModal();
            if(playlistId === currentPlaylistId) renderCurrentPlaylist();
        }
        
        async function searchSongs() {
            let q = searchInput.value.trim();
            if(!q) { showToast('⚠️ اكتب اسم الأغنية'); return; }
            let loadingInterval = showLoading('🔍 جاري البحث عن: ' + q);
            try {
                let res = await fetch(`/api/search?q=${encodeURIComponent(q)}`);
                let songs = await res.json();
                hideLoading(loadingInterval);
                if(songs.length > 0) {
                    searchResults.innerHTML = songs.map(song => `
                        <div class="song-card">
                            <img src="${song.thumbnail}" onclick="playSong('${song.id}','${escapeHtml(song.title)}','${currentPlaylistId}',0)">
                            <h4>${escapeHtml(song.title.substring(0,35))}</h4>
                            <p>${formatTime(song.duration)}</p>
                            <button class="add-btn" onclick="event.stopPropagation(); showPlaylistModal({videoId:'${song.id}',title:'${escapeHtml(song.title)}',thumbnail:'${song.thumbnail}',duration:${song.duration},id:Date.now()})">
                                <i class="fas fa-plus"></i> أضف
                            </button>
                        </div>
                    `).join('');
                    showToast(`✅ ${songs.length} نتيجة`);
                } else {
                    searchResults.innerHTML = '<div class="empty-state">❌ لا توجد نتائج</div>';
                }
            } catch(e) { hideLoading(loadingInterval); showToast('❌ خطأ'); }
        }
        
        async function loadRecommendations() {
            recResults.innerHTML = '<div class="empty-state">🎵 جاري التحميل...</div>';
            try {
                let res = await fetch('/api/recommendations');
                let songs = await res.json();
                if(songs.length > 0) {
                    recResults.innerHTML = songs.map(song => `
                        <div class="song-card">
                            <img src="${song.thumbnail}" onclick="playSong('${song.id}','${escapeHtml(song.title)}','${currentPlaylistId}',0)">
                            <h4>${escapeHtml(song.title.substring(0,35))}</h4>
                            <p>${formatTime(song.duration)}</p>
                            <button class="add-btn" onclick="event.stopPropagation(); showPlaylistModal({videoId:'${song.id}',title:'${escapeHtml(song.title)}',thumbnail:'${song.thumbnail}',duration:${song.duration},id:Date.now()})">
                                <i class="fas fa-plus"></i> أضف
                            </button>
                        </div>
                    `).join('');
                } else {
                    recResults.innerHTML = '<div class="empty-state">🎵 لا توجد توصيات</div>';
                }
            } catch(e) { recResults.innerHTML = '<div class="empty-state">❌ خطأ</div>'; }
        }
        
        function playSong(videoId, title, playlistId, index) {
            if(!videoId) { showToast('❌ لا يمكن التشغيل'); return; }
            currentTitle.innerHTML = title;
            currentVideoId = videoId;
            currentPlayingPlaylistId = playlistId;
            currentIndex = index;
            playerWrapper.style.display = 'block';
            createPlayer(videoId);
            renderCurrentPlaylist();
            fetch('/api/last-played', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ title: title })
            });
            setTimeout(loadRecommendations, 1000);
        }
        
        function getNextIndex() {
            let playlist = playlists.find(p => p.id === currentPlayingPlaylistId);
            if(!playlist || playlist.songs.length === 0) return -1;
            if(shuffleMode) {
                let newIdx = Math.floor(Math.random() * playlist.songs.length);
                while(newIdx === currentIndex && playlist.songs.length > 1) newIdx = Math.floor(Math.random() * playlist.songs.length);
                return newIdx;
            }
            return (currentIndex + 1) % playlist.songs.length;
        }
        
        function nextSong() {
            let playlist = playlists.find(p => p.id === currentPlayingPlaylistId);
            if(!playlist || playlist.songs.length === 0) { showToast('🎵 البلاي ليست فارغة'); return; }
            let nextIdx = getNextIndex();
            if(nextIdx === -1) return;
            currentIndex = nextIdx;
            let song = playlist.songs[currentIndex];
            playSong(song.videoId, song.title, currentPlayingPlaylistId, currentIndex);
        }
        
        function prevSong() {
            let playlist = playlists.find(p => p.id === currentPlayingPlaylistId);
            if(!playlist || playlist.songs.length === 0) return;
            if(shuffleMode) {
                let newIdx = Math.floor(Math.random() * playlist.songs.length);
                while(newIdx === currentIndex && playlist.songs.length > 1) newIdx = Math.floor(Math.random() * playlist.songs.length);
                currentIndex = newIdx;
            } else {
                currentIndex = (currentIndex - 1 + playlist.songs.length) % playlist.songs.length;
            }
            let song = playlist.songs[currentIndex];
            playSong(song.videoId, song.title, currentPlayingPlaylistId, currentIndex);
        }
        
        function playPause() {
            if(!player || !playerReady) {
                let playlist = playlists.find(p => p.id === currentPlaylistId);
                if(playlist && playlist.songs.length > 0) {
                    playSong(playlist.songs[0].videoId, playlist.songs[0].title, currentPlaylistId, 0);
                } else {
                    showToast('🎵 أضف أغاني أولاً');
                }
                return;
            }
            if(isPlaying) player.pauseVideo();
            else player.playVideo();
        }
        
        function toggleShuffle() {
            shuffleMode = !shuffleMode;
            document.getElementById('shuffleBtn').classList.toggle('active', shuffleMode);
            showToast(shuffleMode ? '🔀 عشوائي' : '🔀 إيقاف العشوائي');
        }
        
        function toggleRepeat() {
            let btn = document.getElementById('repeatBtn');
            if(repeatMode === 'none') {
                repeatMode = 'one';
                btn.innerHTML = '<i class="fas fa-repeat-1"></i>';
                btn.classList.add('active');
                showToast('🔁 تكرار أغنية واحدة');
            } else if(repeatMode === 'one') {
                repeatMode = 'all';
                btn.innerHTML = '<i class="fas fa-repeat"></i>';
                btn.classList.add('active');
                showToast('🔄 تكرار البلاي ليست');
            } else {
                repeatMode = 'none';
                btn.innerHTML = '<i class="fas fa-repeat"></i>';
                btn.classList.remove('active');
                showToast('⏹️ إيقاف التكرار');
            }
        }
        
        function formatTime(sec) {
            if(!sec || isNaN(sec)) return '0:00';
            let mins = Math.floor(sec / 60);
            let secs = Math.floor(sec % 60);
            return `${mins}:${secs.toString().padStart(2,'0')}`;
        }
        
        function escapeHtml(str) {
            if(!str) return '';
            return str.replace(/[&<>]/g, m => ({'&':'&amp;','<':'&lt;','>':'&gt;'}[m]));
        }
        
        function showToast(msg) {
            let t = document.createElement('div');
            t.className = 'toast';
            t.innerHTML = msg;
            document.body.appendChild(t);
            setTimeout(() => t.remove(), 2500);
        }
        
        // Tab switching
        document.querySelectorAll('.tab').forEach(tab => {
            tab.addEventListener('click', () => {
                document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
                tab.classList.add('active');
                document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
                document.getElementById(tab.dataset.tab + 'Panel').classList.add('active');
                if(tab.dataset.tab === 'recommendations') loadRecommendations();
            });
        });
        
        // Volume
        volumeSlider.addEventListener('input', (e) => {
            if(player && playerReady) player.setVolume(e.target.value);
        });
        
        // Progress bar click
        progressBar.addEventListener('click', seek);
        
        // Enter search
        searchInput.addEventListener('keypress', (e) => {
            if(e.key === 'Enter') searchSongs();
        });
        
        // Close modal on outside click
        document.getElementById('playlistModal').addEventListener('click', (e) => {
            if(e.target === document.getElementById('playlistModal')) closeModal();
        });
        
        // Initialize
        loadData();
        if(playlists.length === 0) {
            playlists.push({ id: Date.now(), name: 'المفضلة', songs: [] });
            saveData();
        }
        currentPlaylistId = playlists[0].id;
        renderPlaylistsList();
        renderCurrentPlaylist();
        loadRecommendations();
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML)

@app.route('/api/search')
def search():
    q = request.args.get('q', '')
    if not q:
        return jsonify([])
    return jsonify(search_youtube(q))

@app.route('/api/recommendations')
def recommendations():
    return jsonify(get_recommendations())

@app.route('/api/last-played', methods=['POST'])
def last_played():
    global last_played_song
    data = request.get_json()
    if data:
        last_played_song = data.get('title', '')
        print(f"Last played: {last_played_song}")
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    print("=" * 50)
    print("🎵 Dio Music Pro is running!")
    print("📍 Open: http://localhost:5001")
    print("=" * 50)
    app.run(debug=True, port=5001, host='0.0.0.0')