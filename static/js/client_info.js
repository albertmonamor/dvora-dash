

edit_table_is_open = false;

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
function del_his_eventLead(_this, __tmp=0){
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
                setTimeout(()=>{getTemplate($("#"+__tmp)[0],__tmp, 1);cleanHash();}, 500);
            }
            else{
                _this.innerHTML = lhtml;
            }
        }
    })
}


function reCancel_eventLead(_this){
    if (!confirm("לשחזר אירוע?")){
        return;
    }
    lhtml = _this.innerHTML;
    _this.innerHTML = `<i class="fa-solid fa-clock-rotate-left fa-spin fa-spin-reverse"></i>`;
    cid = _this.id.slice(1, _this.id.length);
    $.ajax({
        url:"/event_lead_action/"+_this.id.slice(0,1),
        data:{"client_id":cid},
        type:"post",
        success:(res)=>{
            if (res.success){
                closeLeadInforamtionModal(null, cid);
                setTimeout(()=>{getTemplate($("#2")[0],"2", 1);cleanHash();}, 500);
            }else{
                popNotice("error", res.title, res.notice);

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
                popNotice("error", res.title, res.notice);
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
            if (b.textContent && tr.children[0].id != "addequipment"){
                count = b.textContent.split("x")[0];
                b.innerHTML = `<input type="text" class="edit-table-input" value="${count}" placeholder="${b.textContent}">`;
                edit_table_is_open = true;
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
    else if (_type == 4){
        parent = document.getElementById("edit-payment");
        parent1 = document.getElementById("prepayment");
        parent2 = document.getElementById("typepayment")
        parent3 = document.getElementById("total-pay-info");
        // p1
        $(parent1.children[0]).hide();
        ch = parent1.children[1];
        ch.innerHTML = `<input type="tel" style="width:100%" placeholder="${ch.textContent}" class="edit-table-input">`

        // p2
        $(parent2.children[0]).hide()
        $(parent2.children[1]).hide()
        a = parent2.children[0].role;
        parent2.innerHTML += `
        <div class="edit-type-payment">
            <button class="payment-button" onclick="selectTypePay(this, 0)">מזומן</button>
            <button class="payment-button tpayb" onclick="selectTypePay(this, 1)">העברה בנקאית</button>
            <button class="payment-button tpayb" onclick="selectTypePay(this, 2)">צ'ק</button>
            <input type="hidden" id="type-pay" value="${parent2.children[0].role}" name="type-pay">
        </div>
        `

        if (a == 0){
            selectTypePay(parent2.children[2].children[0], a)
        }
        else if (a == 1){
            selectTypePay(parent2.children[2].children[1], a)
        }
        else if (a == 2){
            selectTypePay(parent2.children[2].children[2], a)
        }
        // p3 
        total_pay = parent3.children[0];
        parent3.innerHTML = `<input type="tel" style="width:100%" placeholder="${total_pay.textContent}" class="edit-table-input">`





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
        edit_table_is_open = false;
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
                        popNotice("error", res.title, res.notice);
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
                        popNotice("error", res.title, res.notice);
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
                        popNotice("error", res.title, res.notice);
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
                        popNotice("error", res.title, res.notice);
                    }
                }
            })
        }
    }
    else if (_type == 4){
        parent = document.getElementById("edit-payment");
        parent1 = document.getElementById("prepayment");
        parent2 = document.getElementById("typepayment")
        parent3 = document.getElementById("total-pay-info")
        // p1
        $(parent1.children[0]).show();
        ch = parent1.children[1];
        _input = ch.children[0];
        dmoney = _input.value ? _input.value : _input.placeholder ;
        ch.innerHTML = _input.placeholder;


        // p2 
        type_payemnt = document.getElementById("type-pay").value;
        $(parent2.children[0]).show()
        $(parent2.children[1]).show()
        parent2.children[2].remove()

        //p3 
        tp = parent3.children[0];
        const _total_money = tp.value ? tp.value: tp.placeholder;
        parent3.innerHTML =  `<span id="totalpay">${tp.placeholder}</span>`;

        
        
        
        if (toUpdate){
            $.ajax({
                url:"/update_lead/"+_type,
                type:"post",
                data:{"data":JSON.stringify({"dmoney":dmoney, "type_pay":type_payemnt, 'total_money':_total_money}), "client_id":parent.role, },
                success:(res)=>{
                    if (res.success){
                        
                        parent = document.getElementById("edit-payment");
                        openLeadInformationModal(document.getElementById("10|"+parent.role));
                    }
                    else{
                        popNotice("error", res.title, res.notice);
                    }
                }
            })
        }

    }


    parent = _this.parentElement;
    parent.classList.remove("edit-open");
    parent.innerHTML = `<i onclick="editLeadInforamtion(this, ${_type})" class="fa-solid fa-user-pen"></i>`;
}


