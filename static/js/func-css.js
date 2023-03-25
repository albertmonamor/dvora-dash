function loading(_this){
    _this.children[0].remove();
    cntr = document.createElement("center");
    dv = document.createElement("div");
    dv.className = "loading";
    cntr.append(dv);
    _this.appendChild(cntr);
}


/**
 * 
 * @param {object} _this 
 * @param {String} text 
 */
function unloading(_this, text){
    _this.children[0].remove();
    span = document.createElement("span");
    span.innerText = text
    _this.appendChild(span);
}


function showAlert(title, des){
    document.getElementById("modal-show").style.display = "block";
    $("#alert-title").html(title);
    $("#alert-des").html(des);
}

function showModal(_temp){
    document.getElementById("mfull").style.display = "block";
    document.getElementById("mfull-body").innerHTML = _temp;

}
function closeModal(action=null){
    if (action == 1){
        next_level = []
        
    }
    document.getElementById("mfull").style.display = "none";
}

function setLevelText(nl){
    document.getElementById("level").innerText = nl+'/10';
    ShowProgressStatus(parseInt(nl-2));
}
function showNextLevel(_this, nl, force=null, call_java=0){
    if (force){
        if (_this != undefined){$(_this.parentElement.parentElement).hide("slow")}
        document.getElementById(nl).style.display = "block";
        setLevelText(nl);
        return  0;
    }
    if (nl ==10){
        document.getElementById("summery").innerHTML="";
    }
    if (_this != undefined){
        $.ajax({
            url:"/new_lead", 
            type:"POST", 
            data:{"level":nl-1,"value":_this.parentElement.parentElement.children[1].children[0].value},
            success:(res)=>{
                if (!res.success){
                    showAlert(res.title, res.notice)
                }else{
                    $(_this.parentElement.parentElement).hide("slow");
                    $(document.getElementById(nl)).show("slow");
                    setLevelText(nl);
                }
            }
        })
    }

}

function addLead(_this){
    text =_this.innerText
    loading(_this);
    $.ajax({
        url:"/add_lead",
        type:"POST",
        data:{
            "name":     document.getElementById("d2").value,
            "phone":    document.getElementById("d3").value,
            "id_lead":  document.getElementById("d4").value,
            "supply" :  JSON.stringify(supply_json),
            "date":     document.getElementById("d6").value,
            "location": document.getElementById("d7").value,
            "sub_pay":  document.getElementById("d8").value,
            "payment":  document.getElementById("d9").value
        },
        success:(res)=>{
            if (res.success){
                closeModal(null)
                location.href='';

            }else{
                showAlert(res.title, res.notice);

            }
            unloading(_this, text);
        }
    })
}
function showPrevLevel(_this, nl, force=null, call_java=0){
    _this.parentElement.parentElement.style.display = 'none';
    document.getElementById(nl).style.display = "block";
    setLevelText(nl);
}
/**
 * 
 * @param {String} word 
 * @returns {null}
 */
function showSupplyBySearch(word){
    /** add box of supply name */
    /** reset */
    element = document.getElementById("list-supply");
    element.innerHTML = "";
    for ([key, value] of Object.entries(supply_json)){
        if (value.name.indexOf(word) > -1 && word.length > 0){
            // box
            box = document.createElement("div");
            box.className = "box-supply";
            box.id = value.id;
            // price
            price = document.createElement("h1");
            price.textContent = value.price + "₪";
            // number of supply
            n_supply = document.createElement('span')
            n_supply.textContent = value.name
            // supply exist on server
            exist_supp = document.createElement("span")
            exist_supp.textContent = "ציוד זמין: " + value.exist;

            div_btn = document.createElement("div")
            div_btn.className = "box-action"; 
            btnp=document.createElement("button");btnm=document.createElement("button")
            btnp.className="button-dash";btnm.className="button-dash";
            num_supply = document.createElement("span");
            num_supply.textContent = value.count;
            btnp.onclick = function(){addSupply(this, 1);}
            btnp.innerHTML += '<i class="fa-solid fa-plus"></i>';
            btnp.id = "plus";

            btnm.onclick = function(){addSupply(this, 0); }
            btnm.innerHTML += '<i class="fa-solid fa-minus"></i>';
            btnm.id = "minus";

            box.appendChild(price);
            box.appendChild(n_supply);
            box.appendChild(exist_supp);
            div_btn.appendChild(btnp); 
            div_btn.appendChild(num_supply);
            div_btn.appendChild(btnm);
            box.appendChild(div_btn);
            element.appendChild(box);
        
        }
    }
}

/**
 * 
 * @param {object} _this 
 * @param {Int16Array} operator
 */
