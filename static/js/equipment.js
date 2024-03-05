/**
 * 
 * @param {Element} t 
 * @param {String} exist 
 * @param {String} price
 */

function openEditItem(t, name, price, exist){
    $(document.getElementById("model-addlead")).fadeIn(300);
    if (document.getElementById("modalcontent").innerHTML!=""){return;}
    $.ajax({
        url:"/template/16",
        type:"post",
        success:(res)=>{
            if (res.success){
                $(document.getElementById("modalequip")).fadeIn(300);
                $(document.getElementById("modalstart")).fadeOut(100);
                document.getElementById("aleadtitle").innerText = "עריכת ציוד "+ name;
                document.getElementById("modaldes").innerText = res.welcome;
                document.getElementById("modalcontent").innerHTML = res.template
                document.getElementById("closeModalButton").onclick = ()=>{closeModalAddEquipment();};
                supply_json = res.supply;
                const btn = document.getElementById("addequipbutton");
                const form = document.getElementById("add-lead-form");
                const btnParent = btn.parentElement;
                document.getElementById("name").value = name;
                document.getElementById("tel").value = price;
                document.getElementById("exist").value = exist;
                btn.classList.add("btnEdit");
                btn.children[0].textContent = 'עדכן';
                // new delete
                const divX = document.createElement("div");
                divX.style.position = 'relative';
                const btn_delete = document.createElement("button");
                btn_delete.type= 'button';
                btn_delete.classList.add("button-addlead-summary");
                btn_delete.classList.add("btnDelete");
                btn_delete.classList.add("small-menu-trigger");
                btn_delete.onclick = function(){deleteEquipment(this, t.id);}
                btn_delete.innerHTML = `<i class="fa-solid fa-trash-can"></i>`;
                divX.appendChild(btn_delete);
                btnParent.appendChild(divX);
                form.onsubmit = function(){updateEquipment(event, this, t);}
                document.getElementById("modalequip").click();
            }
            else{
                popNotice("error", res.title, res.notice);
            }
        }
    })
}


function updateEquipment(e, t, last_this){
    e.preventDefault();
    const name = document.getElementById("name");
    const price = document.getElementById("tel");
    const exist = document.getElementById("exist");
    $.ajax({
        url:"/update_equipment/"+last_this.id,
        type:"post",
        data:{"name":name.value, "price":price.value.replace(/[\s₪]/g, ""), "exist":exist.value.replace(/[\s₪]/g, "")},
        success:(res)=>{
            if (res.success){
                closeModalAddEquipment(t, 0);
                last_this.children[0].textContent = name.value;
                last_this.children[1].textContent = price.value;
                last_this.children[2].textContent = exist.value;
                console.log(last_this);
                
            }
            else{
                popNotice("error", res.title, res.notice);
            }
        }

    })
    

    
}

function addEquipment(e, _this){
    e.preventDefault();
    button = document.getElementById("addequipbutton");
    _name = _this.children[1].value;
    price = _this.children[3].value;
    exist = _this.children[5].value;
    loading(button);
    $.ajax({
        url:"/add_equipment",
        type:"post",
        data:{"name":_name, "price":price, "exist":exist},
        success:(res)=>{
            if (res.success){
                getTemplate($("#1")[0], "1", 1);
                closeModalAddEquipment(1);

            }
            else{
                popNotice("error", res.title, res.notice);
            }
            unloading(button, 'הוסף');
            
        }
    })
}


function deleteEquipment(t, id){
    const cby = function(){
        $.ajax({
            url:"/del_equipment/"+id,
            type:"post",
            success:(res)=>{
                if (res.success){
                    document.getElementById(id).remove();
                    closeModalAddEquipment(0);
                    popNotice("success", "נמחק", "הציוד " + id + " נמחק");
                }
                else{
                    popNotice("error", res.title, res.notice);
    
                }
                
            }
        })
    };

    const cbn = function(){closeSmallConfirm()}
    openSmallConfirm(t, cby, cbn);

}

function openModalAddEquipment(_this){
    $(document.getElementById("model-addlead")).fadeIn(300);
    if (document.getElementById("modalcontent").innerHTML!=""){return;}
    $.ajax({
        url:"/template/"+_this.id,
        type:"post",
        success:(res)=>{
            if (res.success){
                $(document.getElementById("modalequip")).fadeIn(300);
                $(document.getElementById("modalstart")).fadeOut(100);
                document.getElementById("aleadtitle").innerText = "הוספת ציוד למערכת";
                document.getElementById("modaldes").innerText = res.welcome;
                document.getElementById("modalcontent").innerHTML = res.template
                document.getElementById("closeModalButton").onclick = ()=>{closeModalAddEquipment();};
                supply_json = res.supply;
                
            }
            else{

            }
        }
    })
}

function closeModalAddEquipment(ask=0){
    $(document.getElementById("model-addlead")).fadeOut(100);
    $(document.getElementById("modaldes")).fadeIn(300);
    $(document.getElementById("modalstart")).fadeIn(300);
    document.getElementById("modalcontent").innerHTML = "";
    $(document.getElementById("modalcontent")).fadeOut(0);
}





function uploadEquipmentTxt(e){
    console.log(e)
    // notice stupid hackers:: just side client :(, the server verify this too
    MAX_SIZE = 1000*100;
    const fileI = e.target;
    const file = fileI.files[0];
    if (file.type != "text/plain"){
        return;
    }
    else if (file.size > MAX_SIZE || file.size == 0){
        return;
    }
    en = document.getElementById("importnonce")
    form_data_up = new FormData();
    form_data_up.append("txt", file);
    form_data_up.append("nonce", en.value);
    $.ajax({
        url:"/import_txt",
        type:"post",
        data:form_data_up,
        processData: false,
        contentType: false,
        success:(res)=>{
            if (res.success){
                getTemplate($("#1")[0], "1", 1);
                en.value = JSON.parse(JSON.stringify(res).replace(/(['"])?([a-zA-Z0-9_]+)(['"])?:/g, '"$2": '))[en.value];
            }
            else{
                popNotice("error", res.title, res.notice);
            }
            fileI.value = null;
        }
    })
    
    
}


function downloadEquipmentTxt(_this){
    lhtml = _this.innerHTML;
    _this.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i>`;
    location.href = "/export_txt";
    _this.innerHTML = lhtml;
}