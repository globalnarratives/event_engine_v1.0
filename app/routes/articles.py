from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models import Article
from app.forms import ArticleSearchForm
from app import db
from datetime import datetime
from flask_login import login_required

bp = Blueprint('articles', __name__, url_prefix='/articles')


@bp.route('/')
@bp.route('/dashboard')
@login_required
def dashboard():
    """Display article review dashboard"""
    page = request.args.get('page', 1, type=int)
    per_page = 50
    
    # Build query for unprocessed, non-junk articles
    query = Article.query.filter_by(is_processed=False, is_junk=False)
    
    # Apply filters if present
    search_form = ArticleSearchForm(request.args)
    
    if request.args.get('date_from'):
        query = query.filter(Article.published_date >= search_form.date_from.data)
    
    if request.args.get('date_to'):
        query = query.filter(Article.published_date <= search_form.date_to.data)
    
    if request.args.get('source'):
        query = query.filter(Article.source_name.ilike(f'%{search_form.source.data}%'))
    
    if request.args.get('search_text'):
        search = f'%{search_form.search_text.data}%'
        query = query.filter(
            db.or_(
                Article.headline.ilike(search),
                Article.summary.ilike(search)
            )
        )
    
    status = request.args.get('status', '')
    if status == 'processed':
        query = Article.query.filter_by(is_processed=True, is_junk=False)
    elif status == 'junk':
        query = Article.query.filter_by(is_junk=True)
    elif status == 'unprocessed':
        query = Article.query.filter_by(is_processed=False, is_junk=False)
    
    # Sort by published date (newest first)
    query = query.order_by(Article.published_date.desc())
    
    # Paginate
    articles = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template('articles/dashboard.html', 
                         articles=articles,
                         search_form=search_form)


@bp.route('/<int:article_id>')
@login_required
def view(article_id):
    """View article details"""
    article = Article.query.get_or_404(article_id)
    return render_template('articles/view.html', article=article)


@bp.route('/<int:article_id>/mark_processed', methods=['POST'])
@login_required
def mark_processed(article_id):
    """Mark article as processed"""
    article = Article.query.get_or_404(article_id)
    article.is_processed = True
    db.session.commit()
    flash('Article marked as processed', 'success')
    return redirect(url_for('articles.dashboard'))


@bp.route('/<int:article_id>/mark_junk', methods=['POST'])
@login_required
def mark_junk(article_id):
    """Mark article as junk/irrelevant"""
    article = Article.query.get_or_404(article_id)
    article.is_junk = True
    db.session.commit()
    flash('Article marked as junk', 'success')
    return redirect(url_for('articles.dashboard'))


@bp.route('/<int:article_id>/unmark', methods=['POST'])
@login_required
def unmark(article_id):
    """Reset article to unprocessed state"""
    article = Article.query.get_or_404(article_id)
    article.is_processed = False
    article.is_junk = False
    db.session.commit()
    flash('Article reset to unprocessed', 'success')
    return redirect(url_for('articles.dashboard'))


@bp.route('/stats')
@login_required
def stats():
    """Display article collection statistics"""
    total_articles = Article.query.count()
    unprocessed = Article.query.filter_by(is_processed=False, is_junk=False).count()
    processed = Article.query.filter_by(is_processed=True).count()
    junk = Article.query.filter_by(is_junk=True).count()
    
    # Recent collection stats (last 7 days)
    from datetime import timedelta
    week_ago = datetime.utcnow() - timedelta(days=7)
    recent = Article.query.filter(Article.collected_date >= week_ago).count()
    
    stats = {
        'total': total_articles,
        'unprocessed': unprocessed,
        'processed': processed,
        'junk': junk,
        'recent_week': recent,
        'junk_ratio': round((junk / total_articles * 100), 2) if total_articles > 0 else 0
    }
    
    return render_template('articles/stats.html', stats=stats)

@bp.route('/collect', methods=['POST'])
@login_required
def collect_now():
    """Manually trigger article collection"""
    try:
        from collectors.news_api_collector import NewsAPICollector
        from collectors.rss_collector import RSSCollector
        from flask import current_app
        
        total_collected = 0
        
        # Run News API collector
        news_collector = NewsAPICollector(current_app._get_current_object())
        news_count = news_collector.collect()
        total_collected += news_count
        
        # Run RSS collector
        rss_collector = RSSCollector(current_app._get_current_object())
        rss_count = rss_collector.collect()
        total_collected += rss_count
        
        flash(f'Collection complete! {total_collected} new articles added.', 'success')
    except Exception as e:
        flash(f'Collection failed: {str(e)}', 'error')
    
    return redirect(url_for('articles.dashboard'))