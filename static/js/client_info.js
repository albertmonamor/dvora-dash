


function getDateAsValue(strDate){
    const dateParts = strDate.split(".");
    const year = parseInt(dateParts[0]);  
    const month = parseInt(dateParts[1]) < 10 && dateParts[1].length < 2 ? "0" + dateParts[1] : dateParts[1];
    const day = parseInt(dateParts[2]) < 10 && dateParts[2].length < 2 ? "0" + dateParts[2] : dateParts[2];
     
    return year+"-"+month+"-"+day
}



/**
 * 
 * @param {Element} _this 
 * @returns 
 */
function del_his_eventLead(_this){
    if (!confirm("אתה בטוח?")){
        return;
    }
    lhtml = _this.innerHTML;
    if (_this.id.slice(0,1) == 0){
        _this.innerHTML = `<i class="fa-solid fa-trash-can fa-beat"></i>`
    }
    else if (_this.id.slice(0,1) == 1){
        _this.innerHTML = `<i class="fa-solid fa-clock-rotate-left fa-spin fa-spin-reverse"></i>`
    }
    cid = _this.id.slice(1, _this.id.length);
    $.ajax({
        url:"/event_lead_action/"+_this.id.slice(0,1),
        data:{"client_id":cid},
        type:"post",
        success:(res)=>{
            if (res.success){
                closeLeadInforamtionModal(null, cid);
                location.href = "#"+cid;
                setTimeout(()=>{getTemplate($("#0")[0],"0", 1);cleanHash();}, 500);
            }
            else{
                _this.innerHTML = lhtml;
            }
        }
    })
}

/**
 * 
 * @param {Element} _this 
 */
function create_invoice_client(_this){

    lhtml = _this.innerHTML;
    cid = _this.id.slice(1, _this.id.length);
    _this.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i>`;
    $.ajax({
        url:"/event_lead_action/"+_this.id.slice(0,1),
        type:"post",
        data:{"client_id":cid},
        success:(res)=>{
            if (res.success){
                _this.id = "3"+cid;
                _this.innerHTML = `<i class="fa-solid fa-file-arrow-down"></i><span>הורד חשבונית</span>`
                _this.onclick = function(){download_invoice_client(this)};
                lhtml = _this.innerHTML;
            }
            else{
                show_popup_error(res, _this);
            }
            _this.innerHTML = lhtml;
        }
    })
}


function download_invoice_client(_this){
    lhtml = _this.innerHTML;
    cid = _this.id.slice(1, _this.id.length);
    _this.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i>`;
    location.href = "/event_lead_action/"+_this.id.slice(0,1)+"?client_id="+cid;
    _this.innerHTML = lhtml;
}


/**
 * 
 * @param {Element} _this 
 * @param {Int16Array} _type 
 */
function editLeadInforamtion(_this, _type){
    parent = undefined;
    if (_type === 0){
        parent = document.getElementById('body-table-information');
        for (tr of parent.children){
            b = tr.children[1];
            if (b.textContent){
                count = b.textContent.split("x")[0];
                b.innerHTML = `<input type="text" class="edit-table-input" value="${count}" placeholder="${b.textContent}">`;
            }
        }
        
        
    }
    else if (_type == 1){
        parent = document.getElementById("edit-date");
        ch0 = parent.children[0];
        ch1 = parent.children[1];
        ordate = ch1.textContent;
         // last date to show default
        vdate = getDateAsValue(ordate);
        // hide & remove
        $(ch0).fadeOut(0);
        ch1.remove();
        parent.innerHTML += `<input type="date" class="edit-table-input" value="${vdate}" placeholder="${ordate}">`

    }
    else if (_type == 2){
        parent = document.getElementById("edit-location");
        ch1 = parent.children[1];
        orlocation = ch1.textContent;
        ch1.innerHTML = `<input type="text" class="edit-table-input"  placeholder="${orlocation}">`
        
    }
    else if (_type == 3){
            parent = document.getElementById("edit-expense");
            var index = 0;
            for (elem of parent.children){
                if (index){
                    ch1 = elem.children[1];
                    $(ch1).hide();
                    elem.innerHTML += `<input type="tel" placeholder="${ch1.textContent}" class="edit-table-input">`
                }
                index++;
            }
    }
    parentAc = _this.parentElement
    parentAc.innerHTML = `<i onclick="reEditInformation(this, ${_type}, 1);" class="fa-solid fa-check"></i><i onclick="reEditInformation(this, ${_type});" class="fa-solid fa-xmark"></i>`
    parentAc.classList.add("edit-open");
}


