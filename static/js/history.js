

function showSearchHistory(_this){
    element = document.getElementById("searchleads");
    button = document.getElementById("opensearch");
    $(element).show(300);
    $(element).css("display", "flex");
    // replace call
    button.onclick = ()=>{hideSearchHistory(_this);};
    search_is_open.history = 1;
} 

function hideSearchHistory(_this){
    element = document.getElementById("searchleads");
    button = document.getElementById("opensearch");
    $(element).hide(300);
    button.onclick = ()=>{showSearchHistory(_this);};
    getTemplate($("#2")[0], "2", 1);
    search_is_open.history = 0;
}

function filter_event(t){
    show_loading_screen()
    action = t.role;
    id_btn = t.id
    $.ajax({
        url:"/filter",
        type:"post", 
        data:{"type_filter":action, "tmp":2},
        success:(res)=>{
            if (res.success){
                templates[2].tmp = res.template;
                document.getElementsByClassName("dashboard-template")[0].innerHTML = res.template;
                elem = document.getElementsByClassName("bfselcted")[0]
                if (elem != undefined){
                    elem.classList.remove("bfselcted");
                }
                document.getElementById(id_btn).classList.add("bfselcted")
            }
            else{
                show_popup_error(res, null);
            }
            close_loading_screen();
        }
    })
}