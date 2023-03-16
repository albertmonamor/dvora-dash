


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
                showAlert(res.title, res.notice);
            }
            unloading(_this, text);
        }

    })
}