function reEditInformation(_this, _type, toUpdate=0){
    
    if (_type == 0){
        json_equip_value = []
        parent = document.getElementById('body-table-information');
        for (tr of parent.children){
            b = tr.children[1];
            input = b.children[0];
            if (input != undefined && input.tagName === "INPUT"){
                json_equip_value.push({"equip_id":tr.id, "count":input.value});
                b.innerHTML = `${input.placeholder.split("x")[0]}<span style="font-size: 12px;">x${input.placeholder.split("x")[1]}</span>`;
            }
        }
        if (toUpdate){
            $.ajax({
                url:"/update_lead/"+_type,
                type:"post",
                data:{"data":JSON.stringify(json_equip_value), "client_id":parent.role},
                success:(res)=>{
                    if (res.success){
                        parent = document.getElementById('body-table-information');
                        openLeadInformationModal(document.getElementById("10|"+parent.role));
                    }
                    else{
                        show_popup_error(res, "");
                    }
                }
            })
        }

    }else if (_type == 1){
        parent = document.getElementById("edit-date");
        ch0 = parent.children[0];
        ch1 = parent.children[1];
        ordate = ch1.placeholder;
        ndata = ch1.value;
        ch1.remove();
        $(ch0).show();
        parent.innerHTML += `<span class="dmy">${ordate.replace(/\-/g, ".")}</span>`;
        if (toUpdate){
            $.ajax({
                url:"/update_lead/"+_type,
                type:"post",
                data:{"data":ndata, "client_id":parent.role},
                success:(res)=>{
                    if (res.success){
                        parent = document.getElementById("edit-date");
                        openLeadInformationModal(document.getElementById("10|"+parent.role));
                    }
                    else{
                        show_popup_error(res, null)
                    }
                }
            })
        }

    }
    else if ( _type == 2){
        parent = document.getElementById("edit-location");
        ch0 = parent.children[1]
        ch1 = ch0.children[0];
        _location = ch1.value;
        ch0.innerHTML = "";
        ch0.textContent = ch1.placeholder;

        if (toUpdate){
            $.ajax({
                url:"/update_lead/"+_type,
                type:"post",
                data:{"data":_location, "client_id":parent.role},
                success: (res)=>{
                    if (res.success){
                        parent = document.getElementById("edit-location");
                        openLeadInformationModal(document.getElementById("10|"+parent.role));

                    }else{
                        show_popup_error(res, null)
                    }
                }
            })
        }

    }
    else if (_type == 3){
        parent = document.getElementById("edit-expense");
        var index = 0;
        arrayV = []
        for (elem of parent.children){
            if (index){
                ch1 = elem.children[1];
                exp_value = elem.children[2].value;

                arrayV.push((exp_value ? exp_value: elem.children[2].placeholder));
                elem.children[2].remove();
                $(ch1).show();
                
            }
            index++;
            }

        if (toUpdate){
            $.ajax({
                url:"/update_lead/"+_type,
                type:"post",
                data:{"data":JSON.stringify(arrayV), "client_id":parent.role},
                success:(res)=>{
                    if (res.success){
                        parent = document.getElementById("edit-expense");
                        openLeadInformationModal(document.getElementById("10|"+parent.role));

                    }else{
                        show_popup_error(res, null);
                    }
                }
            })
        }
    }


    parent = _this.parentElement;
    parent.classList.remove("edit-open");
    parent.innerHTML = `<i onclick="editLeadInforamtion(this, ${_type})" class="fa-solid fa-user-pen"></i>`;
}


function open_modal_link(_this){
    cid =_this.id.slice(1, _this.id.length)
    var ML = document.createElement('div');
    ML.id = "modallink"+cid
    ML.classList.add('modal-link');
    ML.style.zIndex = '1000';
    document.body.appendChild(ML);

    var MB = document.createElement('div');
    MB.classList.add('modal-link-body');
    ML.appendChild(MB);


    var title = document.createElement('span');
    title.classList.add("modal-link-title")
    title.textContent = "שלח את הלינק ללקוח לחתימה"
    title.innerHTML += `<span class="subtitle"> <b>שם לב:</b> לכל קישור ניתן לחתום עד 15 דקות מיצירת הקישור</span>`
    title.innerHTML += `<i onclick='close_modal_link("${cid}")' class="fa-solid fa-circle-xmark"></i>`
    MB.appendChild(title)

    var DB = document.createElement('div');
    DB.classList.add('modal-buttons-actions-link');
    MB.appendChild(DB);
    DB.innerHTML += `<button id="getlink" class="modal-button-create-link" type="button" onclick="show_link_client(this, '${_this.id}')">הצג לינק</button>`




}

function close_modal_link(_id){
    document.getElementById("modallink"+_id).remove()
}



function show_link_client(_t, acid, override){
    if (override){
        if (!confirm("יצירת קישור חדש תגרום למחיקת הקישור הקודם")){
            return;
        }
    }
    _t.onclick=function(){show_link_client(this, acid, 1);}
    _body = _t.parentElement.parentElement;
    lhtml = _t.innerHTML;
    _t.innerHTML = `<i class="fa-solid fa-ellipsis fa-beat-fade fa-2xl"></i>`;
    a = acid.slice(0, 1)
    cid = acid.slice(1, acid.length);
    $.ajax({
        url:"/event_lead_action/"+a,
        type:"post",
        data:{"client_id":cid, "override":override},
        success:(res)=>{
            if (res.success){
                _this = document.getElementById("getlink")
                _this.innerHTML = `<i class="fa-solid fa-arrows-rotate"></i>`
                if (!_this.parentElement.children[1]){
                    b = document.createElement("button")
                    b.type ="button"
                    b.classList.add("modal-button-create-link") 
                    b.classList.add("copy-link") 
                    b.onclick = function(){copy_link_agreement(this);}
                    b.innerHTML = `<i class="fa-solid fa-copy">`
                    _this.parentElement.appendChild(b)
                }
                if (!_body.children[2]){
                    link = document.createElement("input")
                    link.type = "text"
                    link.classList.add("input-link")
                    link.id = "inputlink"
                    link.value = window.location.origin + res.url_params
                    _body.appendChild(link)
                }
                
                else{
                    _body.children[2].value = window.location.origin + res.url_params
                    
                }
            }
            else{
                show_popup_error(res, null);
                _this.innerHTML = lhtml;
            }
        }
    })
}


function copy_link_agreement(_tbut){
    ch2 = document.getElementById("inputlink")
    if (ch2){
        _tbuthtml = _tbut.innerHTML;
        ch2.select();
        // @declaration 
        document.execCommand('copy');
        ch2.setSelectionRange(0, 1000);
        window.getSelection().removeAllRanges();
        _tbut.innerHTML = `<i class="fa-solid fa-thumbs-up fa-shake"></i>`
        setTimeout(()=>{_tbut.innerHTML=_tbuthtml}, 2000);
    }

}
