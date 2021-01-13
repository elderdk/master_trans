function update_search_result(source_html, target_html) {
    const search_result_source_span = document.querySelector('#search_result_source')
    const search_result_target_span = document.querySelector('#search_result_target')
    search_result_source_span.innerHTML = source_html
    search_result_target_span.innerHTML = target_html
  }


function retrieve_match(search_url, seg_id) {

    var xhr = new XMLHttpRequest();
  
    xhr.onreadystatechange = function() {
      if (xhr.readyState === 4) {
          source_text = xhr.response.split("$$$")[0]
          target_text = xhr.response.split("$$$")[1]
        update_search_result(source_text, target_text);
      }
    }
  
    xhr.open("GET", search_url, true);
    xhr.send(seg_id);
  }