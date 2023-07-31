

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