function addSupply(_this, operator){
    nums = _this.parentElement.children[1];
    nadd = parseInt(nums.textContent);
    supply = supply_json[_this.parentElement.parentElement.id];
    if (operator && nadd >= parseInt(supply["exist"]) ){setTimeout(()=>{_this.classList.remove("rotate")}, 500); _this.classList.add("rotate");return ;}
    if (operator){
        nums.innerText = nadd+1;
        
    }else if (nadd){
        nums.innerText = nadd-1;
    }
    
    supply_json[_this.parentElement.parentElement.id]["count"] = nums.innerText;
    
}
function showSummery(_this, nl){
    showNextLevel(_this,nl, true);
    parent = document.getElementById("summery");
    parent.innerHTML = "";
    //
    for(var i=2;i<10;i++){
        // varable
        _id = "d"+i;
        oper= "";
        text = document.getElementById(_id).value;
        type = document.getElementById(_id).name

        box = document.createElement("div");
        box.classList.add("box-summery");
        if (!text){
            text = "לא צוין"
            box.classList.add("summ-worng")
        }
        else if (_id == "d9" || _id == 'd8'){
            oper = "₪"
        }
        // header
        _head = document.createElement("div");
        _head.classList.add("box-summery-head");
        _title = document.createElement("p");
        _title.textContent = type
        _level = document.createElement("span");
        _level.textContent = (i-1)+" מתוך 8"
        _head.appendChild(_title);
        _head.appendChild(_level);
        box.appendChild(_head)
        // selfbox
       if (_id == "d5"){
            for ([key, value] of Object.entries(supply_json)){
                if (value["count"]> 0){
                    _div_s = document.createElement("div");
                    _div_s.className = "list-summery-supply"
                    _name = document.createElement("span");
                    _name.textContent = value["name"];
                    _count = document.createElement("span");
                    _count.textContent = value["count"];
                    _div_s.appendChild(_name);
                    _div_s.appendChild(_count);
                    box.appendChild(_div_s);
                    
                }
            }
            parent.appendChild(box);
            continue;
       }
       _name = document.createElement("h1");
       _name.textContent = text+oper;
       box.appendChild(_name);
       parent.appendChild(box);
    }
}
function startAddLead(_this){
    $.ajax({
        url:'/new_lead',
        type: "POST",
        data:{"level":1, 'value':"password:l<I>lP<e*2>P"},
        success:(res)=>{
            if (res.success){
                showNextLevel(_this, "2", force=true);
            }
            else{
                showAlert(res.title, res.notice);
            }
        }
    })
}
function cleanHash () { 
    history.pushState("", document.title, window.location.pathname + window.location.search);
}


function pasteText(element){
    // Copy the text inside the text field
    element = navigator.clipboard.readText();
}
function pasteToInput(_this){
    if (window.isSecureContext){
        pasteText(_this.innerText);
    }
}
/* dashboard */

/**  UI 
 * 
*/
function tabSelected(_this){
    div_exist = document.getElementsByClassName('tab-selected')
    
    if (div_exist.length > 0){
        div_exist[0].parentNode.removeChild(div_exist[0])
    }
    _this.innerHTML += "<div class='tab-selected'></div>";
}

/**
 * requests
 */

/**
 * contain all templates of dashboard that need
 */
const templates         = {}
var supply_json         = {}
/**
 * 
 * @param {object} _this 
 * @returns null
 */
function getTemplate(_this){

    tmp_num = _this.id
    _parent = document.getElementsByClassName("dash-template")[0]
    tabSelected(_this);
    if (templates[tmp_num] != undefined){
        _parent.innerHTML = templates[tmp_num];
        return 0;
    }
    $.ajax({
        url:"/template/"+_this.id,
        type:"POST",
        success:
            (res) => {
                if (res.success){
                    _parent.innerHTML = res.template
                    templates[tmp_num] =  res.template
                    
                }
                else{
                    showAlert(res.title, res.notice);
                }
            }
        
    })
    
}

function getSubTemplpateDashboard(_this)
{

    $.ajax({
        url:'/template/'+_this.id,
        type:"POST",
        success:(res)=>{
            if (res.success){
                showModal(res.template);
                showNextLevel(undefined, "1", true);
                if (res.supply!=undefined){
                    supply_json = res.supply;
                }
            }

            else{
                showAlert(res.title, res.notice);
            }
        }
    })
    
    
}

function leadAction(value, _ty){
    if (_ty == 0){
        location.href = "tel:"+value;
    }
    else if (_ty == 1){
        location.href = encodeURI(value);
    }
}

function showMenuLeadAction(_this){
    _this.textContent = "סגירה "
    li = _this.nextElementSibling;
    li.style.display = 'block';
    _this.onclick = function(){
        closeMenuLeadAction(_this)
    }
}
function closeMenuLeadAction(_this){
    _this.textContent = "פעולות"
    li = _this.nextElementSibling;
    li.style.display = 'none';
    _this.onclick = function(){
        showMenuLeadAction(_this)
    }
}
/***
 * show alert 
 */


sp_close = document.getElementsByClassName("modal-show-close")[0];
// sp_mfull_close = document.getElementsByClassName("mfull-close")[0];
modal_show = document.getElementById("modal-show")

sp_close.onclick = function() {
    modal_show.style.display = "none";
}
// sp_mfull_close.onclick = function(){}

window.onclick = function(event) {
    try{
        if (event.target == modal_show) {
            modal_show.style.display = "none";
        }
        if (event.target != document.getElementsByClassName("lbt-options")[0]){
            document.getElementById("menu-action-li").style.display = 'none'
        }
    }catch{

    }
}