#!/usr/bin/env python3
"""
Media Integrity — Botnet & Inauthentic Behavior Detection
Detect coordinated inauthentic accounts, botnets, and troll farms.
"""

import json
import math
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from collections import defaultdict, Counter

try:
    import networkx as nx
    HAS_NX = True
except ImportError:
    HAS_NX = False

try:
    from sklearn.cluster import DBSCAN
    from sklearn.feature_extraction.text import TfidfVectorizer
    import numpy as np
    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False

@dataclass
class BotAnalysisResult:
    """Results from bot detection analysis."""
    account_id: str
    is_likely_bot: bool
    bot_score: float  # 0-1
    behavior_patterns: Dict[str, float]
    network_cluster_id: Optional[int]
    similar_accounts: List[str]
    red_flags: List[str]
    recommendations: List[str]

@dataclass
class NetworkAnalysisResult:
    """Results from coordinated network analysis."""
    total_accounts: int
    clusters: List[Dict]  # each cluster with members and score
    coordination_score: float  # 0-1
    suspicious_links: List[str]
    timeline_patterns: Dict[str, int]
    overall_assessment: str

class BotDetector:
    """Detect single-account bot behavior."""

    def __init__(self):
        self.vectorizer = None
        if HAS_SKLEARN:
            self.vectorizer = TfidfVectorizer(stop_words='english', max_features=100)

    def analyze_account(self, account_data: Dict) -> BotAnalysisResult:
        """
        Analyze a single account for bot-like behavior.
        account_data keys: id, username, join_date, followers, following, posts,
                          avg_posts_per_day, content_samples (List[str])
        """
        flags = []
        behavior = {}

        # 1. Account age vs activity (new account, high activity = suspicious)
        if 'join_date' in account_data and 'posts' in account_data:
            try:
                joined = datetime.fromisoformat(account_data['join_date'].replace('Z', '+00:00'))
                days_old = (datetime.now(timezone.utc) - joined).days
                posts = int(account_data.get('posts', 0))
                if days_old > 0:
                    posts_per_day = posts / days_old
                    behavior['posts_per_day'] = posts_per_day
                    if posts_per_day > 50:
                        flags.append(f"Very high posting rate: {posts_per_day:.1f} posts/day")
                    elif days_old < 30 and posts > 100:
                        flags.append("New account with many posts")
            except:
                pass

        # 2. Follower/Following ratio
        followers = int(account_data.get('followers', 0))
        following = int(account_data.get('following', 0))
        if following > 0:
            ratio = followers / following
            behavior['follower_following_ratio'] = ratio
            if ratio < 0.1:  # many following, few followers
                flags.append("Low follower/following ratio (<0.1)")

        # 3. Content repetition (samples)
        content_samples = account_data.get('content_samples', [])
        if len(content_samples) >= 3 and HAS_SKLEARN and self.vectorizer:
            try:
                tfidf_matrix = self.vectorizer.fit_transform(content_samples)
                # Compute pairwise cosine similarity
                from sklearn.metrics.pairwise import cosine_similarity
                sim_matrix = cosine_similarity(tfidf_matrix)
                # Average similarity to others
                np.fill_diagonal(sim_matrix, 0)
                avg_sim = sim_matrix.sum() / (len(content_samples) * (len(content_samples)-1))
                behavior['content_similarity'] = avg_sim
                if avg_sim > 0.7:
                    flags.append("Posts are very similar (possible copy-paste)")
            except:
                pass

        # 4. Profile completeness (missing avatar, bio)
        if not account_data.get('avatar_url'):
            flags.append("No profile avatar")
        if not account_data.get('bio') or len(account_data.get('bio', '')) < 10:
            flags.append("Profile bio missing or too short")

        # 5. Username patterns (many numbers, random strings)
        username = account_data.get('username', '')
        if re.match(r'^[a-z]+\d{5,}$', username) or re.match(r'^[a-z0-9]{8,}$', username.lower()):
            flags.append("Username appears randomly generated")

        # Compute bot score
        bot_score = min(len(flags) * 0.2, 1.0)
        if behavior.get('posts_per_day', 0) > 100:
            bot_score = max(bot_score, 0.8)
        if behavior.get('content_similarity', 0) > 0.8:
            bot_score = max(bot_score, 0.7)

        is_bot = bot_score > 0.5

        recommendations = self._generate_recommendations(is_bot, bot_score, flags)

        return BotAnalysisResult(
            account_id=account_data['id'],
            is_likely_bot=is_bot,
            bot_score=round(bot_score, 2),
            behavior_patterns=behavior,
            network_cluster_id=None,  # set later if in network
            similar_accounts=[],
            red_flags=flags,
            recommendations=recommendations
        )

    def _generate_recommendations(self, is_bot: bool, score: float, flags: List[str]) -> List[str]:
        recs = []
        if is_bot:
            recs.append("Account exhibits bot-like behavior — limit exposure")
            if score > 0.8:
                recs.append("Highly likely automated — consider blocking/muting")
            recs.append("Verify claims from this account with trusted sources")
        else:
            recs.append("Account appears human-operated but still verify content")
        return recs

