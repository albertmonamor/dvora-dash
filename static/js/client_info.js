
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