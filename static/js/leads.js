var last_client_html = {}

/**
 * 
 * @param {Element} _this 
 */
function openClientInformation(_this){
    if (!(last_client_html.key == undefined)){closeClientInformation("");}
    // set & clear
    parent = _this.parentElement.parentElement;
    bhtml  = parent.innerHTML;
    last_client_html["key"] = parent;
    last_client_html["value"] = bhtml
    parent.innerHTML = "";

    button = `<button onclick="closeClientInformation(this)">סגור</button>`;
    parent.innerHTML+= button;


}

/**
 * 
 * @param {Element} _this 
 */
function closeClientInformation(_this){
    last_client_html.key.innerHTML = last_client_html.value;
    last_client_html.key= undefined;
    last_client_html.value= undefined;
    
}

/**
 * 
 * @param {Element} _this 
 */
function openLeadInformationModal(_this){
    parent = _this.parentElement.parentElement;
    modal = parent.children[parent.childElementCount-1];
    $(modal).fadeIn(300);
    $.ajax({
        url:"/template/"+_this.id,
        type:"post",
        data:{"identify":modal.id},
        success:(res)=>{
            if (res.success){
                document.getElementById("leadcontent"+modal.id).innerHTML = res.template;

            }
            else{
                show_popup_error(res, _this);
            }
        }

    })

}

function closeLeadInforamtionModal(_this, _id=undefined){
    if (!_id){
        modal = _this.parentElement.parentElement;
    }
    else{
        modal = document.getElementById(_id);
    }
    document.getElementById("leadcontent"+modal.id).innerHTML="";
    $(modal).fadeOut(300);
}