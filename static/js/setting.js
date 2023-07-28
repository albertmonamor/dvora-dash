
var signatureO = null;//new SignaturePad(document.getElementById('set-sig-owner'));
function clearSignature(){
    if (document.getElementById('set-sig-owner')){
        signatureO.clear();
    }
}


function open_modal_signature(t){
    modal = document.getElementById('modalsetting');
    title = document.getElementById('ms-title');
    body = document.getElementById('ms-body');
    footer = document.getElementById('ms-footer');
    $(modal).show();
    // title
    title.textContent = "יצירת חתימה לחוזים"
    // body
    body.innerHTML = 
    `<div class="sig-owner">
        <span>חתימה
            <i class="fa-solid fa-trash-can" onclick="clearSignature()"></i>
        </span>
        <canvas id="set-sig-owner"></canvas>
    </div>`
    signatureO = new SignaturePad(document.getElementById('set-sig-owner'));


    footer.innerHTML = `
    <button class="btn-add-sig btn-save-signature" role="0" type="button" onclick="set_signature(this)">
        <span> שמור חתימה</span>
    </button>
    `

    
}

function set_signature(t){
    pic_signa = signatureO._toSVG();
    if (pic_signa.length < 3500){
        show_popup_error({"title":"שיגאה בחתימה","notice":"חתימה קצרה מידיי"}, null)
        return;
    }
    update_or_set_ajax(t, {"signature":pic_signa})
}


function set_email(t){
    email = document.getElementById("mailsetting");
    if (!email.value){
        return;
    }
    update_or_set_ajax(t, {"email":email.value})
}


function set_identify(t){
    identify = document.getElementById("idsetting");
    if (!identify.value){
        return;
    }
    update_or_set_ajax(t, {"identify":identify.value})

}

function update_or_set_ajax(t, data){
    $.ajax({
        url:"/setting/"+t.role,
        type:"post",
        data:data,
        success:(res)=>{
            if (res.success){
                getTemplate($('#4')[0],'4', 1);
            }
            else{
                show_popup_error(res, null);
            }
        }
    
    })

}

function hide_ms(rechache=0){
    modal = document.getElementById('modalsetting');
    $(modal).hide();
    if (rechache){
        document.getElementById('ms-title').textContent='';
        document.getElementById('ms-body').innerHTML ='';
        document.getElementById('msfooter').innerHTML ='';
    }

}

