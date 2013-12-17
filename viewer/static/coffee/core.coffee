class FeedManager
	constructor:()->
		@current_feed=0
		@filter_read=true
		@last_article=Infinity
		@last_article_visible=false
		@more_articles_to_load=true
		@busy=false
		@get_current_feed()
		@set_current_feed()

		@buttons={}
		@bind(true, true)
	update_last_article:(data)->
		for article in data
			time=new Date(article.article.date_published)
			time=time.getTime()
			if time<@last_article
				@last_article=time			
		@last_article
	reset_last_article:()->
		@last_article=Infinity
	update_title:()->
		feed=@get_current_feed()
		el=$("#feed-#{feed}")
		unread=el.children('small').text()
		document.title="#{unread} #{el.data('name')}"
	get_current_feed:()->
		hash=Number(window.location.hash.slice(1))
		if hash!=@current_feed
			@current_feed=hash
			@change_feed(@current_feed)
		hash
	set_current_feed:()->
		$(".feed-row.active").removeClass('active')
		$("#feed-#{@current_feed}").addClass('active')
		window.location.hash=@current_feed
		@update_title()
	change_feed:(feed, keep_active_article=false)->
		@busy=true
		if keep_active_article
			tmp=$('li.article-row.active').clone()
		$.ajax({
			url:"#{window.AJAX_BASE}feeds/feeds/#{feed}/test"
			data:'all' if not @filter_read
			dataType:'json'
			success:(data)=>
				@reset_last_article()
				@update_last_article(data)
				@current_feed=feed
				@set_current_feed()
				$('.article-list>ul').html(Mark.up(window.templates['articles'], {'articles':data}))
				if keep_active_article
					$('div.article-list>ul').prepend(tmp)
				@bind()
				$('.article-list').scrollTop(0)
				if data.length==50
					@more_articles_to_load=true
				@busy=false
		})
	load_more_articles:()->
		@busy=true
		feed=@current_feed
		if not @more_articles_to_load
			return
		$.ajax({
			url:"#{window.AJAX_BASE}feeds/feeds/#{feed}/test"
			data:{'limit':15, 'all':!@filter_read, 'last_article':@last_article}
			dataType:'json'
			success:(data)=>
				@update_last_article(data)
				$('.article-list>ul').append(Mark.up(window.templates['articles'], {'articles':data}))
				@bind()
				if data.length<15
					console.log 'no more'
					@more_articles_to_load=false
				@busy=false
		})
	update_unread:(data)->
		for feed in data
			$("#feed-#{feed.feed}>small").text("(#{feed.count})")
		@update_title()
	mark_read:(article)->
		$.ajax({
			url:"#{window.AJAX_BASE}feeds/article/#{article}/read"
			dataType:'json'
			success:(data)=>
				$("#article-#{article}").addClass('read')
				$("#article-#{article}>div.article-content>div.article-content-footer>div>span:last").text('Mark unread')
				@update_unread(data)
		})
	mark_unread:(article)->
		$.ajax({
			url:"#{window.AJAX_BASE}feeds/article/#{article}/unread"
			dataType:'json'
			success:(data)=>
				$("#article-#{article}").removeClass('read')
				$("#article-#{article}>div.article-content>div.article-content-footer>div>span:last").text('Mark read')
				@update_unread(data)
		})
	mark_all_read:()->
		feed=@get_current_feed()
		$.ajax({
			url:"#{window.AJAX_BASE}feeds/feeds/#{feed}/mark_read"
			dataType:'json'
			success:(data)=>
				$('.article-row').addClass('read')
				if feed==0
					$('.feed-row>small').text('(0)')
				else
					$("#feed-#{feed}>small").text('(0)')
				$('li.article-row>div.article-content>div.article-content-footer>div>span:last').text('Mark unread')
				@update_unread(data)
		})
	refresh_feed:()->
		feed=@get_current_feed()
		$('#refresh-feed').addClass('disabled')
		$.ajax({
			url:"#{window.AJAX_BASE}feeds/feeds/#{feed}/refresh"
			dataType:'json'
			success:(data)=>
				@update_unread(data)
				@change_feed(feed, true)
				$('#refresh-feed').removeClass('disabled')
		})
	toggle_filter_read:()->
		@filter_read=@filter_read^1
		$('#filter-read').button('toggle')
		@change_feed(@get_current_feed())
	toggle_article:(title, e=null)->
		row=title.parent()
		child=row.children('.article-content')
		main_content=child.children('.article-content-main')
		if row.hasClass('active')
			child.css('display', 'none')
			row.removeClass('active')
		else
			$('li.article-row.active').each(->
				$(@).removeClass('active').children('.article-content').css('display', 'none')
			)
			child.css('display', 'inline-block')
			row.addClass('active')
			if not main_content.data('loaded')
				$.ajax({
					url:"#{window.AJAX_BASE}feeds/article/#{row.data('id')}/"
					dataType:'json'
					# async:false
					success:(data)=>
						main_content.html(data.article__content)
						main_content.data('loaded', true)
				})
			if not row.hasClass('read')
				@mark_read(row.data('id'))
		if e?
			e.stopPropagation()
			e.preventDefault()
	next_article:()->
		current_article=$('.article-row.active')
		if current_article.length==0
			next=$('.article-row:first').children('.article-row-title')
		else
			next=current_article.next().children('.article-row-title')
		if next.length==0
			@toggle_article(current_article.children('.article-row-title'))
		else
			@toggle_article(next)
	prev_article:()->
		current_article=$('.article-row.active')
		if current_article.length==0
			return null
		else
			prev=current_article.prev().children('.article-row-title')
		if prev.length==0
			@toggle_article(current_article.children('.article-row-title'))
		else
			@toggle_article(prev)
	bind:(feeds=false, initial=false)->
		_this=@
		$('li.article-row>div.article-row-title').off('click')
		$('li.article-row>div.article-row-title').click((e)->
			# console.log('click detected')
			_this.toggle_article($(@), e)
		)
		$('li.article-row>div.article-content>div.article-content-footer>div').off('click')
		$('li.article-row>div.article-content>div.article-content-footer>div').click((e)->
			row=$(@).parents('li')
			id=row.data('id')
			if row.hasClass('read')
				_this.mark_unread(id)
			else
				_this.mark_read(id)
		)
		if feeds
			$('li.feed-row').off('click')
			$('li.feed-row').click((e)->
				row=$(@)
				id=row.data('id')
				_this.change_feed(id)
			)
		if initial
			@buttons.mark_all_read=$('#mark-all-read')
			@buttons.mark_all_read.click((e)->
				_this.mark_all_read()
			)
			@buttons.refresh_feed=$('#refresh-feed')
			@buttons.refresh_feed.click((e)->
				_this.refresh_feed()
			)
			@buttons.filter_read=$('#filter-read')
			@buttons.filter_read.click((e)->
				_this.toggle_filter_read()
			)
			$('body').keyup((e)->
				if e.which==74
					_this.next_article()
				else if e.which==75
					_this.prev_article()
			)
			@change_feed(@get_current_feed())
			$('.article-list').scroll(()->
				if $('.article-list').scrollTop()==0 or _this.busy
					return
				if $('.article-row:last').offset().top<$('.article-list').innerHeight()
					if _this.last_article_visible==false
						_this.load_more_articles()
						_this.last_article_visible=true
				else
					_this.last_article_visible=false
			)

window.templates={
	'articles':"{{articles}}
	<li class='article-row{{if read}} read{{/if}}' id='article-{{article.pk}}'
	data-id='{{article.pk}}'>
		<div class='article-row-title'>
			<img class='feed-icon' src='{{feed.image}}'>
			<div class='article-feed-name'>{{feed.title}}</div>
			<div class='article-title'>{{article.title}}</div>
			<div class='article-date' title='Published: {{article.date_published}} Discovered: {{article.date_added}}'>{{article.date_published_relative}}</div>
		</div>
		<div class='article-content panel panel-default'>
			<div class='article-content-title panel-heading'>
				<h2><a href='{{article.url}}' target='_blank'>{{article.title}}</a></h2>
			</div>
			<div class='article-content-main panel-body' data-loaded='false'>
				
			</div>
			<div class='article-content-footer panel-footer'>
				<div><span class='glyphicon glyphicon-envelope'></span> <span>{{if read}}Mark unread{{else}}Mark read{{/if}}</span></div>
			</div>
		</div>
	</li>
	{{/articles}}"
}

$(document).ready(->
	window.feeds=new FeedManager()
)
