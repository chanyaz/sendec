/**
 * Created by eprivalov on 26.02.16.
 */

$(document).ready(function() {
    function removeRssFavourite(news_id) {
        $.ajax({
            type: "POST",
            url: "/news/remove_like_rss/r=" + news_id,
            data: {'csrfmiddlewaretoken': '{{ csrf_token }}'},
            success: alert("success")
        });
    }
});