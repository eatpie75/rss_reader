class FeedManager
	constructor:()->
		@current_feed=0
		@filter_read=true
		@get_current_feed()
		@set_current_feed()

		@buttons={}
		@bind(true, true)
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
	change_feed:(feed)->
		$.ajax({
			url:"/feeds/feeds/#{feed}/articles"
			data:'all' if not @filter_read
			dataType:'html'
			success:(data)=>
				@current_feed=feed
				@set_current_feed()
				$('.article-list').html(data)
				@bind()
		})
	update_unread:(data)->
		for feed in data
			$("#feed-#{feed.feed}>small").text("(#{feed.count})")
		@update_title()
	mark_read:(article)->
		$.ajax({
			url:"/feeds/article/#{article}/read"
			dataType:'json'
			success:(data)=>
				$("#article-#{article}").addClass('read')
				@update_unread(data)
		})
	mark_unread:(article)->
		$.ajax({
			url:"/feeds/article/#{article}/unread"
			dataType:'json'
			success:(data)=>
				$("#article-#{article}").removeClass('read')
				@update_unread(data)
		})
	mark_all_read:()->
		feed=@get_current_feed()
		$.ajax({
			url:"/feeds/feeds/#{feed}/mark_read"
			dataType:'json'
			success:(data)=>
				$('.article-row').addClass('read')
				if feed==0
					$('.feed-row>small').text('(0)')
				else
					$("#feed-#{feed}>small").text('(0)')
				@update_unread(data)
		})
	refresh_feed:()->
		feed=@get_current_feed()
		$('#refresh-feed').addClass('disabled')
		$.ajax({
			url:"/feeds/feeds/#{feed}/refresh"
			dataType:'json'
			success:(data)=>
				@update_unread(data)
				@change_feed(feed)
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
					url:"/feeds/article/#{row.data('id')}/"
					dataType:'json'
					async:false
					success:(data)=>
						main_content.html(data.content)
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

$(document).ready(->
	window.feeds=new FeedManager()
)