class NetworkAnalyzer:
    """Detect coordinated behavior across multiple accounts."""

    def __init__(self):
        self.graph = nx.Graph() if HAS_NX else None

    def load_accounts(self, accounts: List[Dict]):
        """Load list of account dicts (each with id, posts, retweet_networks, etc.)."""
        for acc in accounts:
            acc_id = acc['id']
            self.graph.add_node(acc_id, **acc)
            # Add edges based on retweet/mention/mentions patterns
            # For simplicity, if accounts retweet same posts or mention each other
            # We'll assume 'connections' list provided
            connections = acc.get('connections', [])
            for target in connections:
                self.graph.add_edge(acc_id, target)

    def detect_clusters(self, min_size: int = 3) -> List[Dict]:
        """Find clusters of tightly connected accounts."""
        if not HAS_NX or self.graph is None:
            return []
        clusters = []
        for cid, nodes in enumerate(nx.connected_components(self.graph)):
            if len(nodes) >= min_size:
                cluster_accounts = list(nodes)
                # Compute density (edges / possible edges)
                subgraph = self.graph.subgraph(cluster_accounts)
                density = nx.density(subgraph)
                clusters.append({
                    'id': cid,
                    'members': cluster_accounts,
                    'size': len(cluster_accounts),
                    'density': round(density, 3),
                    'suspicious': density > 0.5  # dense cluster = likely coordinated
                })
        return clusters

    def analyze_coordination(self, posts: List[Dict]) -> NetworkAnalysisResult:
        """
        Analyze posts for coordinated timing/content.
        posts: [{'account_id': ..., 'timestamp': iso, 'content': ...}, ...]
        """
        total_accounts = len(set(p['account_id'] for p in posts))

        # 1. Timeline clustering: posts within <60s of each other from different accounts
        timeline_clusters = self._cluster_by_time(posts, window_seconds=60)
        coordination_score = min(len(timeline_clusters) / max(total_accounts, 1), 1.0)

        # 2. Content similarity clusters
        content_clusters = self._cluster_by_content(posts)

        # 3. Combine to find suspicious networks
        suspicious_links = []
        for cluster in timeline_clusters:
            if len(cluster['accounts']) >= 3:
                suspicious_links.append(f"Simultaneous posting: {cluster['accounts']} at {cluster['time']}")

        overall = "LIKELY COORDINATED INAUTHENTIC BEHAVIOR" if coordination_score > 0.5 else "NO OBVIOUS COORDINATION"

        return NetworkAnalysisResult(
            total_accounts=total_accounts,
            clusters=timeline_clusters[:10],  # top 10
            coordination_score=round(coordination_score, 2),
            suspicious_links=suspicious_links,
            timeline_patterns={'bursts': len(timeline_clusters)},
            overall_assessment=overall
        )

    def _cluster_by_time(self, posts: List[Dict], window_seconds: int) -> List[Dict]:
        """Group posts by close timestamps."""
        clusters = []
        posts_sorted = sorted(posts, key=lambda x: x['timestamp'])
        current_cluster = []
        current_time = None
        for post in posts_sorted:
            t = datetime.fromisoformat(post['timestamp'].replace('Z', '+00:00'))
            if current_time is None:
                current_cluster = [post]
                current_time = t
            else:
                delta = (t - current_time).total_seconds()
                if delta <= window_seconds:
                    current_cluster.append(post)
                else:
                    if len(current_cluster) >= 2:
                        account_ids = list(set(p['account_id'] for p in current_cluster))
                        if len(account_ids) >= 2:
                            clusters.append({
                                'accounts': account_ids,
                                'time': current_time.isoformat(),
                                'size': len(current_cluster)
                            })
                    current_cluster = [post]
                    current_time = t
        return clusters

    def _cluster_by_content(self, posts: List[Dict]) -> List[Dict]:
        """Group posts by similar text content."""
        if not HAS_SKLEARN:
            return []
        texts = [p['content'] for p in posts]
        vectorizer = TfidfVectorizer(stop_words='english')
        try:
            tfidf = vectorizer.fit_transform(texts)
            # Use cosine similarity + threshold to cluster
            from sklearn.metrics.pairwise import cosine_similarity
            sim = cosine_similarity(tfidf)
           Threshold = 0.8
            clusters = []
            visited = set()
            for i in range(len(posts)):
                if i in visited:
                    continue
                cluster = [i]
                for j in range(i+1, len(posts)):
                    if sim[i,j] > threshold:
                        cluster.append(j)
                        visited.add(j)
                if len(cluster) >= 3:
                    clusters.append({
                        'posts': [posts[idx]['account_id'] for idx in cluster],
                        'similarity': round(np.mean([sim[i, idx] for idx in cluster[1:]]), 2)
                    })
                visited.add(i)
            return clusters
        except:
            return []

# Convenience
def analyze_bot(account_data: Dict) -> Dict:
    detector = BotDetector()
    result = detector.analyze_account(account_data)
    return asdict(result)

def analyze_network(posts: List[Dict]) -> Dict:
    analyzer = NetworkAnalyzer()
    result = analyzer.analyze_coordination(posts)
    return asdict(result)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Bot & Network Analyzer")
    parser.add_argument("--account", help="Account JSON file")
    parser.add_argument("--network", help="Posts JSON file (list of posts)")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    if args.account:
        with open(args.account) as f:
            acc = json.load(f)
        result = analyze_bot(acc)
        print(json.dumps(result, indent=2) if args.json else f"Bot score: {result['bot_score']} — Flags: {result['red_flags']}")
    elif args.network:
        with open(args.network) as f:
            posts = json.load(f)
        result = analyze_network(posts)
        print(json.dumps(result, indent=2) if args.json else f"Coordination score: {result['coordination_score']} — {result['overall_assessment']}")
    else:
        print("Use --account or --network")
