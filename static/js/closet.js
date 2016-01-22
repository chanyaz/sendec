/**
 * Created by eprivalov on 25.01.16.
 */
var $form = $('#subscribe-form');
    $form.submit(function(){
        $.ajax({
            type: $form.attr('method'),
            url: $form.attr('action'),
            data: $form.serialize(),
            success: function(data){
                if(data.data == true){
                    $form.find('input[type=email]').val('');
                    $('#subs-success').fadeIn("slow").delay(1100).fadeOut("slow");
                }
                else{
                    $form.find('input[type=email]').val('');
                    $('#subs-fail').fadeIn("slow").delay(1100).fadeOut("slow");
                }
            },
            error: function(result){
                $form.find('input[type=email]').val('');
                $('#subs-fail').fadeIn("slow").delay(1100).fadeOut("slow");
            }

        });
        return false;
    });

        $('.about').click(function(){
            $(this).addClass("active");
            $('#contacts').hide();
            $('.contacts').removeClass("active");
            $('#subscribe').hide();
            $('.subscribe').removeClass("active");
            $('#about').fadeIn("slow");
        });
        $('.contacts').click(function(){
            $(this).addClass("active");
            $('#about').hide();
            $('.about').removeClass("active");
            $('#subscribe').hide();
            $('.subscribe').removeClass("active");
            $('#contacts').fadeIn("slow");
        });
        $('.subscribe').click(function(){
            $(this).addClass("active");
            $('#contacts').hide();
            $('.contacts').removeClass("active");
            $('#about').hide();
            $('.about').removeClass("active");
            $('#subscribe').fadeIn("slow");
        });



        $(function() {

		var dd = new DropDown( $('#dd') );

		$(document).click(function() {
			$('.wrapper-dropdown-1').removeClass('active');
		});

	});

    function DropDown(el) {
        this.dd = el;
        this.initEvents();
    }
    DropDown.prototype = {
        initEvents : function() {
            var obj = this;

            obj.dd.on('click', function(event){
                $(this).toggleClass('active');
                event.stopPropagation();
            });
        }
    };