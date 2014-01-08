// Generated by CoffeeScript 1.6.3
(function() {
  var FeedManager;

  FeedManager = (function() {
    function FeedManager() {
      var _this = this;
      this.current_feed = -1;
      this.filter_read = true;
      this.last_article = Infinity;
      this.last_article_visible = false;
      this.more_articles_to_load = true;
      this.busy = false;
      this.refresh_feed_list(function() {
        _this.get_current_feed();
        return _this.set_current_feed();
      });
      this.buttons = {};
      this.bind(true, true);
    }

    FeedManager.prototype.update_last_article = function(data) {
      var article, time, _i, _len;
      for (_i = 0, _len = data.length; _i < _len; _i++) {
        article = data[_i];
        time = new Date(article.article.date_published);
        time = time.getTime();
        if (time < this.last_article) {
          this.last_article = time;
        }
      }
      return this.last_article;
    };

    FeedManager.prototype.reset_last_article = function() {
      return this.last_article = Infinity;
    };

    FeedManager.prototype.update_title = function() {
      var el, feed, unread;
      feed = this.get_current_feed();
      el = $("#feed-" + feed);
      unread = el.children('small').text();
      return document.title = "" + unread + " " + (el.data('name'));
    };

    FeedManager.prototype.get_current_feed = function() {
      var hash;
      hash = Number(window.location.hash.slice(1));
      if (hash !== this.current_feed) {
        this.current_feed = hash;
        this.change_feed(this.current_feed);
      }
      return hash;
    };

    FeedManager.prototype.set_current_feed = function() {
      $(".feed-row.active").removeClass('active');
      $("#feed-" + this.current_feed).addClass('active');
      window.location.hash = this.current_feed;
      return this.update_title();
    };

    FeedManager.prototype.change_feed = function(feed, keep_active_article) {
      var ih, offset, scroll, tmp,
        _this = this;
      if (keep_active_article == null) {
        keep_active_article = false;
      }
      this.busy = true;
      offset = $("#feed-" + feed).offset().top - 25;
      ih = $('.feed-list>ul').innerHeight() - 25;
      scroll = $('.feed-list>ul').scrollTop();
      if (offset + 14 > ih) {
        $('.feed-list>ul').scrollTop(scroll + (offset - ih) + 14);
      } else if (offset < 0) {
        $('.feed-list>ul').scrollTop(scroll + offset);
      }
      if (keep_active_article) {
        tmp = $('li.article-row.active').clone();
      }
      return $.ajax({
        url: "" + window.AJAX_BASE + "feeds/feeds/" + feed + "/articles",
        data: !this.filter_read ? 'all' : void 0,
        dataType: 'json',
        success: function(data) {
          _this.reset_last_article();
          _this.update_last_article(data.articles);
          _this.current_feed = feed;
          _this.set_current_feed();
          $('.article-list>ul').html(Mark.up(window.templates['articles'], {
            'articles': data.articles
          }));
          if (keep_active_article) {
            $('div.article-list>ul').prepend(tmp);
          }
          _this.bind();
          $('.article-list').scrollTop(0);
          if (data.length === 50) {
            _this.more_articles_to_load = true;
          }
          _this.update_unread(data.unread, feed);
          return _this.busy = false;
        }
      });
    };

    FeedManager.prototype.load_more_articles = function() {
      var feed,
        _this = this;
      feed = this.current_feed;
      if (!this.more_articles_to_load) {
        return;
      }
      this.busy = true;
      return $.ajax({
        url: "" + window.AJAX_BASE + "feeds/feeds/" + feed + "/articles",
        data: {
          'limit': 15,
          'all': !this.filter_read,
          'last_article': this.last_article
        },
        dataType: 'json',
        success: function(data) {
          _this.update_last_article(data.articles);
          $('.article-list>ul').append(Mark.up(window.templates['articles'], {
            'articles': data.articles
          }));
          _this.bind();
          if (data.length < 15) {
            console.log('no more');
            _this.more_articles_to_load = false;
          }
          _this.update_unread(data.unread, feed);
          return _this.busy = false;
        }
      });
    };

    FeedManager.prototype.update_unread = function(data, feed) {
      var _i, _len;
      if (feed == null) {
        feed = null;
      }
      if (feed != null) {
        $("#feed-" + feed + ">small").text("(" + data + ")");
      } else {
        for (_i = 0, _len = data.length; _i < _len; _i++) {
          feed = data[_i];
          $("#feed-" + feed.feed + ">small").text("(" + feed.unread + ")");
        }
      }
      return this.update_title();
    };

    FeedManager.prototype.mark_read = function(article) {
      var _this = this;
      return $.ajax({
        url: "" + window.AJAX_BASE + "feeds/article/" + article + "/read",
        dataType: 'json',
        success: function(data) {
          $("#article-" + article).addClass('read');
          $("#article-" + article + ">div.article-content>div.article-content-footer>div>span:last").text('Mark unread');
          return _this.update_unread(data);
        }
      });
    };

    FeedManager.prototype.mark_unread = function(article) {
      var _this = this;
      return $.ajax({
        url: "" + window.AJAX_BASE + "feeds/article/" + article + "/unread",
        dataType: 'json',
        success: function(data) {
          $("#article-" + article).removeClass('read');
          $("#article-" + article + ">div.article-content>div.article-content-footer>div>span:last").text('Mark read');
          return _this.update_unread(data);
        }
      });
    };

    FeedManager.prototype.mark_all_read = function() {
      var feed,
        _this = this;
      feed = this.get_current_feed();
      return $.ajax({
        url: "" + window.AJAX_BASE + "feeds/feeds/" + feed + "/mark_read",
        dataType: 'json',
        success: function(data) {
          $('.article-row').addClass('read');
          if (feed === 0) {
            $('.feed-row>small').text('(0)');
          } else {
            $("#feed-" + feed + ">small").text('(0)');
          }
          $('li.article-row>div.article-content>div.article-content-footer>div>span:last').text('Mark unread');
          return _this.update_unread(data);
        }
      });
    };

    FeedManager.prototype.refresh_feed = function() {
      var feed,
        _this = this;
      feed = this.get_current_feed();
      $('#refresh-feed').addClass('disabled');
      return $.ajax({
        url: "" + window.AJAX_BASE + "feeds/feeds/" + feed + "/refresh",
        dataType: 'json',
        success: function(data) {
          _this.update_unread(data);
          _this.change_feed(feed, true);
          return $('#refresh-feed').removeClass('disabled');
        }
      });
    };

    FeedManager.prototype.refresh_feed_list = function(cb) {
      var _this = this;
      if (cb == null) {
        cb = null;
      }
      return $.ajax({
        url: "" + window.AJAX_BASE + "feeds/feeds/list/",
        dataType: 'json',
        success: function(data) {
          $('.feed-list>ul').html(Mark.up(window.templates.feed_list, data));
          _this.bind(true);
          if (cb != null) {
            return cb();
          }
        }
      });
    };

    FeedManager.prototype.toggle_filter_read = function() {
      this.filter_read = this.filter_read ^ 1;
      $('#filter-read').button('toggle');
      return this.change_feed(this.get_current_feed());
    };

    FeedManager.prototype.toggle_article = function(title, e) {
      var child, main_content, row,
        _this = this;
      if (e == null) {
        e = null;
      }
      row = title.parent();
      child = row.children('.article-content');
      main_content = child.children('.article-content-main');
      if (row.hasClass('active')) {
        child.css('display', 'none');
        row.removeClass('active');
      } else {
        $('li.article-row.active').each(function() {
          return $(this).removeClass('active').children('.article-content').css('display', 'none');
        });
        child.css('display', 'inline-block');
        row.addClass('active');
        if (!main_content.data('loaded')) {
          $.ajax({
            url: "" + window.AJAX_BASE + "feeds/article/" + (row.data('id')) + "/",
            dataType: 'json',
            success: function(data) {
              main_content.html(data.article__content);
              return main_content.data('loaded', true);
            }
          });
        }
        if (!row.hasClass('read')) {
          this.mark_read(row.data('id'));
        }
      }
      if (e != null) {
        e.stopPropagation();
        return e.preventDefault();
      }
    };

    FeedManager.prototype.next_article = function() {
      var current_article, next;
      current_article = $('.article-row.active');
      if (current_article.length === 0) {
        next = $('.article-row:first').children('.article-row-title');
      } else {
        next = current_article.next().children('.article-row-title');
      }
      if (next.length === 0) {
        return this.toggle_article(current_article.children('.article-row-title'));
      } else {
        return this.toggle_article(next);
      }
    };

    FeedManager.prototype.prev_article = function() {
      var current_article, prev;
      current_article = $('.article-row.active');
      if (current_article.length === 0) {
        return null;
      } else {
        prev = current_article.prev().children('.article-row-title');
      }
      if (prev.length === 0) {
        return this.toggle_article(current_article.children('.article-row-title'));
      } else {
        return this.toggle_article(prev);
      }
    };

    FeedManager.prototype.add_feed = function() {
      var _this = this;
      if (!$('#modal').length || $('#modal').data('for') !== 'add') {
        if ($('#modal').data('for') !== 'add') {
          $('#modal').remove();
        }
        $('body').append(Mark.up(window.templates.modal, {
          'for': 'add',
          'title': 'Add Feed',
          'modal_submit_text': 'Add Feed'
        }));
        $('#modal .modal-body').html(Mark.up(window.templates.add_feed_form));
        $('#modal_submit').click(function(e) {
          $('#modal_submit').addClass('disabled');
          return _this.add_feed_submit();
        });
      }
      return $('#modal').modal();
    };

    FeedManager.prototype.add_feed_submit = function() {
      var _this = this;
      return $.ajax({
        url: "" + window.AJAX_BASE + "feeds/feeds/add/",
        type: 'POST',
        dataType: 'json',
        data: $('#id_url').serialize(),
        headers: {
          'X-CSRFToken': window.CSRF_TOKEN
        },
        success: function(data) {
          if ('error' in data) {
            $('#modal .modal-body>.alert').text(data.error).removeClass('hidden');
            return $('#modal_submit').removeClass('disabled');
          } else {
            return _this.refresh_feed_list(function() {
              $('#modal').on('hidden.bs.modal', function(e) {
                return $('#modal').remove();
              });
              $('#modal').modal('hide');
              return _this.change_feed(data.pk);
            });
          }
        }
      });
    };

    FeedManager.prototype.edit_feed = function(feed) {
      var _this = this;
      if (!$('#modal').length || $('#modal').data('for') !== 'edit') {
        if ($('#modal').data('for') !== 'edit') {
          $('#modal').remove();
        }
        $('body').append(Mark.up(window.templates.modal, {
          'for': 'edit',
          'title': 'Edit Feed',
          'modal_submit_text': 'Edit Feed'
        }));
        $('#modal .modal-body').html("<div class='progress progress-striped active'><div class='progress-bar' role='progressbar' style='width: 100%'></div></div>");
      }
      $.ajax({
        url: "" + window.AJAX_BASE + "feeds/feeds/" + feed + "/info",
        dataType: 'json',
        success: function(data) {
          $('#modal .modal-body').html(Mark.up(window.templates.edit_feed_form, data));
          return $('#modal_submit').click(function(e) {
            $('#modal_submit').addClass('disabled');
            $('#modal .modal-body>.alert').addClass('hidden');
            $("#modal input").parents('.form-group').removeClass('has-error');
            return _this.edit_feed_submit(feed);
          });
        }
      });
      return $('#modal').modal();
    };

    FeedManager.prototype.edit_feed_submit = function(feed) {
      var _this = this;
      return $.ajax({
        url: "" + window.AJAX_BASE + "feeds/feeds/" + feed + "/edit",
        type: 'POST',
        dataType: 'json',
        data: $('#modal-form').serialize(),
        headers: {
          'X-CSRFToken': window.CSRF_TOKEN
        },
        success: function(data) {
          var error, field, name, _ref;
          if ('error' in data || 'form_errors' in data) {
            if ('error' in data) {
              $('#modal .modal-body>.alert').text(data.error).removeClass('hidden');
            }
            if ('form_errors' in data) {
              _ref = data.form_errors;
              for (name in _ref) {
                error = _ref[name];
                field = $("#modal input[name=" + name + "]");
                field.parents('.form-group').addClass('has-error');
              }
            }
            return $('#modal_submit').removeClass('disabled');
          } else {
            return _this.refresh_feed_list(function() {
              $('#modal').on('hidden.bs.modal', function(e) {
                return $('#modal').remove();
              });
              $('#modal').modal('hide');
              return _this.change_feed(data.pk);
            });
          }
        }
      });
    };

    FeedManager.prototype.bind = function(feeds, initial) {
      var _this;
      if (feeds == null) {
        feeds = false;
      }
      if (initial == null) {
        initial = false;
      }
      _this = this;
      $('li.article-row>div.article-row-title').off('click');
      $('li.article-row>div.article-row-title').click(function(e) {
        return _this.toggle_article($(this), e);
      });
      $('li.article-row>div.article-content>div.article-content-footer>div').off('click');
      $('li.article-row>div.article-content>div.article-content-footer>div').click(function(e) {
        var id, row;
        row = $(this).parents('li');
        id = row.data('id');
        if (row.hasClass('read')) {
          return _this.mark_unread(id);
        } else {
          return _this.mark_read(id);
        }
      });
      if (feeds) {
        $('li.feed-row').off('click');
        $('li.feed-row').click(function(e) {
          var id, row;
          row = $(this);
          id = row.data('id');
          return _this.change_feed(id);
        });
        $('li.feed-row>div.marker').click(function(e) {
          var id, row;
          e.stopPropagation();
          row = $(this).parent();
          id = row.data('id');
          return _this.edit_feed(id);
        });
      }
      if (initial) {
        this.buttons.mark_all_read = $('#mark-all-read');
        this.buttons.mark_all_read.click(function(e) {
          return _this.mark_all_read();
        });
        this.buttons.add_feed = $('#add-feed');
        this.buttons.add_feed.click(function(e) {
          return _this.add_feed();
        });
        this.buttons.refresh_feed = $('#refresh-feed');
        this.buttons.refresh_feed.click(function(e) {
          return _this.refresh_feed();
        });
        this.buttons.filter_read = $('#filter-read');
        this.buttons.filter_read.click(function(e) {
          return _this.toggle_filter_read();
        });
        $('body').keyup(function(e) {
          e.stopPropagation();
          e.preventDefault();
          if (e.which === 74) {
            return _this.next_article();
          } else if (e.which === 75) {
            return _this.prev_article();
          }
        });
        return $('.article-list').scroll(function() {
          if ($('.article-list').scrollTop() === 0 || _this.busy) {
            return;
          }
          if ($('.article-row:last').offset().top < $('.article-list').innerHeight()) {
            if (_this.last_article_visible === false) {
              _this.load_more_articles();
              return _this.last_article_visible = true;
            }
          } else {
            return _this.last_article_visible = false;
          }
        });
      }
    };

    return FeedManager;

  })();

  Mark.pipes.datetime = function(date) {
    return new Date(+date || date).toLocaleString();
  };

  Mark.pipes.sanitize = function(str) {
    var input, output;
    input = "[<>&\"'\/]";
    output = ["&lt;", "&gt;", "&amp;", "&quot;", "&#39;", "&#x2F;"];
    return str.replace(new RegExp(input, "g"), function(s) {
      return output[input.indexOf(s) - 1];
    });
  };

  window.templates = {
    'feed_list': "		<li class='feed-row' id='feed-0' data-id='0' data-name='All Items'>			Unread Items <small>({{total_unread_count}})</small>		</li>		{{feed_list}}		<li class='feed-row{{if not success}} error{{/if}}' id='feed-{{pk}}' data-id='{{pk}}' data-name='{{title|sanitize}}'{{if not success}} title='{{last_error|sanitize}}'{{/if}}>			<span>{{title|sanitize}}</span> <small>({{unread}})</small>			<div class='marker glyphicon glyphicon-wrench'></div>		</li>		{{/feed_list}}",
    'articles': "{{articles}}	<li class='article-row{{if read}} read{{/if}}' id='article-{{article.pk}}'	data-id='{{article.pk}}'>		<div class='article-row-title'>			<img class='feed-icon' src='{{feed.image}}'>			<div class='article-feed-name'>{{feed.title|sanitize}}</div>			<div class='article-title'>{{article.title|sanitize}}</div>			<div class='article-date' title='Published: {{article.date_published}} Discovered: {{article.date_added}}'>{{article.date_published_relative}}</div>		</div>		<div class='article-content panel panel-default'>			<div class='article-content-title panel-heading'>				<h2><a href='{{article.url|sanitize}}' target='_blank'>{{article.title|sanitize}}</a></h2>			</div>			<div class='article-content-main panel-body' data-loaded='false'>							</div>			<div class='article-content-footer panel-footer'>				<div><span class='glyphicon glyphicon-envelope'></span> <span>{{if read}}Mark unread{{else}}Mark read{{/if}}</span></div>			</div>		</div>	</li>	{{/articles}}",
    'modal': "		<div class='modal fade' id='modal' tabindex='-1' role='dialog' data-for='{{for}}'>			<div class='modal-dialog'>				<div class='modal-content'>					<div class='modal-header'>						<button type='button' class='close' data-dismiss='modal'>&times;</button>						<h4 class='modal-title' id='modal_label'>{{title|sanitize}}</h4>					</div>					<div class='modal-body'></div>					<div class='modal-footer'>						<button type='button' class='btn btn-primary' id='modal_submit'>{{modal_submit_text}}</button>					</div>				</div>			</div>		</div>",
    'add_feed_form': "		<div class='alert alert-danger hidden'></div>		<form class='form-horizontal' role='form'>			<div class='form-group'>				<label class='col-md-2 control-label' for='id_url'>Feed URL</label>				<div class='col-md-12'>					<input class='form-control' id='id_url' name='url' type='url'>				</div>			</div>		</form>",
    'edit_feed_form': "		<div class='alert alert-danger hidden'></div>		<form id='modal-form' class='form-horizontal' role='form'>			<div class='form-group'>				<label class='col-md-3 control-label' for='id_title'>Feed Title</label>				<div class='col-md-11'>					<input class='form-control' id='id_title' name='title' value='{{title|sanitize}}'>				</div>			</div>			<div class='form-group'>				<label class='col-md-3 control-label' for='id_feed_url'>Feed URL</label>				<div class='col-md-11'>					<input class='form-control' id='id_feed_url' name='feed_url' type='url' value='{{feed_url|sanitize}}'>				</div>			</div>			<div class='form-group'>				<label class='col-md-3 control-label' for='id_site_url'>Site URL</label>				<div class='col-md-11'>					<input class='form-control' id='id_site_url' name='site_url' type='url' value='{{site_url|sanitize}}'>				</div>			</div>		</form>		<div>		Last fetched:{{last_fetched|datetime}}<br>		Next fetch:{{next_fetch|datetime}}		</div>	"
  };

  $(document).ready(function() {
    return window.feeds = new FeedManager();
  });

}).call(this);
