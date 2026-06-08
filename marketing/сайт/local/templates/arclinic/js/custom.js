$(document).ready(function () {
    $(document).on('click',".load_more_blog", function(){

        var button = $(this).data('next');

        $.ajax({
            url: button,
            success: function (data) {
                $('.navigation-blog').remove();
                
                var newPage = $(data).find('.blog-wrapper').html();
                var nav = $(data).find('.navigation-blog');
                $('.blog-wrapper').append(newPage);
                $('.blog-wrapper').after(nav);

              //  history.replaceState(null, null, location.origin + button);
            
            }
        })
    })
})