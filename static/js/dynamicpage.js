$(function() {

    var newHash      = "",
        $mainContent = $("body"),
        $pageWrap    = $("body"),
        baseHeight   = 0,
        $el;
        

    $(".to-usernews").delegate("a", "click", function() {
        window.location.hash = $(this).attr("href");
        return false;
    });

    
    $(window).bind('hashchange', function(){
    
        newHash = window.location.hash.substring(1);
        
        if (newHash) {
            $mainContent
                .find("body")
                .fadeOut(200, function() {
                    $mainContent.hide().load(newHash, function() {
                        $mainContent.fadeIn(200, function() {

                        });

                    });
                });
        }
        
    });
    
    $(window).trigger('hashchange');

});