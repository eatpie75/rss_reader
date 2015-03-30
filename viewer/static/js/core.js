// Generated by CoffeeScript 1.9.1
(function() {
  var Category, CategoryList, Feed, FeedList, FeedManager, check_for_new_articles,
    indexOf = [].indexOf || function(item) { for (var i = 0, l = this.length; i < l; i++) { if (i in this && this[i] === item) return i; } return -1; };

  FeedManager = (function() {
    function FeedManager() {
      this.current_feed = -1;
      this.current_feed_is_category = null;
      this.filter_read = true;
      this.last_article = Infinity;
      this.last_article_visible = false;
      this.more_articles_to_load = true;
      this.busy = false;
      this.newest_article = new Date(0);
      this.new_articles_available = false;
      this.categories = new CategoryList();
      this.feeds = new FeedList();
      this.cache = {};
      this.refresh_categories((function(_this) {
        return function() {
          return _this.refresh_feed_list(function() {
            _this.get_current_feed();
            return _this.set_current_feed();
          });
        };
      })(this));
      this.buttons = {};
      this.bind(true, true);
    }

    FeedManager.prototype.update_last_article = function(data) {
      var article, i, len, time;
      for (i = 0, len = data.length; i < len; i++) {
        article = data[i];
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

    FeedManager.prototype.update_newest_article = function(data) {
      var article, i, len, time;
      for (i = 0, len = data.length; i < len; i++) {
        article = data[i];
        time = new Date(article.article.date_added);
        if (time > this.newest_article) {
          this.newest_article = time;
        }
      }
      return this.newest_article;
    };

    FeedManager.prototype.reset_newest_article = function() {
      return this.newest_article = new Date(0);
    };

    FeedManager.prototype.update_title = function() {
      var el, feed, mod, unread;
      feed = this.get_current_feed();
      if (feed[0] === 'c') {
        el = $("#category-" + feed);
      } else {
        el = $("#feed-" + feed);
      }
      unread = el.children('small').text();
      mod = this.new_articles_available ? '!' : '';
      return document.title = "" + unread + mod + " " + (el.data('name'));
    };

    FeedManager.prototype.clear_cache = function() {
      return this.cache = {};
    };

    FeedManager.prototype.get_current_feed = function() {
      var hash;
      hash = window.location.hash.slice(1);
      if (hash === '') {
        hash = '0';
      }
      if (hash !== this.current_feed) {
        this.current_feed = hash;
        this.current_feed_is_category = hash[0] === 'c';
        this.change_feed(this.current_feed, this.current_feed_is_category);
      }
      return hash;
    };

    FeedManager.prototype.set_current_feed = function() {
      $(".feed-row.active").removeClass('active');
      $(".category-row.active").removeClass('active');
      if (!this.current_feed_is_category) {
        $("#feed-" + this.current_feed).addClass('active');
      } else {
        $("#category-" + this.current_feed).addClass('active');
      }
      window.location.hash = this.current_feed;
      return this.update_title();
    };

    FeedManager.prototype.change_feed = function(feed, is_category) {
      var ih, offset, scroll;
      if (is_category == null) {
        is_category = false;
      }
      this.busy = true;
      if (!is_category) {
        offset = $("#feed-" + feed).offset().top - 25;
      } else {
        offset = $("#category-" + feed).offset().top - 25;
      }
      ih = $('.feed-list>ul').innerHeight() - 25;
      scroll = $('.feed-list>ul').scrollTop();
      if (offset + 14 > ih) {
        $('.feed-list>ul').scrollTop(scroll + (offset - ih) + 14);
      } else if (offset < 0) {
        $('.feed-list>ul').scrollTop(scroll + offset);
      }
      if (!is_category) {
        return $.ajax({
          url: window.AJAX_BASE + "feeds/feeds/" + feed + "/articles",
          data: !this.filter_read ? 'read' : void 0,
          dataType: 'json',
          success: (function(_this) {
            return function(data) {
              _this.reset_last_article();
              _this.reset_newest_article();
              _this.update_last_article(data.articles);
              _this.update_newest_article(data.articles);
              _this.current_feed = String(feed);
              _this.current_feed_is_category = feed[0] === 'c';
              _this.set_current_feed();
              $('.article-list>ul').html(Mark.up(window.templates['articles'], {
                'articles': data.articles
              }));
              _this.bind();
              $('.article-list').scrollTop(0);
              if (data.length === 50) {
                _this.more_articles_to_load = true;
              }
              _this.update_unread(data.unread, feed);
              return _this.busy = false;
            };
          })(this)
        });
      } else {
        return $.ajax({
          url: window.AJAX_BASE + "feeds/category/" + (feed.slice(1)) + "/articles",
          data: !this.filter_read ? 'read' : void 0,
          dataType: 'json',
          success: (function(_this) {
            return function(data) {
              _this.reset_last_article();
              _this.reset_newest_article();
              _this.update_last_article(data.articles);
              _this.update_newest_article(data.articles);
              _this.current_feed = feed;
              _this.current_feed_is_category = feed[0] === 'c';
              _this.set_current_feed(true);
              $('.article-list>ul').html(Mark.up(window.templates['articles'], {
                'articles': data.articles
              }));
              _this.bind();
              $('.article-list').scrollTop(0);
              if (data.length === 50) {
                _this.more_articles_to_load = true;
              }
              _this.update_unread(data.unread, feed);
              return _this.busy = false;
            };
          })(this)
        });
      }
    };

    FeedManager.prototype.load_more_articles = function() {
      var feed, url;
      feed = this.current_feed;
      if (!this.more_articles_to_load) {
        return;
      }
      this.busy = true;
      if (this.current_feed_is_category) {
        url = window.AJAX_BASE + "feeds/category/" + feed + "/articles";
      } else {
        url = window.AJAX_BASE + "feeds/feeds/" + feed + "/articles";
      }
      return $.ajax({
        url: url,
        data: {
          'limit': 15,
          'read': !this.filter_read,
          'last_article': this.last_article
        },
        dataType: 'json',
        success: (function(_this) {
          return function(data) {
            _this.update_last_article(data.articles);
            $('.article-list>ul').append(Mark.up(window.templates['articles'], {
              'articles': data.articles
            }));
            _this.bind();
            if (data.length < 15) {
              _this.more_articles_to_load = false;
            }
            if (_this.current_feed_is_category) {
              _this.update_unread(data.unread, feed);
            }
            return _this.busy = false;
          };
        })(this)
      });
    };

    FeedManager.prototype.update_unread = function(data, feed) {
      var category, i, id, j, len, len1, ref, tmp;
      if (feed == null) {
        feed = null;
      }
      if (feed != null) {
        $("#feed-" + feed + ">small").text("(" + data + ")");
      } else {
        for (i = 0, len = data.length; i < len; i++) {
          feed = data[i];
          $("#feed-" + feed.feed + ">small").text("(" + feed.unread + ")");
        }
      }
      ref = $('.category-row');
      for (j = 0, len1 = ref.length; j < len1; j++) {
        category = ref[j];
        category = $(category);
        id = category.data('id');
        tmp = 0;
        feed = category.next();
        while (true) {
          if (feed.data('category') !== id) {
            break;
          }
          tmp += Number(feed.find('small').text().slice(1, -1));
          feed = feed.next();
        }
        category.find('small').text("(" + tmp + ")");
      }
      return this.update_title();
    };

    FeedManager.prototype.mark_read = function(article) {
      return $.ajax({
        url: window.AJAX_BASE + "feeds/article/" + article + "/read",
        dataType: 'json',
        success: (function(_this) {
          return function(data) {
            $("#article-" + article).addClass('read');
            $("#article-" + article + ">div.article-content>div.article-content-footer>div>span:last").text('Mark unread');
            return _this.update_unread(data);
          };
        })(this)
      });
    };

    FeedManager.prototype.mark_unread = function(article) {
      return $.ajax({
        url: window.AJAX_BASE + "feeds/article/" + article + "/unread",
        dataType: 'json',
        success: (function(_this) {
          return function(data) {
            $("#article-" + article).removeClass('read');
            $("#article-" + article + ">div.article-content>div.article-content-footer>div>span:last").text('Mark read');
            return _this.update_unread(data);
          };
        })(this)
      });
    };

    FeedManager.prototype.mark_all_read = function() {
      var feed;
      feed = this.get_current_feed();
      return $.ajax({
        url: window.AJAX_BASE + "feeds/feeds/" + feed + "/mark_read",
        data: {
          'newest_article': window.feeds.newest_article.toISOString()
        },
        dataType: 'json',
        success: (function(_this) {
          return function(data) {
            $('.article-row').addClass('read');
            if (feed === 0) {
              $('.feed-row>small').text('(0)');
            } else {
              $("#feed-" + feed + ">small").text('(0)');
            }
            $('li.article-row>div.article-content>div.article-content-footer>div>span:last').text('Mark unread');
            return _this.update_unread(data);
          };
        })(this)
      });
    };

    FeedManager.prototype.refresh_feed = function() {
      var feed;
      feed = this.get_current_feed();
      $('#refresh-feed').addClass('disabled');
      return $.ajax({
        url: window.AJAX_BASE + "feeds/feeds/" + feed + "/refresh",
        dataType: 'json',
        success: (function(_this) {
          return function(data) {
            _this.update_unread(data);
            _this.change_feed(feed);
            return $('#refresh-feed').removeClass('disabled');
          };
        })(this)
      });
    };

    FeedManager.prototype.refresh_categories = function(cb) {
      if (cb == null) {
        cb = null;
      }
      return $.ajax({
        url: window.AJAX_BASE + "feeds/category/list/",
        dataType: 'json',
        success: (function(_this) {
          return function(data) {
            var category, i, len;
            _this.categories = new CategoryList();
            for (i = 0, len = data.length; i < len; i++) {
              category = data[i];
              _this.categories.add(category);
            }
            if (cb != null) {
              return cb();
            }
          };
        })(this)
      });
    };

    FeedManager.prototype.refresh_feed_list = function(cb) {
      if (cb == null) {
        cb = null;
      }
      return $.ajax({
        url: window.AJAX_BASE + "feeds/feeds/list/",
        dataType: 'json',
        success: (function(_this) {
          return function(data) {
            var feed, i, len, ref;
            _this.feeds = new FeedList();
            _this.feeds.total_unread_count = data.total_unread_count;
            ref = data.feed_list;
            for (i = 0, len = ref.length; i < len; i++) {
              feed = ref[i];
              _this.feeds.add(new Feed(feed));
            }
            _this.render_feed_list();
            _this.bind(true);
            if (cb != null) {
              return cb();
            }
          };
        })(this)
      });
    };

    FeedManager.prototype.render_feed_list = function() {
      var category, feed, i, j, k, len, len1, len2, ref, ref1, render, used_categories;
      render = "";
      render += Mark.up(window.template_includes.all_feed_row, {
        'total_unread_count': this.feeds.total_unread_count
      });
      used_categories = this.feeds.get_used_categories();
      for (i = 0, len = used_categories.length; i < len; i++) {
        category = used_categories[i];
        category = this.categories.get_by_pk(category);
        category.unread = this.feeds.get_unread_for_category(category.pk);
        render += Mark.up(window.template_includes.category_row, category);
        ref = this.feeds.get_by_category(category.pk);
        for (j = 0, len1 = ref.length; j < len1; j++) {
          feed = ref[j];
          render += Mark.up(window.template_includes.feed_row, feed);
        }
      }
      ref1 = this.feeds.get_all_without_category();
      for (k = 0, len2 = ref1.length; k < len2; k++) {
        feed = ref1[k];
        render += Mark.up(window.template_includes.feed_row, feed);
      }
      $('.feed-list>ul').html(render);
      this.bind(true);
    };

    FeedManager.prototype.toggle_category = function(id) {
      var feed, row;
      row = $("#category-c" + id);
      if (row.hasClass('open')) {
        feed = row.next();
        while (true) {
          if (feed.data('category') !== id) {
            break;
          }
          feed.css('display', 'none');
          feed = feed.next();
        }
        row.find('.folder').removeClass('glyphicon-folder-open').addClass('glyphicon-folder-close');
        row.find('.marker').removeClass('glyphicon-chevron-up').addClass('glyphicon-chevron-down');
        return row.removeClass('open');
      } else {
        feed = row.next();
        while (true) {
          if (feed.data('category') !== id) {
            break;
          }
          feed.css('display', 'list-item');
          feed = feed.next();
        }
        row.find('.folder').removeClass('glyphicon-folder-close').addClass('glyphicon-folder-open');
        row.find('.marker').removeClass('glyphicon-chevron-down').addClass('glyphicon-chevron-up');
        return row.addClass('open');
      }
    };

    FeedManager.prototype.toggle_filter_read = function() {
      this.filter_read = this.filter_read ^ 1;
      $('#filter-read').button('toggle');
      return this.change_feed(this.get_current_feed());
    };

    FeedManager.prototype.show_row = function(row) {
      row.children('div.article-content').css('display', 'inline-block');
      return row.addClass('active');
    };

    FeedManager.prototype.hide_row = function(row) {
      row.removeClass('active');
      return row.children('div.article-content').css('display', 'none').children('article-content-main').html('');
    };

    FeedManager.prototype.toggle_article = function(title, e) {
      var _this, child, main_content, row;
      if (e == null) {
        e = null;
      }
      _this = this;
      row = title.parent();
      child = row.children('div.article-content');
      main_content = child.children('.article-content-main');
      if (row.hasClass('active')) {
        this.hide_row(row);
      } else {
        $('li.article-row.active').each(function() {
          return _this.hide_row($(this));
        });
        if (main_content.data('loaded')) {
          if (row.data('id') in this.cache) {
            main_content.html(this.cache[row.data('id')]);
            this.show_row(row);
          } else {
            main_content.data('loaded', false);
            this.toggle_article(title);
          }
        } else {
          this.show_row(row);
          main_content.html(window.templates.loading_bar);
          $.ajax({
            url: window.AJAX_BASE + "feeds/article/" + (row.data('id')) + "/",
            dataType: 'json',
            success: (function(_this) {
              return function(data) {
                _this.cache[row.data('id')] = data.article__content;
                main_content.html(data.article__content);
                return main_content.data('loaded', true);
              };
            })(this)
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
        $('#modal_submit').off('click');
        $('#modal_submit').on('click', (function(_this) {
          return function(e) {
            $('#modal_submit').addClass('disabled');
            return _this.add_feed_submit();
          };
        })(this));
      }
      return $('#modal').modal();
    };

    FeedManager.prototype.add_feed_submit = function() {
      return $.ajax({
        url: window.AJAX_BASE + "feeds/feeds/add/",
        type: 'POST',
        dataType: 'json',
        data: $('#id_url').serialize(),
        headers: {
          'X-CSRFToken': window.CSRF_TOKEN
        },
        success: (function(_this) {
          return function(data) {
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
          };
        })(this)
      });
    };

    FeedManager.prototype.edit_feed = function(feed) {
      if (!$('#modal').length || $('#modal').data('for') !== 'edit') {
        if ($('#modal').data('for') !== 'edit') {
          $('#modal').remove();
        }
        $('body').append(Mark.up(window.templates.modal, {
          'for': 'edit',
          'title': 'Edit Feed',
          'modal_submit_text': 'Edit Feed'
        }));
        $('#modal .modal-body').html(window.templates.loading_bar);
      }
      $.ajax({
        url: window.AJAX_BASE + "feeds/feeds/" + feed + "/info",
        dataType: 'json',
        success: (function(_this) {
          return function(data) {
            data['categories'] = _this.categories.categories;
            Mark.globals.tmp = data;
            $('#modal .modal-body').html(Mark.up(window.templates.edit_feed_form, data));
            delete Mark.globals.tmp;
            $('#modal_submit').off('click').on('click', function(e) {
              e.stopImmediatePropagation();
              $('#modal_submit').addClass('disabled');
              $('#modal .modal-body>.alert').addClass('hidden');
              $("#modal input").parents('.form-group').removeClass('has-error');
              return _this.edit_feed_submit(feed);
            });
            return $('#modal_delete').off('click').one('click', function(e) {
              e.stopImmediatePropagation();
              return $('#modal_delete').one($.support.transition.end, function(e) {
                return $('#modal_delete').one($.support.transition.end, function(e) {
                  return $('#modal_delete').one('click', function(e) {
                    $('#modal_delete').addClass('disabled');
                    return _this.delete_feed(feed);
                  });
                }).text('Are you sure?').width(70);
              }).width(70).width(140);
            });
          };
        })(this)
      });
      return $('#modal').modal();
    };

    FeedManager.prototype.edit_feed_submit = function(feed) {
      return $.ajax({
        url: window.AJAX_BASE + "feeds/feeds/" + feed + "/edit",
        type: 'POST',
        dataType: 'json',
        data: $('#modal-form').serialize(),
        headers: {
          'X-CSRFToken': window.CSRF_TOKEN
        },
        success: (function(_this) {
          return function(data) {
            var error, field, name, ref;
            if ('error' in data || 'form_errors' in data) {
              if ('error' in data) {
                $('#modal .modal-body>.alert').text(data.error).removeClass('hidden');
              }
              if ('form_errors' in data) {
                ref = data.form_errors;
                for (name in ref) {
                  error = ref[name];
                  field = $("#modal input[name=" + name + "], #modal select[name=" + name + "]");
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
          };
        })(this)
      });
    };

    FeedManager.prototype.delete_feed = function(feed) {
      return $.ajax({
        url: window.AJAX_BASE + "feeds/feeds/" + feed + "/delete",
        type: 'POST',
        dataType: 'json',
        headers: {
          'X-CSRFToken': window.CSRF_TOKEN
        },
        success: (function(_this) {
          return function(data) {
            return _this.refresh_feed_list(function() {
              $('#modal').on('hidden.bs.modal', function(e) {
                return $('#modal').remove();
              });
              $('#modal').modal('hide');
              return _this.change_feed(0);
            });
          };
        })(this)
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
      $('li.article-row>div.article-row-title').on('click', function(e) {
        return _this.toggle_article($(this), e);
      });
      $('li.article-row>div.article-content>div.article-content-footer>div').off('click');
      $('li.article-row>div.article-content>div.article-content-footer>div').on('click', function(e) {
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
        $('li.category-row').off('click');
        $('li.category-row>div.marker').off('click');
        $('li.feed-row').off('click');
        $('li.feed-row>div.marker').off('click');
        $('li.category-row').on('click', function(e) {
          var id, row;
          row = $(this);
          id = row.data('id');
          return _this.change_feed("c" + id, true);
        });
        $('li.category-row>div.marker').on('click', function(e) {
          var id, row;
          e.stopImmediatePropagation();
          row = $(this).parent();
          id = row.data('id');
          return _this.toggle_category(id);
        });
        $('li.feed-row').on('click', function(e) {
          var id, row;
          row = $(this);
          id = row.data('id');
          return _this.change_feed(id);
        });
        $('li.feed-row>div.marker').on('click', function(e) {
          var id, row;
          e.stopImmediatePropagation();
          row = $(this).parent();
          id = row.data('id');
          return _this.edit_feed(id);
        });
      }
      if (initial) {
        this.buttons.mark_all_read = $('#mark-all-read');
        this.buttons.mark_all_read.on('click', function(e) {
          return _this.mark_all_read();
        });
        this.buttons.add_feed = $('#add-feed');
        this.buttons.add_feed.on('click', function(e) {
          return _this.add_feed();
        });
        this.buttons.refresh_feed = $('#refresh-feed');
        this.buttons.refresh_feed.on('click', function(e) {
          return _this.refresh_feed();
        });
        this.buttons.filter_read = $('#filter-read');
        this.buttons.filter_read.on('click', function(e) {
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
        $('.article-list').scroll(function() {
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
        return setTimeout(check_for_new_articles, 30000);
      }
    };

    return FeedManager;

  })();

  Feed = (function() {
    function Feed(data) {
      this.category = data.category;
      this.success = data.success;
      this.title = data.title;
      this.last_error = data.last_error;
      this.pk = data.pk;
      this.unread = data.unread;
    }

    Feed.prototype.has_category = function() {
      if (this.category !== null) {
        return true;
      } else {
        return false;
      }
    };

    return Feed;

  })();

  FeedList = (function() {
    function FeedList() {
      this.feeds = [];
      this.total_unread_count = 0;
    }

    FeedList.prototype.add = function(feed) {
      return this.feeds.push(feed);
    };

    FeedList.prototype.get_by_category = function(category) {
      return this.feeds.filter(function(item) {
        return item.category === category;
      });
    };

    FeedList.prototype.get_all_with_category = function() {
      return this.feeds.filter(function(item) {
        return item.has_category();
      });
    };

    FeedList.prototype.get_all_without_category = function() {
      return this.feeds.filter(function(item) {
        return !item.has_category();
      });
    };

    FeedList.prototype.get_used_categories = function() {
      var feed, i, len, list, ref, ref1;
      list = [];
      ref = this.get_all_with_category();
      for (i = 0, len = ref.length; i < len; i++) {
        feed = ref[i];
        if (ref1 = feed.category, indexOf.call(list, ref1) < 0) {
          list.push(feed.category);
        }
      }
      return list;
    };

    FeedList.prototype.get_unread_for_category = function(category) {
      var feed, i, len, ref, unread;
      unread = 0;
      ref = this.get_by_category(category);
      for (i = 0, len = ref.length; i < len; i++) {
        feed = ref[i];
        unread += feed.unread;
      }
      return unread;
    };

    return FeedList;

  })();

  Category = (function() {
    function Category(data) {
      this.pk = data.pk;
      this.user = data.user;
      this.name = data.category;
      this.parent = data.parent;
    }

    return Category;

  })();

  CategoryList = (function() {
    function CategoryList() {
      this.categories = [];
    }

    CategoryList.prototype.add = function(category) {
      return this.categories.push(category);
    };

    CategoryList.prototype.get_by_pk = function(pk) {
      return this.categories.filter(function(item) {
        return item.pk === pk;
      })[0];
    };

    return CategoryList;

  })();

  Mark.pipes.datetime = function(date) {
    return new Date(+date || date).toLocaleString();
  };

  Mark.pipes.sanitize = function(str, escape_only) {
    var input, output;
    if (escape_only == null) {
      escape_only = false;
    }
    input = !escape_only ? "[<>&\"'\/]" : "[<>]";
    output = ["&lt;", "&gt;", "&amp;", "&quot;", "&#39;", "&#x2F;"];
    return str.replace(new RegExp(input, "g"), function(s) {
      return output[input.indexOf(s) - 1];
    });
  };

  Mark.pipes.escape = function(str) {
    return Mark.pipes.sanitize(str, true);
  };

  window.template_includes = {
    'all_feed_row': "<li class='feed-row' id='feed-0' data-id='0' data-name='All Items'> Unread Items <small>({{total_unread_count}})</small> </li>",
    'feed_row': "<li class='feed-row{{if not success}} error{{/if}}{{if category}} indent{{/if}}' id='feed-{{pk}}' data-id='{{pk}}' {{if category}}data-category='{{category}}'{{/if}} data-name='{{title|sanitize}}'{{if not success}} title='{{last_error|sanitize}}'{{/if}}> <span>{{title|escape}}</span> <small>({{unread}})</small> <div class='marker glyphicon glyphicon-wrench'></div> </li>",
    'category_row': "<li class='category-row open' id='category-c{{pk}}' data-id='{{pk}}' data-name='{{name|sanitize}}'> <div class='folder glyphicon glyphicon-folder-open'></div> <span>{{name|escape}}</span> <small>({{unread}})</small> <div class='marker glyphicon glyphicon-chevron-up'></div> </li>"
  };

  Mark.includes.all_feed_row = window.template_includes['all_feed_row'];

  Mark.includes.feed_row = window.template_includes['feed_row'];

  Mark.includes.category_row = window.template_includes['category_row'];

  window.templates = {
    'loading_bar': "<div class='progress progress-striped active'><div class='progress-bar' role='progressbar' style='width: 100%'></div></div>",
    'feed_list': "{{all_feed_row}} {{feeds.feed_list}} {{feed_row}} {{/feeds.feed_list}}",
    'articles': "{{articles}} <li class='article-row{{if read}} read{{/if}}' id='article-{{article.pk}}' data-id='{{article.pk}}'> <div class='article-row-title'> <img class='feed-icon' src='{{feed.image}}' title='{{feed.title|sanitize}}' alt='Feed Icon'> <div class='article-feed-name'>{{feed.title|escape}}</div> <div class='article-title'>{{article.title|escape}}</div> <div class='article-date' title='Published: {{article.date_published}} Discovered: {{article.date_added}}'>{{article.date_published_relative}}</div> </div> <div class='article-content panel panel-default'> <div class='article-content-title panel-heading'> <h2><a href='{{article.url|sanitize}}' target='_blank'>{{article.title|escape}}</a></h2> </div> <div class='article-content-main panel-body' data-loaded='false'> </div> <div class='article-content-footer panel-footer'> <div><span class='glyphicon glyphicon-envelope'></span> <span>{{if read}}Mark unread{{else}}Mark read{{/if}}</span></div> </div> </div> </li> {{/articles}}",
    'modal': "<div class='modal fade' id='modal' tabindex='-1' role='dialog' data-for='{{for}}'> <div class='modal-dialog'> <div class='modal-content'> <div class='modal-header'> <button type='button' class='close' data-dismiss='modal'>&times;</button> <h4 class='modal-title' id='modal_label'>{{title|escape}}</h4> </div> <div class='modal-body'></div> <div class='modal-footer'> <button type='button' class='btn btn-primary' id='modal_submit'>{{modal_submit_text}}</button> </div> </div> </div> </div>",
    'add_feed_form': "<div class='alert alert-danger hidden'></div> <form class='form-horizontal' role='form'> <div class='form-group'> <label class='col-md-2 control-label' for='id_url'>Feed URL</label> <div class='col-md-12'> <input class='form-control' id='id_url' name='url' type='url'> </div> </div> </form>",
    'edit_feed_form': "<div class='alert alert-danger hidden'></div> <form id='modal-form' class='form-horizontal' role='form'> <div class='form-group'> <label class='col-md-3 control-label' for='id_title'>Feed Title</label> <div class='col-md-11'> <input class='form-control' id='id_title' name='title' value='{{title|sanitize}}'> </div> </div> <div class='form-group'> <label class='col-md-3 control-label' for='id_feed_url'>Feed URL</label> <div class='col-md-11'> <input class='form-control' id='id_feed_url' name='feed_url' type='url' value='{{feed_url|sanitize}}'> </div> </div> <div class='form-group'> <label class='col-md-3 control-label' for='id_site_url'>Site URL</label> <div class='col-md-11'> <input class='form-control' id='id_site_url' name='site_url' type='url' value='{{site_url|sanitize}}'> </div> </div> <div class='form-group'> <label class='col-md-3 control-label' for='id_category'>Category</label> <div class='col-md-11'> <select class='form-control' id='id_category' name='category'> <option value=''>---------</option> {{categories}} <option value='{{pk}}'{{if tmp.category|equals>`pk|number`}} selected{{/if}}>{{name}}</option> {{/categories}} </select> </div> </div> <div class='form-group'> <button type='button' class='btn btn-danger pull-right' style='margin-right:10px;' id='modal_delete'>Delete Feed</button> </div> </form>"
  };

  check_for_new_articles = function() {
    var feed, url;
    feed = window.feeds.get_current_feed();
    if (!window.feeds.current_feed_is_category) {
      url = window.AJAX_BASE + "feeds/feeds/" + feed + "/new";
    } else {
      url = window.AJAX_BASE + "feeds/category/" + (feed.slice(1)) + "/new";
    }
    return $.ajax({
      url: url,
      data: {
        'newest_article': window.feeds.newest_article.toISOString()
      },
      dataType: 'json',
      success: function(data) {
        if (data.new_articles) {
          window.feeds.new_articles_available = true;
          if (!window.feeds.current_feed_is_category) {
            $("#feed-" + feed).addClass('update');
          } else {
            $("#category-" + feed).addClass('update');
          }
        } else {
          window.feeds.new_articles_available = false;
          if (!window.feeds.current_feed_is_category) {
            $("#feed-" + feed).removeClass('update');
          } else {
            $("#category-" + feed).removeClass('update');
          }
        }
        window.feeds.update_title();
        return setTimeout(check_for_new_articles, 60000);
      }
    });
  };

  $(document).ready(function() {
    return window.feeds = new FeedManager();
  });

}).call(this);
