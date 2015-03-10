class FeedManager
	constructor:()->
		@current_feed=-1
		@current_feed_is_category=null
		@filter_read=true

		@last_article=Infinity
		@last_article_visible=false
		@more_articles_to_load=true
		@busy=false

		@newest_article=new Date(0)
		@new_articles_available=false

		@categories=new CategoryList()
		@feeds=new FeedList()

		@refresh_categories(()=>
			@refresh_feed_list(()=>
				@get_current_feed()
				@set_current_feed()
			)
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
		if feed[0]=='c'
			el=$("#category-#{feed}")
		else
			el=$("#feed-#{feed}")
		unread=el.children('small').text()
		mod=if @new_articles_available then '!' else ''
		document.title="#{unread}#{mod} #{el.data('name')}"
	get_current_feed:()->
		hash=window.location.hash.slice(1)
		if hash=='' then hash='0'
		if hash!=@current_feed
			@current_feed=hash
			@current_feed_is_category=hash[0]=='c'
			@change_feed(@current_feed, @current_feed_is_category)
		hash
	set_current_feed:()->
		$(".feed-row.active").removeClass('active')
		$(".category-row.active").removeClass('active')
		if not @current_feed_is_category
			$("#feed-#{@current_feed}").addClass('active')
		else
			$("#category-#{@current_feed}").addClass('active')
		window.location.hash=@current_feed
		@update_title()
	change_feed:(feed, is_category=false)->
		@busy=true
		if not is_category
			offset=$("#feed-#{feed}").offset().top-25
		else
			offset=$("#category-#{feed}").offset().top-25
		ih=$('.feed-list>ul').innerHeight()-25
		scroll=$('.feed-list>ul').scrollTop()
		if offset+14>ih
			$('.feed-list>ul').scrollTop(scroll+(offset-ih)+14)
		else if offset<0
			$('.feed-list>ul').scrollTop(scroll+offset)
		if not is_category
			$.ajax({
				url:"#{window.AJAX_BASE}feeds/feeds/#{feed}/articles"
				data:'read' if not @filter_read
				dataType:'json'
				success:(data)=>
					@reset_last_article()
					@reset_newest_article()
					@update_last_article(data.articles)
					@update_newest_article(data.articles)
					@current_feed=String(feed)
					@current_feed_is_category=feed[0]=='c'
					@set_current_feed()
					$('.article-list>ul').html(Mark.up(window.templates['articles'], {'articles':data.articles}))
					@bind()
					$('.article-list').scrollTop(0)
					if data.length==50
						@more_articles_to_load=true
					@update_unread(data.unread, feed)
					@busy=false
			})
		else
			$.ajax({
				url:"#{window.AJAX_BASE}feeds/category/#{feed.slice(1)}/articles"
				data:'read' if not @filter_read
				dataType:'json'
				success:(data)=>
					@reset_last_article()
					@reset_newest_article()
					@update_last_article(data.articles)
					@update_newest_article(data.articles)
					@current_feed=feed
					@current_feed_is_category=feed[0]=='c'
					@set_current_feed(true)
					$('.article-list>ul').html(Mark.up(window.templates['articles'], {'articles':data.articles}))
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
		if @current_feed_is_category
			url="#{window.AJAX_BASE}feeds/category/#{feed}/articles"
		else
			url="#{window.AJAX_BASE}feeds/feeds/#{feed}/articles"
		$.ajax({
			url:url
			data:{'limit':15, 'read':!@filter_read, 'last_article':@last_article}
			dataType:'json'
			success:(data)=>
				@update_last_article(data.articles)
				$('.article-list>ul').append(Mark.up(window.templates['articles'], {'articles':data.articles}))
				@bind()
				if data.length<15
					@more_articles_to_load=false
				if @current_feed_is_category then @update_unread(data.unread, feed)
				@busy=false
		})
	update_unread:(data, feed=null)->
		if feed?
			$("#feed-#{feed}>small").text("(#{data})")
		else
			for feed in data
				$("#feed-#{feed.feed}>small").text("(#{feed.unread})")
		for category in $('.category-row')
			category=$(category)
			id=category.data('id')
			tmp=0
			feed=category.next()
			while true
				if feed.data('category')!=id
					break
				tmp+=Number(feed.find('small').text().slice(1, -1))
				feed=feed.next()
			category.find('small').text("(#{tmp})")
		@update_title()
	mark_read:(article)->
		$.ajax({
			url:"#{window.AJAX_BASE}feeds/article/#{article}/read"
			dataType:'json'
			success:(data)=>
				$("#article-#{article}").addClass('read')
				$("#article-#{article}>div.collapse>div.article-content>div.article-content-footer>div>span:last").text('Mark unread')
				@update_unread(data)
		})
	mark_unread:(article)->
		$.ajax({
			url:"#{window.AJAX_BASE}feeds/article/#{article}/unread"
			dataType:'json'
			success:(data)=>
				$("#article-#{article}").removeClass('read')
				$("#article-#{article}>div.collapse>div.article-content>div.article-content-footer>div>span:last").text('Mark read')
				@update_unread(data)
		})
	mark_all_read:()->
		feed=@get_current_feed()
		$.ajax({
			url:"#{window.AJAX_BASE}feeds/feeds/#{feed}/mark_read"
			data:{'newest_article':window.feeds.newest_article.toISOString()}
			dataType:'json'
			success:(data)=>
				$('.article-row').addClass('read')
				if feed==0
					$('.feed-row>small').text('(0)')
				else
					$("#feed-#{feed}>small").text('(0)')
				$('li.article-row>div.collapse>div.article-content>div.article-content-footer>div>span:last').text('Mark unread')
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
				@change_feed(feed)
				$('#refresh-feed').removeClass('disabled')
		})
	refresh_categories:(cb=null)->
		$.ajax({
			url:"#{window.AJAX_BASE}feeds/category/list/"
			dataType:'json'
			success:(data)=>
				@categories=new CategoryList()
				for category in data
					@categories.add(category)
				if cb?
					cb()
		})
	refresh_feed_list:(cb=null)->
		$.ajax({
			url:"#{window.AJAX_BASE}feeds/feeds/list/"
			dataType:'json'
			success:(data)=>
				@feeds=new FeedList()
				@feeds.total_unread_count=data.total_unread_count
				for feed in data.feed_list
					@feeds.add(new Feed(feed))
				@render_feed_list()
				@bind(true)
				if cb?
					cb()
		})
	render_feed_list:()->
		render=""
		render+=Mark.up(window.template_includes.all_feed_row, {'total_unread_count':@feeds.total_unread_count})
		used_categories=@feeds.get_used_categories()
		for category in used_categories
			category=@categories.get_by_pk(category)
			category.unread=@feeds.get_unread_for_category(category.pk)
			render+=Mark.up(window.template_includes.category_row, category)
			for feed in @feeds.get_by_category(category.pk)
				render+=Mark.up(window.template_includes.feed_row, feed)
		for feed in @feeds.get_all_without_category()
			render+=Mark.up(window.template_includes.feed_row, feed)
		$('.feed-list>ul').html(render)
		@bind(true)
		return
	toggle_category:(id)->
		row=$("#category-c#{id}")
		if row.hasClass('open')
			feed=row.next()
			while true
				if feed.data('category')!=id
					break
				feed.css('display', 'none')
				feed=feed.next()
			row.find('.folder').removeClass('glyphicon-folder-open').addClass('glyphicon-folder-close')
			row.find('.marker').removeClass('glyphicon-chevron-up').addClass('glyphicon-chevron-down')
			row.removeClass('open')
		else
			feed=row.next()
			while true
				if feed.data('category')!=id
					break
				feed.css('display', 'list-item')
				feed=feed.next()
			row.find('.folder').removeClass('glyphicon-folder-close').addClass('glyphicon-folder-open')
			row.find('.marker').removeClass('glyphicon-chevron-down').addClass('glyphicon-chevron-up')
			row.addClass('open')
	toggle_filter_read:()->
		@filter_read=@filter_read^1
		$('#filter-read').button('toggle')
		@change_feed(@get_current_feed())
	toggle_article:(title, e=null)->
		row=title.parent()
		collapse=row.children('div.collapse')
		child=collapse.children('div.article-content')
		main_content=child.children('.article-content-main')
		if row.hasClass('active')
			row.removeClass('active')
			collapse.collapse('hide')
		else
			$('li.article-row.active').each(->
				$(@).children('div.collapse').collapse('hide')
				$(@).removeClass('active')
			)
			row.addClass('active')
			if not main_content.data('loaded')
				$.ajax({
					url:"#{window.AJAX_BASE}feeds/article/#{row.data('id')}/"
					dataType:'json'
					success:(data)->
						main_content.html(data.article__content)
						main_content.data('loaded', true)
						collapse.collapse('show')
				})
			else
				collapse.collapse('show')
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
			$('#modal_submit').off('click')
			$('#modal_submit').on('click', (e)=>
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
			$('#modal .modal-body').html(window.templates.loading_bar)
		$.ajax({
			url:"#{window.AJAX_BASE}feeds/feeds/#{feed}/info"
			dataType:'json'
			success:(data)=>
				data['categories']=@categories.categories
				Mark.globals.tmp=data
				$('#modal .modal-body').html(Mark.up(window.templates.edit_feed_form, data))
				delete Mark.globals.tmp
				$('#modal_submit').off('click')
				$('#modal_submit').on('click', (e)=>
					e.stopImmediatePropagation()
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
							field=$("#modal input[name=#{name}], #modal select[name=#{name}]")
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
		$('li.article-row>div.article-row-title').on('click', (e)->
			_this.toggle_article($(@), e)
		)
		$('li.article-row>div.collapse>div.article-content>div.article-content-footer>div').off('click')
		$('li.article-row>div.collapse>div.article-content>div.article-content-footer>div').on('click', (e)->
			row=$(@).parents('li')
			id=row.data('id')
			if row.hasClass('read')
				_this.mark_unread(id)
			else
				_this.mark_read(id)
		)
		if feeds
			$('li.category-row').off('click')
			$('li.category-row>div.marker').off('click')
			$('li.feed-row').off('click')
			$('li.feed-row>div.marker').off('click')
			$('li.category-row').on('click', (e)->
				# e.stopPropagation()
				row=$(@)
				id=row.data('id')
				_this.change_feed("c#{id}", true)
			)
			$('li.category-row>div.marker').on('click', (e)->
				e.stopImmediatePropagation()
				row=$(@).parent()
				id=row.data('id')
				_this.toggle_category(id)
			)
			$('li.feed-row').on('click', (e)->
				# e.stopImmediatePropagation()
				row=$(@)
				id=row.data('id')
				_this.change_feed(id)
			)
			$('li.feed-row>div.marker').on('click', (e)->
				e.stopImmediatePropagation()
				row=$(@).parent()
				id=row.data('id')
				_this.edit_feed(id)
			)
		if initial
			@buttons.mark_all_read=$('#mark-all-read')
			@buttons.mark_all_read.on('click', (e)->
				_this.mark_all_read()
			)
			@buttons.add_feed=$('#add-feed')
			@buttons.add_feed.on('click', (e)->
				_this.add_feed()
			)
			@buttons.refresh_feed=$('#refresh-feed')
			@buttons.refresh_feed.on('click', (e)->
				_this.refresh_feed()
			)
			@buttons.filter_read=$('#filter-read')
			@buttons.filter_read.on('click', (e)->
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

class Feed
	constructor:(data)->
		@category=data.category
		@success=data.success
		@title=data.title
		@last_error=data.last_error
		@pk=data.pk
		@unread=data.unread

	has_category:()->
		if @category!=null then true else false

class FeedList
	constructor:()->
		@feeds=[]
		@total_unread_count=0
	add:(feed)->
		@feeds.push(feed)
	get_by_category:(category)->
		@feeds.filter((item)->item.category==category)
	get_all_with_category:()->
		@feeds.filter((item)->item.has_category())
	get_all_without_category:()->
		@feeds.filter((item)->!item.has_category())
	get_used_categories:()->
		list=[]
		for feed in @get_all_with_category()
			if feed.category not in list
				list.push(feed.category)
		list
	get_unread_for_category:(category)->
		unread=0
		for feed in @get_by_category(category)
			unread+=feed.unread
		unread

class Category
	constructor:(data)->
		@pk=data.pk
		@user=data.user
		@name=data.category
		@parent=data.parent

class CategoryList
	constructor:()->
		@categories=[]
	add:(category)->
		@categories.push(category)
	get_by_pk:(pk)->
		@categories.filter((item)->item.pk==pk)[0]

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

window.template_includes={
	'all_feed_row':"
		<li class='feed-row' id='feed-0' data-id='0' data-name='All Items'>
			Unread Items <small>({{total_unread_count}})</small>
		</li>"
	'feed_row':"
		<li class='feed-row{{if not success}} error{{/if}}{{if category}} indent{{/if}}' id='feed-{{pk}}' data-id='{{pk}}'
		 {{if category}}data-category='{{category}}'{{/if}} data-name='{{title|sanitize}}'{{if not success}} title='{{last_error|sanitize}}'{{/if}}>
			<span>{{title|escape}}</span> <small>({{unread}})</small>
			<div class='marker glyphicon glyphicon-wrench'></div>
		</li>",
	'category_row':"
		<li class='category-row open' id='category-c{{pk}}' data-id='{{pk}}' data-name='{{name|sanitize}}'>
			<div class='folder glyphicon glyphicon-folder-open'></div>
			<span>{{name|escape}}</span> <small>({{unread}})</small>
			<div class='marker glyphicon glyphicon-chevron-up'></div>
		</li>"
}

Mark.includes.all_feed_row=window.template_includes['all_feed_row']
Mark.includes.feed_row=window.template_includes['feed_row']
Mark.includes.category_row=window.template_includes['category_row']

window.templates={
	'loading_bar':"<div class='progress progress-striped active'><div class='progress-bar' role='progressbar' style='width: 100%'></div></div>",
	'feed_list':"
		{{all_feed_row}}
		{{feeds.feed_list}}
		{{feed_row}}
		{{/feeds.feed_list}}",
	'articles':"{{articles}}
	<li class='article-row{{if read}} read{{/if}}' id='article-{{article.pk}}' data-id='{{article.pk}}'>
		<div class='article-row-title'>
			<img class='feed-icon' src='{{feed.image}}' title='{{feed.title|sanitize}}' alt='Feed Icon'>
			<div class='article-feed-name'>{{feed.title|escape}}</div>
			<div class='article-title'>{{article.title|escape}}</div>
			<div class='article-date' title='Published: {{article.date_published}} Discovered: {{article.date_added}}'>{{article.date_published_relative}}</div>
		</div>
		<div class='collapse'>
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
			<div class='form-group'>
				<label class='col-md-3 control-label' for='id_category'>Category</label>
				<div class='col-md-11'>
					<select class='form-control' id='id_category' name='category'>
						<option value=''>---------</option>{{categories}}
						<option value='{{pk}}'{{if tmp.category|equals>`pk|number`}} selected{{/if}}>{{name}}</option>
					{{/categories}}</select>
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
	if not window.feeds.current_feed_is_category
		url="#{window.AJAX_BASE}feeds/feeds/#{feed}/new"
	else
		url="#{window.AJAX_BASE}feeds/category/#{feed.slice(1)}/new"
	$.ajax({
		url:url
		data:{'newest_article':window.feeds.newest_article.toISOString()}
		dataType:'json'
		success:(data)->
			if data.new_articles
				window.feeds.new_articles_available=true
				if not window.feeds.current_feed_is_category
					$("#feed-#{feed}").addClass('update')
				else
					$("#category-#{feed}").addClass('update')
			else
				window.feeds.new_articles_available=false
				if not window.feeds.current_feed_is_category
					$("#feed-#{feed}").removeClass('update')
				else
					$("#category-#{feed}").removeClass('update')
			window.feeds.update_title()
			setTimeout(check_for_new_articles, 60000)
	})


$(document).ready(->
	window.feeds=new FeedManager()
)
