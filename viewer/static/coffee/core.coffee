class FeedManager
	constructor:()->
		@current_feed=0
		@get_current_feed()
		@set_current_feed()
		@bind(true, true)
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
	change_feed:(feed)->
		$.ajax({
			url:"/feeds/feeds/#{feed}/articles"
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
				@update_unread(data)
				$('.article-row').addClass('read')
				if feed==0
					$('.feed-row>small').text('(0)')
				else
					$("#feed-#{feed.feed}>small").text('(0)')
		})
	refresh_feed:()->
		feed=@get_current_feed()
		$('#refresh-feed').button('loading')
		$.ajax({
			url:"/feeds/feeds/#{feed}/refresh"
			dataType:'json'
			success:(data)=>
				@update_unread(data)
				@change_feed(feed)
				$('#refresh-feed').button('reset')
		})
	bind:(feeds=false, initial=false)->
		_this=@
		$('li.article-row>div.article-row-title').off('click')
		$('li.article-row>div.article-row-title').click((e)->
			# console.log('click detected')
			title=$(@)
			row=title.parent()
			child=title.next('.article-content')
			if row.hasClass('active')
				child.css('display', 'none')
				row.removeClass('active')
			else
				$('li.article-row.active').each(->
					$(@).removeClass('active').children('.article-content').css('display', 'none')
				)
				child.css('display', 'inline-block')
				row.addClass('active')
				if not row.hasClass('read')
					_this.mark_read(row.data('id'))
			e.stopPropagation()
			e.preventDefault()
		)
		if feeds
			$('li.feed-row').off('click')
			$('li.feed-row').click((e)->
				row=$(@)
				id=row.data('id')
				_this.change_feed(id)
			)
		if initial
			$('#mark-all-as-read').click((e)->
				_this.mark_all_read()
			)
			$('#refresh-feed').click((e)->
				_this.refresh_feed()
			)

$(document).ready(->
	window.feeds=new FeedManager()
)