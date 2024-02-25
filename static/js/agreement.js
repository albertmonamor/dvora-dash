if (document.getElementById('sig-client')){
    // var signatureO = new SignaturePad(document.getElementById('sig-owner'));
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

/**
 * 
 * @param {Element} _this 
 */
function sent_agreement_client(_this){
    lhtml = _this.innerHTML;
    _this.innerHTML = `<i class="fa-solid fa-spinner fa-spin fa-xl"></i>`
    // identify card
    identify    = document.getElementById("identify")
    signature   = signatureC._toSVG();
    if (signature.length < 1500){
        location.href="#sig-client";
        popNotice("error","שגיאה בחתימה", "לא חתמת, או שהחתימה קטנה")
        _this.innerHTML = lhtml;
        return;
    }
    $.ajax({
        url:"/add_agreement/"+window.location.search,
        type:"post",
        data:{"identify":identify.value,
            "signature":signature
        },
        success:(res)=>{
            if (res.success){
                document.body.innerHTML = res.template
                setTimeout(()=>{location.href="https://dvora.pythonanywhere.com/"}, 5000)
            }
            else{
                popNotice("error", res.title, res.notice);
                _this.innerHTML = lhtml;

            }
        }
    })

}

/* SLEEP */
function Sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}
/* POPUPs */
/**
 * 
 * @param {String} t 
 * @param {String} title 
 * @param {String} notice 
 */
function popNotice(t, title, notice){
    console.log(title);
    // PARENT
    var popup_base = document.getElementById("popbase");
    var is_new = false;
    if (popup_base == undefined){
        popup_base = document.createElement("div");
        popup_base.classList.add("pop-notice-base");
        popup_base.id = "popbase"
        is_new = true;
    }
    var popup = document.createElement("div");
    popup.classList.add("pop-notice");
    popup.classList.add("shadow9-a");
    const id = "popup"+popup_base.children.length;
    popup.id = id;
    popup.onclick = function(){document.getElementById(id)?.remove()};
    // HEAD
    head = document.createElement("div")
    head.classList.add("pop-head");
    head.classList.add(t);
    tit = document.createElement("span");
    tit.innerText = title;
    icon = document.createElement("i");
    if (t == "error"){
        icon.className = "fa-solid fa-triangle-exclamation";
    }
    else{
        icon.className = "fa-regular fa-circle-check";
    }
    // BODY
    not = document.createElement("div");
    not.classList.add("pop-body");
    not.innerText = notice;

    head.appendChild(icon);
    head.appendChild(tit);
    popup.appendChild(head);
    popup.appendChild(not);
    popup_base.appendChild(popup);
    if (is_new){
        document.body.appendChild(popup_base);
    }

    setTimeout(async function() {
        $(popup).fadeOut("slow");
        await Sleep(300);
        popup.click();

    }, 4000);
}
