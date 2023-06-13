


function connect(_this){
    text = _this.innerText;
    loading(_this);
    $.ajax({
        url:"/login",
        type:"POST",
        data:{'pwd': $("#pwd").val(),'user':$("#user").val(), 'key':$("#nonce").val()},
        success: (res)=>{
            if (res.success){
                document.location = res.location;


            }else{
                $(_this).hide(300);
                var popup = document.getElementById("popup");
                var title = document.getElementById("popup-title");
                var notice = document.getElementById("popup-notice");
                title.innerHTML += res.title;
                notice.innerText = res.notice;
                popup.style.display = "block";
                setTimeout(()=>{popup.style.display = "none";title.innerText="";notice.innerText="";$(_this).show(300);},2000);
            }
            unloading(_this, text);
        }

    })
}