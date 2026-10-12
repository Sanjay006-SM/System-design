import React, { useState, useEffect } from 'react';
import './App.css';

interface Topic {
  id: number;
  name: string;
  slug: string;
}

interface Article {
  id: number;
  title: string;
  description: string;
  content: string;
  source: string;
  author: string | null;
  image_url: string | null;
  published_at: string;
  region: string;
  view_count: number;
  engagement_count: number;
  topics: Topic[];
}

interface NotificationItem {
  id: number;
  article_id: number;
  message: string;
  status: string;
  created_at: string;
}

const API_BASE = 'http://localhost:8000/api/v1';

const DEMO_USERS = [
  { id: 101, name: 'Alex Chen', email: 'alex.chen@example.com', badge: 'Tech & AI Lead' },
  { id: 102, name: 'Priya Sharma', email: 'priya.sharma@example.com', badge: 'Markets & Policy' },
  { id: 103, name: 'David Miller', email: 'david.miller@example.com', badge: 'Global Science' },
  { id: 104, name: 'Guest Explorer', email: 'guest@example.com', badge: 'New Explorer' },
];

export default function App() {
  const [currentUser, setCurrentUser] = useState(DEMO_USERS[0]);
  const [activeTab, setActiveTab] = useState<'personalized' | 'trending' | 'search' | 'topics'>('personalized');
  const [articles, setArticles] = useState<Article[]>([]);
  const [trendingArticles, setTrendingArticles] = useState<Article[]>([]);
  const [allTopics, setAllTopics] = useState<Topic[]>([]);
  const [userTopicIds, setUserTopicIds] = useState<number[]>([]);
  const [notifications, setNotifications] = useState<NotificationItem[]>([]);
  const [unreadNotifCount, setUnreadNotifCount] = useState(0);
  const [showNotifDrawer, setShowNotifDrawer] = useState(false);
  const [selectedArticle, setSelectedArticle] = useState<Article | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchLoading, setSearchLoading] = useState(false);
  const [systemHealth, setSystemHealth] = useState<any>(null);
  const [isDarkMode, setIsDarkMode] = useState(true);

  // New Article Form state
  const [publishForm, setPublishForm] = useState({
    title: '',
    description: '',
    content: '',
    source: 'TechWire Daily',
    author: 'Chief Editor',
    topic_names: 'Artificial Intelligence',
    region: 'GLOBAL'
  });
  const [publishing, setPublishing] = useState(false);
  const [publishFeedback, setPublishFeedback] = useState<string | null>(null);

  // Fetch initial system health & topics
  useEffect(() => {
    fetch(`${API_BASE}/health`)
      .then(r => r.json())
      .then(d => setSystemHealth(d))
      .catch(() => setSystemHealth({ status: 'offline' }));

    fetch(`${API_BASE}/topics`)
      .then(r => r.json())
      .then(data => setAllTopics(data))
      .catch(console.error);

    loadTrending();
  }, []);

  // Fetch user data when user changes
  useEffect(() => {
    loadUserTopics();
    loadPersonalizedFeed();
    loadNotifications();
  }, [currentUser]);

  const loadUserTopics = async () => {
    try {
      const res = await fetch(`${API_BASE}/users/${currentUser.id}/topics`, {
        headers: { 'X-Demo-User-Id': String(currentUser.id) }
      });
      if (res.ok) {
        const topics: Topic[] = await res.json();
        setUserTopicIds(topics.map(t => t.id));
      }
    } catch (e) {
      console.error(e);
    }
  };

  const loadPersonalizedFeed = async () => {
    try {
      const res = await fetch(`${API_BASE}/users/${currentUser.id}/feed?page=1&limit=15`, {
        headers: { 'X-Demo-User-Id': String(currentUser.id) }
      });
      if (res.ok) {
        const data = await res.json();
        setArticles(data.items || []);
      }
    } catch (e) {
      console.error(e);
    }
  };

  const loadTrending = async () => {
    try {
      const res = await fetch(`${API_BASE}/news/trending?region=GLOBAL&limit=10`);
      if (res.ok) {
        const data = await res.json();
        setTrendingArticles(data);
      }
    } catch (e) {
      console.error(e);
    }
  };

  const loadNotifications = async () => {
    try {
      const res = await fetch(`${API_BASE}/users/${currentUser.id}/notifications`, {
        headers: { 'X-Demo-User-Id': String(currentUser.id) }
      });
      if (res.ok) {
        const data = await res.json();
        setNotifications(data.items || []);
        setUnreadNotifCount(data.unread_count || 0);
      }
    } catch (e) {
      console.error(e);
    }
  };

  const handleSearch = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!searchQuery.trim()) return;
    setSearchLoading(true);
    setActiveTab('search');
    try {
      const res = await fetch(`${API_BASE}/news/search?q=${encodeURIComponent(searchQuery.trim())}&page=1&limit=20`);
      if (res.ok) {
        const data = await res.json();
        setArticles(data.items || []);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setSearchLoading(false);
    }
  };

  const handleToggleTopic = async (topicId: number) => {
    const isFollowing = userTopicIds.includes(topicId);
    try {
      if (isFollowing) {
        const res = await fetch(`${API_BASE}/users/${currentUser.id}/topics/${topicId}`, {
          method: 'DELETE',
          headers: { 'X-Demo-User-Id': String(currentUser.id) }
        });
        if (res.ok) {
          setUserTopicIds(prev => prev.filter(id => id !== topicId));
          loadPersonalizedFeed();
        }
      } else {
        const res = await fetch(`${API_BASE}/users/${currentUser.id}/topics`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-Demo-User-Id': String(currentUser.id)
          },
          body: JSON.stringify({ topicId })
        });
        if (res.ok) {
          setUserTopicIds(prev => [...prev, topicId]);
          loadPersonalizedFeed();
        }
      }
    } catch (e) {
      console.error(e);
    }
  };

  const handleArticleClick = async (articleId: number) => {
    try {
      const res = await fetch(`${API_BASE}/articles/${articleId}`);
      if (res.ok) {
        const fullArticle = await res.json();
        setSelectedArticle(fullArticle);
      }
    } catch (e) {
      console.error(e);
    }
  };

  const handlePublishNews = async (e: React.FormEvent) => {
    e.preventDefault();
    setPublishing(true);
    setPublishFeedback(null);
    try {
      const res = await fetch(`${API_BASE}/news/publish`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          title: publishForm.title,
          description: publishForm.description,
          content: publishForm.content,
          source: publishForm.source,
          author: publishForm.author,
          region: publishForm.region,
          topic_names: publishForm.topic_names.split(',').map(s => s.trim()).filter(Boolean)
        })
      });
      if (res.ok) {
        setPublishFeedback('Article published! Event published and followers notified.');
        setPublishForm({
          title: '',
          description: '',
          content: '',
          source: 'TechWire Daily',
          author: 'Chief Editor',
          topic_names: 'Artificial Intelligence',
          region: 'GLOBAL'
        });
        loadNotifications();
        loadPersonalizedFeed();
        loadTrending();
      } else {
        setPublishFeedback('Error publishing article.');
      }
    } catch (err: any) {
      setPublishFeedback('Network error: ' + err.message);
    } finally {
      setPublishing(false);
    }
  };

  const displayedArticles = activeTab === 'trending' ? trendingArticles : articles;

  return (
    <div className={`app-container ${isDarkMode ? 'dark-theme' : 'light-theme'}`}>
      {/* Top Navigation */}
      <header className="navbar">
        <div className="brand">
          <span className="logo-badge">⚡</span>
          <div>
            <h1>NexusPulse</h1>
            <p className="subheading">Personalized High-Concurrency News Engine</p>
          </div>
        </div>

        {/* Global Search Bar */}
        <form className="search-box" onSubmit={handleSearch}>
          <input
            type="text"
            placeholder="Search news by topic, title, keywords..."
            value={searchQuery}
            onChange={e => setSearchQuery(e.target.value)}
          />
          <button type="submit" disabled={searchLoading}>
            {searchLoading ? 'Searching...' : 'Search'}
          </button>
        </form>

        <div className="nav-actions">
          {/* Health Badge */}
          <div className="health-pill">
            <span className={`status-dot ${systemHealth?.status === 'healthy' ? 'healthy' : 'degraded'}`} />
            <span>{systemHealth ? systemHealth.status.toUpperCase() : 'CHECKING'}</span>
          </div>

          {/* User Switcher */}
          <div className="user-dropdown">
            <select
              value={currentUser.id}
              onChange={e => {
                const u = DEMO_USERS.find(usr => usr.id === Number(e.target.value));
                if (u) setCurrentUser(u);
              }}
            >
              {DEMO_USERS.map(u => (
                <option key={u.id} value={u.id}>
                  {u.name} ({u.badge})
                </option>
              ))}
            </select>
          </div>

          {/* Notifications Bell */}
          <button
            className="notif-btn"
            onClick={() => {
              setShowNotifDrawer(!showNotifDrawer);
              loadNotifications();
            }}
          >
            🔔
            {unreadNotifCount > 0 && <span className="notif-count">{unreadNotifCount}</span>}
          </button>

          {/* Theme Toggle */}
          <button className="theme-toggle" onClick={() => setIsDarkMode(!isDarkMode)}>
            {isDarkMode ? '☀️ Light' : '🌙 Dark'}
          </button>
        </div>
      </header>

      {/* Main Content Area */}
      <div className="layout">
        {/* Left Sidebar */}
        <aside className="sidebar">
          <nav className="tab-menu">
            <button
              className={activeTab === 'personalized' ? 'active' : ''}
              onClick={() => {
                setActiveTab('personalized');
                loadPersonalizedFeed();
              }}
            >
              📰 My Feed
            </button>
            <button
              className={activeTab === 'trending' ? 'active' : ''}
              onClick={() => {
                setActiveTab('trending');
                loadTrending();
              }}
            >
              🔥 Trending News
            </button>
            <button
              className={activeTab === 'topics' ? 'active' : ''}
              onClick={() => setActiveTab('topics')}
            >
              🏷️ Topics ({allTopics.length})
            </button>
          </nav>

          {/* Followed Topics Quick Pills */}
          <div className="sidebar-section">
            <h3>Followed Topics</h3>
            <div className="pill-cloud">
              {allTopics
                .filter(t => userTopicIds.includes(t.id))
                .map(t => (
                  <span key={t.id} className="active-pill" onClick={() => handleToggleTopic(t.id)}>
                    ✓ {t.name}
                  </span>
                ))}
              {userTopicIds.length === 0 && <p className="empty-hint">No followed topics yet. Follow some below!</p>}
            </div>
          </div>

          {/* Live Ingestion / Event Publishing Simulation */}
          <div className="sidebar-section publish-box">
            <h3>Publish Breaking News</h3>
            <p className="hint">Simulates external ingest & triggers real-time subscriber events.</p>
            <form onSubmit={handlePublishNews}>
              <input
                type="text"
                placeholder="Headline"
                value={publishForm.title}
                onChange={e => setPublishForm({ ...publishForm, title: e.target.value })}
                required
              />
              <textarea
                placeholder="Brief summary"
                rows={2}
                value={publishForm.description}
                onChange={e => setPublishForm({ ...publishForm, description: e.target.value })}
                required
              />
              <textarea
                placeholder="Full content"
                rows={3}
                value={publishForm.content}
                onChange={e => setPublishForm({ ...publishForm, content: e.target.value })}
                required
              />
              <input
                type="text"
                placeholder="Topics (comma separated, e.g. Artificial Intelligence)"
                value={publishForm.topic_names}
                onChange={e => setPublishForm({ ...publishForm, topic_names: e.target.value })}
              />
              <button type="submit" disabled={publishing}>
                {publishing ? 'Broadcasting...' : 'Publish & Broadcast Event'}
              </button>
              {publishFeedback && <p className="feedback-msg">{publishFeedback}</p>}
            </form>
          </div>
        </aside>

        {/* Center Feed Area */}
        <main className="content">
          {activeTab === 'topics' ? (
            <div className="topics-catalog">
              <h2>Explore & Follow Topics</h2>
              <p>Following topics personalizes your AI-ranked news feed with zero latency.</p>
              <div className="topic-grid">
                {allTopics.map(t => {
                  const isFollowing = userTopicIds.includes(t.id);
                  return (
                    <div key={t.id} className={`topic-card ${isFollowing ? 'following' : ''}`}>
                      <div className="topic-meta">
                        <h4>{t.name}</h4>
                        <code>#{t.slug}</code>
                      </div>
                      <button
                        className={isFollowing ? 'btn-unfollow' : 'btn-follow'}
                        onClick={() => handleToggleTopic(t.id)}
                      >
                        {isFollowing ? 'Following ✓' : '+ Follow'}
                      </button>
                    </div>
                  );
                })}
              </div>
            </div>
          ) : (
            <div>
              <div className="feed-header">
                <h2>
                  {activeTab === 'personalized'
                    ? `Personalized Feed for ${currentUser.name}`
                    : activeTab === 'trending'
                    ? 'Global Trending News'
                    : `Search Results for "${searchQuery}"`}
                </h2>
                <span className="count-pill">{displayedArticles.length} Articles</span>
              </div>

              {displayedArticles.length === 0 ? (
                <div className="empty-state">
                  <h3>No news items found</h3>
                  <p>Try searching another keyword or follow additional topics in the topics directory.</p>
                </div>
              ) : (
                <div className="articles-grid">
                  {displayedArticles.map(art => (
                    <article key={art.id} className="news-card" onClick={() => handleArticleClick(art.id)}>
                      <div className="card-header">
                        <span className="source-tag">{art.source}</span>
                        <span className="date-tag">{new Date(art.published_at).toLocaleDateString()}</span>
                      </div>
                      <h3>{art.title}</h3>
                      <p className="card-desc">{art.description}</p>
                      <div className="card-footer">
                        <div className="card-topics">
                          {art.topics.map(t => (
                            <span key={t.id} className="topic-badge">
                              {t.name}
                            </span>
                          ))}
                        </div>
                        <div className="stats-badges">
                          <span>👁️ {art.view_count}</span>
                          <span>💬 {art.engagement_count}</span>
                        </div>
                      </div>
                    </article>
                  ))}
                </div>
              )}
            </div>
          )}
        </main>
      </div>

      {/* Article Details Modal */}
      {selectedArticle && (
        <div className="modal-overlay" onClick={() => setSelectedArticle(null)}>
          <div className="modal-content" onClick={e => e.stopPropagation()}>
            <button className="modal-close" onClick={() => setSelectedArticle(null)}>
              ✕
            </button>
            <div className="modal-meta">
              <span className="source-tag">{selectedArticle.source}</span>
              <span>• Author: {selectedArticle.author || 'Editorial Desk'}</span>
              <span>• Published: {new Date(selectedArticle.published_at).toLocaleString()}</span>
              <span>• Views: {selectedArticle.view_count}</span>
            </div>
            <h2>{selectedArticle.title}</h2>
            <div className="card-topics" style={{ margin: '1rem 0' }}>
              {selectedArticle.topics.map(t => (
                <span key={t.id} className="topic-badge">
                  {t.name}
                </span>
              ))}
            </div>
            <div className="modal-body">
              <p className="lead-desc">{selectedArticle.description}</p>
              <hr />
              <div className="article-body-text">{selectedArticle.content}</div>
            </div>
          </div>
        </div>
      )}

      {/* Notifications Drawer */}
      {showNotifDrawer && (
        <div className="drawer-overlay" onClick={() => setShowNotifDrawer(false)}>
          <div className="drawer-content" onClick={e => e.stopPropagation()}>
            <div className="drawer-header">
              <h3>🔔 Notifications ({notifications.length})</h3>
              <button onClick={() => setShowNotifDrawer(false)}>✕</button>
            </div>
            <div className="notifications-list">
              {notifications.length === 0 ? (
                <p className="empty-hint">No notifications yet. Try publishing a breaking article matching your followed topics!</p>
              ) : (
                notifications.map(n => (
                  <div key={n.id} className="notification-card">
                    <p>{n.message}</p>
                    <small>{new Date(n.created_at).toLocaleTimeString()}</small>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