function open_modal_add_equipment(_this){
    cid =_this.parentElement.parentElement.parentElement.role;
    var ML = document.createElement('div');
    ML.id = "modaladdequipment"+cid
    ML.classList.add('modal-link');
    ML.style.zIndex = '1000';
    document.body.appendChild(ML);

    var MB = document.createElement('div');
    MB.classList.add('modal-link-body');
    ML.appendChild(MB);

    var title = document.createElement('span');
    title.classList.add("modal-link-title")
    title.textContent = "הוספת ציוד ללקוח";
    title.innerHTML += `<i onclick='close_modal_add_equipment("${cid}")' class="fa-solid fa-circle-xmark"></i>`
    MB.appendChild(title)
    var DB = document.createElement('div');
    DB.innerHTML = `
    <div class="search-form">
        <span>חפש מתוך הרשימה</span>
        <input class="search-input" id="searchinputadd" placeholder="לדוגמא: הגברה" oninput='showEquipmentBySearch(this.value)' name="search-equip">
    </div>
    <div class='list-equipment search-result' id="list-equipment">

    </div>
    <div class="search-action">
        <button type="button" class="search-save-btn" onclick="updateEquipmentClient(this, '${cid}')">
            <span>שמירה</span>
            <i class="fa-solid fa-check"></i>
        </button>
    </div>
    </div>
    
    `;
    MB.appendChild(DB);
    $.ajax({
        url:"/template/15",
        type:"post",
        success:(res)=>{
            if (res.success){
                supply_json = res.supply;
            }
            else{
                popNotice("error", res.title, res.notice);
            }
        }
    })
}

function close_modal_add_equipment(cid){
    document.getElementById("modaladdequipment"+cid).remove()
}
/**
 * 
 * @param {Element} _this 
 * @param {String} _title 
 * @param {String} btn 
 * @param {String} show_agree 
 */
function open_modal_link(_this, _title=null,btn=null, show_agree=null){
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
    if (!_title){
        title.textContent = "שלח את הלינק ללקוח לחתימה"
        title.innerHTML += `<span class="subtitle"> <b>שם לב:</b>
        נותרו
        <div class="lnk-countdown">
            <span id="lnks">--</span>
            <span id="lnkm">--</span>
            <span id="lnkh">--</span>
            <span id="lnkd">--</span>

        </div>
        דקות לחתום על החוזה 
        </span>`
    }else{
        title.textContent = _title;
    }

    title.innerHTML += `<i onclick='close_modal_link("${cid}")' class="fa-solid fa-circle-xmark"></i>`

    MB.appendChild(title)

    var DB = document.createElement('div');
    DB.classList.add('modal-buttons-actions-link');
    MB.appendChild(DB);
    if (!show_agree){
        show_agree = `show_link_client(this, '${_this.id}')`
    }
    if (!btn){
        btn = "הצג לינק"
    }
    DB.innerHTML += `<button id="getlink" class="modal-button-create-link" type="button" onclick="${show_agree}">${btn}</button>`
}

function close_modal_link(_id){
    document.getElementById("modallink"+_id).remove()
    clearInterval(TIMER);
}



