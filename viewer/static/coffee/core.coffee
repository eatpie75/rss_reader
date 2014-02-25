class FeedManager
	constructor:()->
		@current_feed=-1
		@filter_read=true

		@last_article=Infinity
		@last_article_visible=false
		@more_articles_to_load=true
		@busy=false

		@newest_article=new Date(0)
		@new_articles_available=false

		@refresh_feed_list(()=>
			@get_current_feed()
			@set_current_feed()
		)

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
	update_newest_article:(data)->
		for article in data
			time=new Date(article.article.date_added)
			if time>@newest_article
				@newest_article=time
		@newest_article
	reset_newest_article:()->
		@newest_article=new Date(0)
	update_title:()->
		feed=@get_current_feed()
		el=$("#feed-#{feed}")
		unread=el.children('small').text()
		mod=if @new_articles_available then '!' else ''
		document.title="#{unread}#{mod} #{el.data('name')}"
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
		offset=$("#feed-#{feed}").offset().top-25
		ih=$('.feed-list>ul').innerHeight()-25
		scroll=$('.feed-list>ul').scrollTop()
		if offset+14>ih
			$('.feed-list>ul').scrollTop(scroll+(offset-ih)+14)
		else if offset<0
			$('.feed-list>ul').scrollTop(scroll+offset)
		if keep_active_article
			tmp=$('li.article-row.active').clone()
		$.ajax({
			url:"#{window.AJAX_BASE}feeds/feeds/#{feed}/articles"
			data:'read' if not @filter_read
			dataType:'json'
			success:(data)=>
				@reset_last_article()
				@reset_newest_article()
				@update_last_article(data.articles)
				@update_newest_article(data.articles)
				@current_feed=feed
				@set_current_feed()
				$('.article-list>ul').html(Mark.up(window.templates['articles'], {'articles':data.articles}))
				if keep_active_article
					$('div.article-list>ul').prepend(tmp)
				@bind()
				$('.article-list').scrollTop(0)
				if data.length==50
					@more_articles_to_load=true
				@update_unread(data.unread, feed)
				@busy=false
		})
	load_more_articles:()->
		feed=@current_feed
		if not @more_articles_to_load
			return
		@busy=true
		$.ajax({
			url:"#{window.AJAX_BASE}feeds/feeds/#{feed}/articles"
			data:{'limit':15, 'read':!@filter_read, 'last_article':@last_article}
			dataType:'json'
			success:(data)=>
				@update_last_article(data.articles)
				$('.article-list>ul').append(Mark.up(window.templates['articles'], {'articles':data.articles}))
				@bind()
				if data.length<15
					# console.log 'no more'
					@more_articles_to_load=false
				@update_unread(data.unread, feed)
				@busy=false
		})
	update_unread:(data, feed=null)->
		if feed?
			$("#feed-#{feed}>small").text("(#{data})")
		else
			for feed in data
				$("#feed-#{feed.feed}>small").text("(#{feed.unread})")
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
	refresh_feed_list:(cb=null)->
		$.ajax({
			url:"#{window.AJAX_BASE}feeds/feeds/list/"
			dataType:'json'
			success:(data)=>
				$('.feed-list>ul').html(Mark.up(window.templates.feed_list, data))
				@bind(true)
				if cb?
					cb()
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
					success:(data)->
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
	add_feed:()->
		if not $('#modal').length or $('#modal').data('for')!='add'
			if $('#modal').data('for')!='add'
				$('#modal').remove()
			$('body').append(Mark.up(window.templates.modal, {'for':'add', 'title':'Add Feed', 'modal_submit_text':'Add Feed'}))
			$('#modal .modal-body').html(Mark.up(window.templates.add_feed_form))
			$('#modal_submit').click((e)=>
				$('#modal_submit').addClass('disabled')
				@add_feed_submit()
			)
		$('#modal').modal()
	add_feed_submit:()->
		$.ajax({
			url:"#{window.AJAX_BASE}feeds/feeds/add/"
			type:'POST'
			dataType:'json'
			data:$('#id_url').serialize()
			headers:{'X-CSRFToken':window.CSRF_TOKEN}
			success:(data)=>
				if 'error' of data
					$('#modal .modal-body>.alert').text(data.error).removeClass('hidden')
					$('#modal_submit').removeClass('disabled')
				else
					@refresh_feed_list(()=>
						$('#modal').on('hidden.bs.modal', (e)->
							$('#modal').remove()
						)
						$('#modal').modal('hide')
						@change_feed(data.pk)
					)
		})
	edit_feed:(feed)->
		if not $('#modal').length or $('#modal').data('for')!='edit'
			if $('#modal').data('for')!='edit'
				$('#modal').remove()
			$('body').append(Mark.up(window.templates.modal, {'for':'edit', 'title':'Edit Feed', 'modal_submit_text':'Edit Feed'}))
			$('#modal .modal-body').html("<div class='progress progress-striped active'><div class='progress-bar' role='progressbar' style='width: 100%'></div></div>")
		$.ajax({
			url:"#{window.AJAX_BASE}feeds/feeds/#{feed}/info"
			dataType:'json'
			success:(data)=>
				$('#modal .modal-body').html(Mark.up(window.templates.edit_feed_form, data))
				$('#modal_submit').click((e)=>
					$('#modal_submit').addClass('disabled')
					$('#modal .modal-body>.alert').addClass('hidden')
					$("#modal input").parents('.form-group').removeClass('has-error')
					@edit_feed_submit(feed)
				)

		})
		$('#modal').modal()
	edit_feed_submit:(feed)->
		$.ajax({
			url:"#{window.AJAX_BASE}feeds/feeds/#{feed}/edit"
			type:'POST'
			dataType:'json'
			data:$('#modal-form').serialize()
			headers:{'X-CSRFToken':window.CSRF_TOKEN}
			success:(data)=>
				if 'error' of data or 'form_errors' of data
					if 'error' of data
						$('#modal .modal-body>.alert').text(data.error).removeClass('hidden')
					if 'form_errors' of data
						for name, error of data.form_errors
							field=$("#modal input[name=#{name}]")
							field.parents('.form-group').addClass('has-error')
					$('#modal_submit').removeClass('disabled')
				else
					@refresh_feed_list(()=>
						$('#modal').on('hidden.bs.modal', (e)->
							$('#modal').remove()
						)
						$('#modal').modal('hide')
						@change_feed(data.pk)
					)
		})
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
			$('li.feed-row>div.marker').click((e)->
				e.stopPropagation()
				row=$(@).parent()
				id=row.data('id')
				_this.edit_feed(id)
			)
		if initial
			@buttons.mark_all_read=$('#mark-all-read')
			@buttons.mark_all_read.click((e)->
				_this.mark_all_read()
			)
			@buttons.add_feed=$('#add-feed')
			@buttons.add_feed.click((e)->
				_this.add_feed()
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
				e.stopPropagation()
				e.preventDefault()
				if e.which==74
					_this.next_article()
				else if e.which==75
					_this.prev_article()
			)
			# @change_feed(@get_current_feed())
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
			setTimeout(check_for_new_articles, 30000)

Mark.pipes.datetime=(date)->
	new Date(+date || date).toLocaleString()
Mark.pipes.sanitize=(str, escape_only=false)->
	input=if not escape_only then "[<>&\"'\/]" else "[<>]"
	output=["&lt;", "&gt;", "&amp;", "&quot;", "&#39;", "&#x2F;"]
	str.replace(new RegExp(input, "g"), (s)->
		output[input.indexOf(s)-1]
	)
Mark.pipes.escape=(str)->
	Mark.pipes.sanitize(str, true)

window.templates={
	'feed_list':"
		<li class='feed-row' id='feed-0' data-id='0' data-name='All Items'>
			Unread Items <small>({{total_unread_count}})</small>
		</li>
		{{feed_list}}
		<li class='feed-row{{if not success}} error{{/if}}' id='feed-{{pk}}' data-id='{{pk}}' data-name='{{title|sanitize}}'{{if not success}} title='{{last_error|sanitize}}'{{/if}}>
			<span>{{title|escape}}</span> <small>({{unread}})</small>
			<div class='marker glyphicon glyphicon-wrench'></div>
		</li>
		{{/feed_list}}",
	'articles':"{{articles}}
	<li class='article-row{{if read}} read{{/if}}' id='article-{{article.pk}}'
	data-id='{{article.pk}}'>
		<div class='article-row-title'>
			<img class='feed-icon' src='{{feed.image}}' title='{{feed.title|escape}}'>
			<div class='article-feed-name'>{{feed.title|escape}}</div>
			<div class='article-title'>{{article.title|escape}}</div>
			<div class='article-date' title='Published: {{article.date_published}} Discovered: {{article.date_added}}'>{{article.date_published_relative}}</div>
		</div>
		<div class='article-content panel panel-default'>
			<div class='article-content-title panel-heading'>
				<h2><a href='{{article.url|sanitize}}' target='_blank'>{{article.title|escape}}</a></h2>
			</div>
			<div class='article-content-main panel-body' data-loaded='false'>
				
			</div>
			<div class='article-content-footer panel-footer'>
				<div><span class='glyphicon glyphicon-envelope'></span> <span>{{if read}}Mark unread{{else}}Mark read{{/if}}</span></div>
			</div>
		</div>
	</li>
	{{/articles}}",
	'modal':"
		<div class='modal fade' id='modal' tabindex='-1' role='dialog' data-for='{{for}}'>
			<div class='modal-dialog'>
				<div class='modal-content'>
					<div class='modal-header'>
						<button type='button' class='close' data-dismiss='modal'>&times;</button>
						<h4 class='modal-title' id='modal_label'>{{title|escape}}</h4>
					</div>
					<div class='modal-body'></div>
					<div class='modal-footer'>
						<button type='button' class='btn btn-primary' id='modal_submit'>{{modal_submit_text}}</button>
					</div>
				</div>
			</div>
		</div>",
	'add_feed_form':"
		<div class='alert alert-danger hidden'></div>
		<form class='form-horizontal' role='form'>
			<div class='form-group'>
				<label class='col-md-2 control-label' for='id_url'>Feed URL</label>
				<div class='col-md-12'>
					<input class='form-control' id='id_url' name='url' type='url'>
				</div>
			</div>
		</form>",
	'edit_feed_form':"
		<div class='alert alert-danger hidden'></div>
		<form id='modal-form' class='form-horizontal' role='form'>
			<div class='form-group'>
				<label class='col-md-3 control-label' for='id_title'>Feed Title</label>
				<div class='col-md-11'>
					<input class='form-control' id='id_title' name='title' value='{{title|sanitize}}'>
				</div>
			</div>
			<div class='form-group'>
				<label class='col-md-3 control-label' for='id_feed_url'>Feed URL</label>
				<div class='col-md-11'>
					<input class='form-control' id='id_feed_url' name='feed_url' type='url' value='{{feed_url|sanitize}}'>
				</div>
			</div>
			<div class='form-group'>
				<label class='col-md-3 control-label' for='id_site_url'>Site URL</label>
				<div class='col-md-11'>
					<input class='form-control' id='id_site_url' name='site_url' type='url' value='{{site_url|sanitize}}'>
				</div>
			</div>
		</form>
		<div>
		Last fetched:{{last_fetched|datetime}}<br>
		Next fetch:{{next_fetch|datetime}}
		</div>
	"
}

check_for_new_articles=()->
	feed=window.feeds.get_current_feed()
	$.ajax({
		url:"#{window.AJAX_BASE}feeds/feeds/#{feed}/new"
		data:{'newest_article':window.feeds.newest_article.toISOString()}
		dataType:'json'
		success:(data)->
			if data.new_articles
				window.feeds.new_articles_available=true
				$("#feed-#{feed}").addClass('update')
			else
				window.feeds.new_articles_available=false
				$("#feed-#{feed}").removeClass('update')
			window.feeds.update_title()
			setTimeout(check_for_new_articles, 30000)
	})


$(document).ready(->
	window.feeds=new FeedManager()
)
