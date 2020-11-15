function select_all_text(e){
    e.currentTarget.select()
}

function move_to_seg_num(dict){
    if("goto_seg" in dict){
        if(dict["goto_seg"].length != 0){
        window.onload = function(){
            seg_id = "seg-" + dict["goto_seg"]
            found = document.querySelector("#"+seg_id)
            found.scrollIntoView();
            found.parentNode.children[3].childNodes[1].focus()
            }
        }
    }
}

function goto_seg(e){
    if (e.keyCode == 13) {
        seg_num = e.currentTarget.value
        base_url = window.location.origin + window.location.pathname
        per_page = dict["paginate_by"]

        full_url = base_url + "?page=" + Math.ceil(seg_num/per_page) + "&paginate_by=" + per_page + "&goto_seg=" + seg_num
        
        // Access to full_url
        window.location.href = full_url

        // Focus on the goto_seg
        seg_id = "seg-" + seg_num

    }
}

function paginator_submit(e){
    if (e.keyCode == 13) {
        form = document.querySelector('#paginator-form');
        form.submit()
    }
}

function add_event(dict){
    paginator_inputs = document.querySelectorAll(".paginator-input")
    paginator_inputs.forEach(input => {
        input.addEventListener("keyup", paginator_submit, false)
    })
    paginator_inputs.forEach(input => {
        input.addEventListener("focus", select_all_text, false)
    })

    go_to_seg = document.querySelector("#goto-seg")
    go_to_seg.dict = dict
    go_to_seg.addEventListener("keyup", goto_seg, false)


}

function fill_in_paginators(){

    if(dict["paginate_by"] != undefined){
        paginate_by = document.querySelector("#seg_per_page")
        paginate_by.value = dict["paginate_by"]
    }
    
}

function get_param_dict(){
    dict = {}
    url_params = window.location.search.substring(1).split("&");
    
    url_params.forEach(param => {
        slice = param.split("=")
        param_key = slice[0]
        param_value = slice[1]
        dict[param_key] = param_value
    })

    return dict
}

dict = get_param_dict()
fill_in_paginators(dict)
add_event(dict)
move_to_seg_num(dict)