function show_link_client(_t, acid, override){
    if (override){
        if (!confirm("יצירת קישור חדש תגרום למחיקת הקישור הקודם")){
            return;
        }
    }
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
                _this.onclick=function(){show_link_client(this, acid, 1);} 
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
                nd = new Date().getTime()
                cd = new Date(res.ctime).getTime()
                if (cd-nd < 0){
                    document.getElementById("lnks").classList.add('lnkexpired')
                    document.getElementById("lnkm").classList.add('lnkexpired')
                }
                else{
                    document.getElementById("lnks").classList.remove('lnkexpired')
                    document.getElementById("lnkm").classList.remove('lnkexpired')
                }
                countdown(res.ctime)
                
                
            }
            else{
                popNotice("error", res.title, res.notice);
                _t.innerHTML = lhtml;
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


/**
 * 
 * @param {Element} t 
 */
function open_modal_agreement(t){
    open_modal_link(t, "פתח חוזה השכרה", "הצג קישור", `show_agreement(this, '${t.id}')`);
}

function show_agreement(t, acid){
    lhtml = t.innerHTML;
    t.innerHTML = `<i class="fa-solid fa-ellipsis fa-beat-fade fa-2xl"></i>`;
    _body = t.parentElement.parentElement
    parent = t.parentElement
    a = acid.slice(0, 1)
    cid = acid.slice(1, acid.length)
    $.ajax({
        url:"/event_lead_action/"+a,
        type:"post",
        data:{"client_id":cid},
        success:(res)=>{
            if (res.success){
                _link_ = window.location.origin + res.url_params

                b = document.createElement("button")
                b.type ="button"
                b.classList.add("modal-button-create-link") 
                b.classList.add("copy-link") 
                b.onclick = function(){window.open(_link_, "_blank");}
                b.innerHTML = `<i class="fa-solid fa-up-right-from-square fa-rotate-270"></i>`
                parent.appendChild(b)

                t.innerHTML = `<i class="fa-solid fa-copy">`
                t.onclick = function(){copy_link_agreement(this)}
                link = document.createElement("input")
                link.type = "text"
                link.classList.add("input-link")
                link.id = "inputlink"
                link.value = _link_
                _body.appendChild(link)
            }
            else{
                popNotice("error", res.title, res.notice);
                t.innerHTML = lhtml
            }
    
        }
    })
}



function open_modal_finished(t){
    name_client = document.getElementById("cname").textContent;
    open_modal_link(t, `האירוע של "${name_client}" הסתיים?`, "סיימנו!", `event_finished(this, '${t.id}')`);
}

function event_finished(t, acid){

    a = acid.slice(0, 1)
    cid = acid.slice(1, acid.length);
    $.ajax({
        url:"/event_lead_action/"+a,
        type:"post",
        data:{"client_id":cid},
        success:(res)=>{
            if (res.success){
                t.innerHTML = `<i class="fa-solid fa-star fa-bounce"></i>`
                closeLeadInforamtionModal(null, cid);
                setTimeout(()=>{close_modal_link(cid);getTemplate($("#0")[0],"0", 1);cleanHash();}, 2000);

            }
            else{
                popNotice("error", res.title, res.notice);
            }
        }
    })
}

function showOptionItemEquipmentClient(t){
    if (edit_table_is_open){return;}
    reEditEquipmentItem()
    eid = t.id;
    cid = t.parentElement.role
    t.onclick='';
    div = document.createElement('div');
    div.classList.add('edit-equipment-option');
    div.innerHTML = `
    <div class="equipment-option">
        <div class="option-body-e">
        <i class="fa-solid fa-trash-can" onclick="removeEquipmentItem(this, '${cid}', '${eid}', 5)"></i>
        <i class="fa-solid fa-xmark" onclick="reEditEquipmentItem()"></i>
        </div>
    </div>
    `
    t.appendChild(div);


}

function removeEquipmentItem(t, cid, eid, _type){
    equipment = document.getElementById(eid);
    $.ajax({
        url:"/update_lead/"+_type,
        type:"post",
        data:{"data":JSON.stringify({"eid":eid}), "client_id":cid},
        success:(res)=>{
            if (res.success){
                parent = document.getElementById('body-table-information');
                openLeadInformationModal(document.getElementById("10|"+cid));
            }
            else{
                popNotice("error", res.title, res.notice);
            }
        }
    })
    reEditEquipmentItem();
}

function reEditEquipmentItem(){
    elem = document.getElementsByClassName("edit-equipment-option")[0]
    if (elem == undefined){
        return;
    }
    var parent_edit = elem.parentElement;
    elem.remove();
    setTimeout(function(){parent_edit.onclick= function(){showOptionItemEquipmentClient(this)}}, 1000);
    
}   

function updateEquipmentClient(t, cid){
    console.log(cid)
    $.ajax({
        url:"/add_equipment_client",
        type:"post",
        data:{"cid":cid, "supply":JSON.stringify(supply_json)},
        success:(res)=>{
            if (res.success){
                close_modal_add_equipment(cid);
                openLeadInformationModal(document.getElementById("10|"+cid));
            }
            else{
                popNotice("error", res.title, res.notice);
            }
        }
    })
}