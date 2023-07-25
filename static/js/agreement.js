if (document.getElementById('sig-owner')){
    var signatureO = new SignaturePad(document.getElementById('sig-owner'));
    var signatureC = new SignaturePad(document.getElementById('sig-client'));
}


function clearSignature(parent){
    if (parent == "sig-owner"){
        signatureO.clear();
    }
    else{
        signatureC.clear();
    }
}
function show_popup_error(res){
    //$(_this).hide(300);
    var popup = document.getElementById("popup");
    var title = document.getElementById("popup-title");
    var notice = document.getElementById("popup-notice");
    title.innerHTML += res.title;
    notice.innerText = res.notice;
    popup.style.display = "block";
    setTimeout(()=>{popup.style.display = "none";title.innerText="";notice.innerText=""},3000);
}

/**
 * 
 * @param {Element} _this 
 */
function sent_agreement_client(_this){
    lhtml = _this.innerHTML;
    _this.innerHTML = `<i class="fa-solid fa-spinner fa-spin fa-xl"></i>`
    // full name
    fname       = document.getElementById("fname");
    // location 
    _location   = document.getElementById("_location")
    if (_location.tagName == "SPAN"){_location = _location.textContent}else{_location = _location.value}
    // identify card
    identify    = document.getElementById("identify")
    if (identify.tagName == "SPAN"){identify = identify.textContent}else{identify = identify.value}
    phone       = document.getElementById("phone");
    udate       = document.getElementById("udate")
    signature   = signatureC._toSVG();
    if (signature.length < 1500){
        location.href="#sig-client";
        show_popup_error({"title":"שגיאה בחתימה", "notice":"לא חתמת, או שהחתימה קטנה"})
        _this.innerHTML = lhtml;
        return;
    }
    $.ajax({
        url:"/add_agreement/"+window.location.search,
        type:"post",
        data:{"fname":fname.textContent,
            "_location":_location,
            "identify":identify,
            "phone":phone.textContent,
            "udate":udate.value,
            "signature":signature
        },
        success:(res)=>{
            if (res.success){
                document.body.innerHTML = res.template
                setTimeout(()=>{location.href="https://dvora.pythonanywhere.com/"}, 5000)
            }
            else{
                show_popup_error(res);
                _this.innerHTML = lhtml;
               // location.href=`#${}`

            }
        }
    })

}