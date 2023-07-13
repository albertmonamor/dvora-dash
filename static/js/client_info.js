


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