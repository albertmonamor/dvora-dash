function editEquipment(_this){
    parent = _this.parentElement.parentElement;
    // css class input & button
    cls = "edit-table-input";
    ue = "update-equip";
    // name
    iname = parent.children[0];
    iname.innerHTML = `<input type="text" class="${cls}" value="${iname.innerText}" placeholder="${iname.innerText}">`;
    // price
    iprice = parent.children[1];
    iprice.innerHTML = `<input type="tel" class="${cls}" value="${iprice.innerText}" placeholder="${iprice.innerText}">`;
    // count
    iexist = parent.children[2];
    iexist.innerHTML = `<input type="tel" class="${cls}" value="${iexist.innerText}" placeholder="${iexist.innerText}">`;
    // button to update & cancel 
    iedit = parent.children[3];
    iedit.innerHTML = `<button onclick="reEditEquipment(this, 1)" class='${ue} cancel'><i class="fa-solid fa-xmark"></i></button>`;
    iedit.innerHTML += `<button onclick="updateEquipment(this)" class='${ue} ok'><i class="fa-solid fa-check"></i></button`;
    iedit.innerHTML += `<button onclick="deleteEquipment(this)" class='${ue} grab'><i class="fa-solid fa-trash-can"></i></button`;
}


function reEditEquipment(_this, m){
    parent = _this.parentElement.parentElement;
    iname = parent.children[0];
    iprice =  parent.children[1];
    iexist =  parent.children[2];
    iedit = parent.children[3];
    if (m){
        iname.innerHTML = iname.children[0].placeholder;
        iprice.innerHTML = iprice.children[0].placeholder;
        iexist.innerHTML = iexist.children[0].placeholder;
    }else{
        iname.innerHTML = iname.children[0].value;
        iprice.innerHTML = iprice.children[0].value;
        iexist.innerHTML = iexist.children[0].value;
    }
    iedit.innerHTML = `<button onclick="editEquipment(this)"><i class="fa-solid fa-ellipsis fa-fade"></i></button>`
    
}

function updateEquipment(_this){
    parent = _this.parentElement.parentElement;
    iname = parent.children[0];
    iprice =  parent.children[1];
    iexist =  parent.children[2];
    iedit = parent.children[3];
    _name = iname.children[0].value;
    _price = iprice.children[0].value;
    _exist = iexist.children[0].value;
    $.ajax({
        url:"/update_equipment/"+parent.id,
        type:"post",
        data:{"name":_name, "price":_price.replace(/[\s₪]/g, ""), "exist":_exist.replace(/[\s₪]/g, "")},
        success:(res)=>{
            if (res.success){
                reEditEquipment(_this, 0)
            }
            else{
                show_popup_error(res, _this);
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
                show_popup_error(res, _this)
            }
            unloading(button, 'הוסף');
            
        }
    })
}


function deleteEquipment(_this){
    
    
}

function openModalAddEquipment(_this){
    $(document.getElementById("model-addlead")).show(300);
    if (document.getElementById("modalcontent").innerHTML!=""){return;}
    $.ajax({
        url:"/template/"+_this.id,
        type:"post",
        success:(res)=>{
            if (res.success){
                document.getElementById("aleadtitle").innerText = "הוספת ציוד למערכת"
                document.getElementById("modaldes").innerText = res.welcome
                document.getElementById("modalcontent").innerHTML = res.template
                supply_json = res.supply;
            }
            else{

            }
        }
    })
}

function closeModalAddEquipment(ask=0){
    if (ask || confirm("לבטל הוספת ציוד?")){
        $(document.getElementById("model-addlead")).fadeOut(100);
        $(document.getElementById("modaldes")).fadeIn(300);
        $(document.getElementById("modalstart")).fadeIn(300);
        document.getElementById("modalcontent").innerHTML = "";
        $(document.getElementById("modalcontent")).fadeOut(0);

    }
    else{

    }
}